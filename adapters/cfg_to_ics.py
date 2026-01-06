import sqlite3
import time
from typing import Final

from adapters.config_files import iter_class_configs
from adapters.path_resolvers import cfg_path
from adapters.sql_loader import load_sql
from domain.calendar import build_ics_icalendar

SQL_UPSERT_CALENDAR: Final[str] = load_sql("upsert_calendar.sql")


def convert_cfg_directory(conn: sqlite3.Connection):
    dir = cfg_path()
    cur = conn.cursor()

    for name, classes in iter_class_configs(dir):
        ics_bytes = _generate_ics(cur, classes, name)
        cur.execute(SQL_UPSERT_CALENDAR, (_safe_name(name), ics_bytes, int(time.time())))

    conn.commit()
    cur.close()


def _generate_ics(cur: sqlite3.Cursor, classes: list[tuple[int, int]], name: str) -> bytes:
    if not classes:
        raise ValueError("classes list is empty")

    where = " OR ".join(["(a.unit_id = ? AND a.group_number = ?)"] * len(classes))
    params: list[int] = []
    for unit_id, group_number in classes:
        params.extend([unit_id, group_number])

    cur.execute(f"""
        SELECT a.activity_uid, a.start_time, a.end_time, a.cancelled, a.sequence,
               c.course_name, t.type_name, r.room_name
        FROM activities a
        JOIN courses c ON c.course_id = a.course
        JOIN types   t ON t.type_id   = a.type
        JOIN rooms   r ON r.room_id   = a.room
        WHERE {where}
        ORDER BY a.start_time
    """, params)

    rows = cur.fetchall()

    ics_bytes = build_ics_icalendar(rows, cal_name=name)

    return ics_bytes


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name).strip("_")
