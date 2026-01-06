SELECT
    start_time,
    end_time,
    course,
    type,
    room,
    cancelled,
    sequence,
    dtstamp
FROM activities
WHERE activity_uid = ?
