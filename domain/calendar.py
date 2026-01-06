from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

WARSAW = ZoneInfo("Europe/Warsaw")
TZID = "Europe/Warsaw"


def build_ics_icalendar(rows, cal_name: str = "Plan zajęć") -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//plan.chojnacki.dev//USOS Plan//PL")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    cal.add("x-wr-calname", cal_name)
    cal.add("x-wr-timezone", TZID)
    cal.add("x-published-ttl", "PT1H")

    now_utc = datetime.now(timezone.utc)

    for r in rows:
        ev = Event()

        ev.add("uid", r["activity_uid"])
        ev.add("dtstamp", now_utc)

        dtstart = _iso_to_dt(r["start_time"])
        dtend = _iso_to_dt(r["end_time"])

        ev.add("dtstart", _to_warsaw_naive(dtstart), parameters={"TZID": TZID})
        ev.add("dtend", _to_warsaw_naive(dtend), parameters={"TZID": TZID})

        summary = f"{r['course_name']} ({r['type_name']})"
        ev.add("summary", summary)

        room = r["room_name"] or ""
        if room:
            ev.add("location", room)

        ev.add("sequence", int(r["sequence"]))

        if int(r["cancelled"]) == 1:
            ev.add("status", "CANCELLED")

        cal.add_component(ev)

    return cal.to_ical()


def _iso_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _to_warsaw_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=WARSAW)
    else:
        dt = dt.astimezone(WARSAW)
    return dt.replace(tzinfo=None)
