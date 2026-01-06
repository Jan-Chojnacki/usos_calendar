INSERT INTO courses (course_name)
VALUES (?)
ON CONFLICT (course_name) DO UPDATE SET course_name = courses.course_name
RETURNING course_id;
