PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS types (
    type_id INTEGER PRIMARY KEY,
    type_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY,
    room_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS activities (
    activity_uid TEXT PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    group_number INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    cancelled INTEGER NOT NULL DEFAULT 0,
    last_seen_at TEXT NOT NULL,
    dtstamp TEXT NOT NULL,
    sequence INTEGER NOT NULL DEFAULT 0,
    course INTEGER NOT NULL,
    type INTEGER NOT NULL,
    room INTEGER NOT NULL,
    FOREIGN KEY (course) REFERENCES courses (course_id),
    FOREIGN KEY (type) REFERENCES types (type_id),
    FOREIGN KEY (room) REFERENCES rooms (room_id)
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    error TEXT
);

CREATE TABLE IF NOT EXISTS calendars (
    key TEXT PRIMARY KEY,
    content BLOB NOT NULL,
    updated_at INTEGER NOT NULL
);
