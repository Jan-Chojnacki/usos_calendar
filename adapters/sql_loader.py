from pathlib import Path


def _sql_dir() -> Path:
    return Path(__file__).resolve().parent.parent.joinpath("sql")


def load_sql(name: str) -> str:
    path = _sql_dir().joinpath(name)
    return path.read_text(encoding="utf-8")
