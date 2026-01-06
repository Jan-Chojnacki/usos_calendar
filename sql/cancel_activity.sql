UPDATE activities
SET cancelled = 1, dtstamp = ?, sequence = sequence + 1
WHERE
    unit_id = ? AND group_number = ?
    AND last_seen_at <> ?
    AND cancelled = 0
