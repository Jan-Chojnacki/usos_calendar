INSERT INTO types (type_name)
VALUES (?)
ON CONFLICT (type_name) DO UPDATE SET type_name = types.type_name
RETURNING type_id;
