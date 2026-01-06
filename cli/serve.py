import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from adapters.cfg_to_ics import convert_cfg_directory
from adapters.database_update import database_setup, generate_data_to_fetch, database_update
from adapters.path_resolvers import db_path

url = "https://api.usos.tu.kielce.pl/services/tt/classgroup_dates2"


def _setup_and_update_database(conn: sqlite3.Connection):
    data = generate_data_to_fetch()
    database_setup(conn)
    database_update(conn, data, url)
    convert_cfg_directory(conn)


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    _setup_and_update_database(conn)
    app.state.db = conn
    try:
        yield
    finally:
        conn.close()


app = FastAPI(lifespan=lifespan)


@app.get("/{name}.ics")
def get_ics(name: str):
    if not name or not all(c.isalnum() or c in ("-", "_") for c in name):
        raise HTTPException(400, "Invalid calendar name")

    row = app.state.db.execute(
        "SELECT content FROM calendars WHERE key = ?",
        (name.lower(),),
    ).fetchone()

    if not row:
        raise HTTPException(404, "Calendar not found")

    ics_bytes: bytes = row["content"]
    return Response(
        content=ics_bytes,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{name}.ics"'},
    )
