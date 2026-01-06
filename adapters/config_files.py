from pathlib import Path
from typing import Iterable, Iterator


def _is_cfg_file(path: Path, ext: str) -> bool:
    return path.is_file() and path.suffix.lower() == ext.lower()


def parse_class_pairs(file_path: Path) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []

    with file_path.open("r") as file:
        for line in file:
            if not line.strip():
                continue

            a, b = line.strip().split(",")
            pairs.append((int(a), int(b)))

    return pairs


def iter_class_configs(directory: Path, ext: str = ".txt") -> Iterator[tuple[str, list[tuple[int, int]]]]:
    for file_path in directory.iterdir():
        if not _is_cfg_file(file_path, ext):
            continue

        name = file_path.stem
        yield name, parse_class_pairs(file_path)


def unique_class_pairs(configs: Iterable[tuple[str, list[tuple[int, int]]]]) -> list[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()

    for _, values in configs:
        pairs.update(values)

    return list(pairs)
