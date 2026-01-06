INSERT INTO calendars (key, content, updated_at)
VALUES (?, ?, ?)
ON CONFLICT (key) DO UPDATE SET
    content = excluded.content,
    updated_at = excluded.updated_at
