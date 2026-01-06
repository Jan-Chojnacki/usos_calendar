from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ActivityNorm:
    uid: str
    unit_id: int
    group_number: int
    start_iso: str
    end_iso: str
    course_name: str | None
    type_name: str | None
    room_name: str | None


def _generate_uid(unit_id: int, group_number: int, start_dt: datetime) -> str:
    return (
        f"{unit_id}:{group_number}:"
        f"{start_dt.year:04d}{start_dt.month:02d}{start_dt.day:02d}"
        f"{start_dt.hour:02d}{start_dt.minute:02d}"
        "@plan.chojnacki.dev"
    )


def normalize_raw(unit_id: int, group_number: int, raw: dict[str, Any]) -> ActivityNorm:
    course_name = (raw.get("course_name") or {}).get("pl")
    type_name = (raw.get("name") or {}).get("pl")
    start_dt = parse_dt(raw["start_time"])
    end_dt = parse_dt(raw["end_time"])
    room_name = raw.get("room_number")

    uid = _generate_uid(unit_id, group_number, start_dt)

    return ActivityNorm(
        uid=uid,
        unit_id=unit_id,
        group_number=group_number,
        start_iso=start_dt.isoformat(timespec="seconds"),
        end_iso=end_dt.isoformat(timespec="seconds"),
        course_name=course_name,
        type_name=type_name,
        room_name=room_name,
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Warsaw"))
