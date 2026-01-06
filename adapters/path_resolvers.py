import os
from pathlib import Path


def cfg_path() -> Path:
    override = os.environ.get("USOS_CFG_DIR")
    if override:
        d = Path(override).expanduser()
    else:
        d = Path(__file__).parent.parent.joinpath("cfgs").resolve()
    d.mkdir(parents=True, exist_ok=True)
    return d


def db_path() -> Path:
    override = os.environ.get("USOS_DB_PATH")
    if override:
        d = Path(override).expanduser()
    else:
        d = Path(__file__).parent.parent.joinpath("plan.db3").resolve()
    return d
