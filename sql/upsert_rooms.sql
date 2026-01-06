INSERT INTO rooms (room_name)
VALUES (?)
ON CONFLICT (room_name) DO UPDATE SET room_name = rooms.room_name
RETURNING room_id;
