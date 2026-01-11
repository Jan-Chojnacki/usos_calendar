import sqlite3
import time
from typing import Any, Final

import requests

from adapters.acrivity_normalizer import utc_now_iso, normalize_raw, ActivityNorm
from adapters.config_files import iter_class_configs, unique_class_pairs
from adapters.path_resolvers import cfg_path
from adapters.sql_loader import load_sql

SQL_UPSERT_ACTIVITY: Final[str] = load_sql("upsert_activity.sql")
SQL_CANCEL_ACTIVITY: Final[str] = load_sql("cancel_activity.sql")
SQL_UPSERT_COURSES: Final[str] = load_sql("upsert_courses.sql")
SQL_UPSERT_ROOMS: Final[str] = load_sql("upsert_rooms.sql")
SQL_UPSERT_TYPES: Final[str] = load_sql("upsert_types.sql")
SQL_SELECT_OLD_ACTIVITY: Final[str] = load_sql("select_old_activity.sql")
SQL_INSERT_SYNC_RUN: Final[str] = load_sql("insert_sync_run.sql")
SQL_UPDATE_SYNC_RUN_OK: Final[str] = load_sql("update_sync_run_ok.sql")
SQL_UPDATE_SYNC_RUN_ERROR: Final[str] = load_sql("update_sync_run_error.sql")
SQL_SCHEMA: Final[str] = load_sql("schema.sql")


class RPSLimiter:
    def __init__(self, rps: float):
        if rps <= 0:
            raise ValueError("rps must be > 0")
        self._interval = 1.0 / rps
        self._next_allowed = time.monotonic()

    def wait(self) -> None:
        now = time.monotonic()
        if now < self._next_allowed:
            time.sleep(self._next_allowed - now)
            now = time.monotonic()
        self._next_allowed = max(self._next_allowed, now) + self._interval


def database_setup(conn: sqlite3.Connection):
    with conn:
        conn.executescript(SQL_SCHEMA)


def generate_data_to_fetch() -> list[tuple[int, int]]:
    base_dir = cfg_path()
    configs = iter_class_configs(base_dir)
    return unique_class_pairs(configs)


def database_update(conn: sqlite3.Connection, data: list[tuple[int, int]], url: str):
    now = utc_now_iso()
    cur = conn.cursor()

    cur.execute(SQL_INSERT_SYNC_RUN, (now,))
    sync_id = cur.lastrowid

    limiter = RPSLimiter(rps=10)

    try:
        with requests.Session() as session:
            for unit_id, group_number in data:
                limiter.wait()
                raws = _fetch_unit_group(session, url, unit_id, group_number)

                for raw in raws:
                    a = normalize_raw(unit_id, group_number, raw)
                    _upsert_activity_row(cur, a, now)

                cur.execute(SQL_CANCEL_ACTIVITY, (now, unit_id, group_number, now))

        cur.execute(SQL_UPDATE_SYNC_RUN_OK, (utc_now_iso(), sync_id))
        conn.commit()

    except Exception as e:
        conn.rollback()
        cur.execute(SQL_UPDATE_SYNC_RUN_ERROR, (repr(e), utc_now_iso(), sync_id))
        conn.commit()
        raise

    finally:
        cur.close()


def _compute_seq_dtstamp(
        now: str,
        old: sqlite3.Row | None,
        start_iso: str,
        end_iso: str,
        course_id: int,
        type_id: int,
        room_id: int,
) -> tuple[int, str]:
    if not old:
        return 0, now

    old_start, old_end, old_course, old_type, old_room, old_cancelled, old_seq, old_dt_stamp = old
    changed = (
            old_start != start_iso or
            old_end != end_iso or
            old_course != course_id or
            old_type != type_id or
            old_room != room_id or
            old_cancelled != 0
    )
    new_seq = old_seq + (1 if changed else 0)
    dtstamp = now if new_seq > old_seq else old_dt_stamp
    return new_seq, dtstamp


def _upsert_dims(cur: sqlite3.Cursor, a: ActivityNorm) -> tuple[int, int, int]:
    course_id = cur.execute(SQL_UPSERT_COURSES, (a.course_name,)).fetchone()[0]
    type_id = cur.execute(SQL_UPSERT_TYPES, (a.type_name,)).fetchone()[0]
    room_id = cur.execute(SQL_UPSERT_ROOMS, (a.room_name,)).fetchone()[0]
    return course_id, type_id, room_id


def _upsert_activity_row(cur: sqlite3.Cursor, a: ActivityNorm, now: str) -> None:
    course_id, type_id, room_id = _upsert_dims(cur, a)

    old = cur.execute(SQL_SELECT_OLD_ACTIVITY, (a.uid,)).fetchone()
    seq, dtstamp = _compute_seq_dtstamp(now, old, a.start_iso, a.end_iso, course_id, type_id, room_id)

    row = (
        a.uid, a.unit_id, a.group_number,
        a.start_iso, a.end_iso,
        course_id, type_id, room_id,
        now, dtstamp, seq
    )
    cur.execute(SQL_UPSERT_ACTIVITY, row)


def _fetch_unit_group(session: requests.Session, url: str, unit_id: int, group_number: int) -> list[dict[str, Any]]:
    params = {
        "unit_id": unit_id,
        "group_number": group_number,
        "fields": "start_time|end_time|name|room_number|course_name",
    }
    r = session.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json() or []
