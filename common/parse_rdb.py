import contextlib
import json
import os
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

            values.append(
                RdbEntry(
                    game.get("rom_name"),
                    game.get("size"),
                    game.get("region"),
                    game.get("developer", None),
                    game.get("publisher", None),
                )
            )

    print(f"{len(values)} entries")
    return values


def get_rdb_filename(platform: RomMatchPlatform):
    files = os.listdir(rdb_dir)

    # Find the file that starts with the platform string
    matching_files = [file for file in files if file == f"{platform.rdb_name}.rdb"]
    return os.path.join(rdb_dir, matching_files[0]) if matching_files else None


def parse_rdb(platform: RomMatchPlatform) -> List[RdbEntry]:
    filename = get_rdb_filename(platform)
    return read_rdb(filename)
