import sqlite3

from adapters.cfg_to_ics import convert_cfg_directory
from adapters.database_update import generate_data_to_fetch, database_update, database_setup
from adapters.path_resolvers import db_path

url = "https://api.usos.tu.kielce.pl/services/tt/classgroup_dates2"


def main() -> None:
    data = generate_data_to_fetch()

    database_location = db_path()
    with sqlite3.connect(database_location) as conn:
        conn.row_factory = sqlite3.Row
        database_setup(conn)
        database_update(conn, data, url)
        convert_cfg_directory(conn)


if __name__ == "__main__":
    main()
