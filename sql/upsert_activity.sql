INSERT INTO activities
(
    activity_uid, unit_id, group_number, start_time, end_time,
    course, type, room, cancelled, last_seen_at, dtstamp, sequence
)
VALUES
(?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
ON
CONFLICT (activity_uid)
DO
UPDATE SET
    unit_id = excluded.unit_id,
    group_number = excluded.group_number,
    start_time = excluded.start_time,
    end_time = excluded.end_time,
    course = excluded.course,
    type = excluded.type,
    room = excluded.room,
    cancelled = 0,
    last_seen_at = excluded.last_seen_at,
    dtstamp = excluded.dtstamp,
    sequence = excluded.sequence;
