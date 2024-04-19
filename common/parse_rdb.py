import contextlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import List

from rom_metacritic_match.rom_match_platform import RomMatchPlatform

rdb_dir = "rdb"


@dataclass
class RdbEntry:
    rom_name: str
    size: int
    region: str
    developer: str | None
    publisher: str | None
    clean_name: str


def read_rdb(filename) -> List[RdbEntry]:
    process = subprocess.run(
        ["./bin/libretrodb_tool", filename, "list"], capture_output=True
    )
    values: List[RdbEntry] = []
    for line in process.stdout.decode().split("\n"):
        line = line.replace("\\", "\\\\")
        with contextlib.suppress(json.decoder.JSONDecodeError):
            game = json.loads(line)

            # Some games do not have a name, we just discard them
            if "name" not in game or not game["name"]:
                continue
            # Discard any games with no size (no dump)
            if "size" not in game or not game["size"]:
                continue

            clean_name: str = game.get("rom_name")
            # Remove parenthesis groups
            clean_name = re.sub(r"\([^()]*\)", "", clean_name)
            # Remove file extension
            clean_name = re.sub(r"\.[^.]+$", "", clean_name)
            clean_name = clean_name.strip()

            values.append(
                RdbEntry(
                    game.get("rom_name"),
                    game.get("size"),
                    game.get("region"),
                    game.get("developer", None),
                    game.get("publisher", None),
                    clean_name,
                )
            )

    print(f"{len(values)} entries")
    return values


def get_rdb_filename(rdb_name: str):
    files = os.listdir(rdb_dir)

    # Find the file that starts with the platform string
    matching_files = [file for file in files if file == f"{rdb_name}.rdb"]
    return os.path.join(rdb_dir, matching_files[0]) if matching_files else None


def parse_rdb(platform: RomMatchPlatform) -> List[RdbEntry]:
    filenames = list(map(lambda x: get_rdb_filename(x), platform.rdb_names))
    rdb_entries: List[RdbEntry] = []
    for filename in filenames:
        rdb_entries.extend(read_rdb(filename))

    return rdb_entries
