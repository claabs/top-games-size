import contextlib
import json
import os
import subprocess

rdb_dir = "rdb"


def read_rdb(filename, system):
    process = subprocess.run(
        ["./bin/libretrodb_tool", filename, "list"], capture_output=True
    )
    values = []
    for line in process.stdout.decode().split("\n"):
        line = line.replace("\\", "\\\\")
        with contextlib.suppress(json.decoder.JSONDecodeError):
            game = json.loads(line)

            # Some games do not have a name, we just discard them
            if "name" not in game or not game["name"]:
                continue

            game["system"] = system
            values.append(
                tuple(
                    game.get(key, None)
                    for key in [
                        "name",
                        "rom_name",
                        "system",
                        "developer",
                        "serial",
                        "size",
                        "region",
                    ]
                )
            )

    print(f"{system}: {len(values)} entries")
    return values


def get_rdb_filename(platform):
    files = os.listdir(rdb_dir)

    # Find the file that starts with the platform string
    matching_files = [
        file
        for file in files
        if file.startswith(platform.name) and file.endswith(".rdb")
    ]
    return matching_files[0] if matching_files else None


def parse_rdb(platform):
    filename = get_rdb_filename(platform)
    return read_rdb(filename, platform.name)
