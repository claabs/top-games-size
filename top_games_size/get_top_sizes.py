import os

import humanize
from rapidfuzz import fuzz, process

from top_games_size.igdb import get_top_rated_games
from top_games_size.parse_redump_dat import parse_redump_xml

redump_dat_dir = "redump_datfiles"


def get_top_sizes(platforms):
    for platform in platforms:
        get_top_sizes_platform(platform)


def get_top_sizes_platform(platform):
    redump_games = parse_redump_xml(read_platform_dat(platform))
    igdb_games = get_top_rated_games(platform)

    top_redump_games = []
    redump_names = list(map(lambda x: x.name, redump_games))
    for igdb_game in igdb_games:
        matched_game, score, index = process.extractOne(
            igdb_game.name, redump_names, scorer=fuzz.WRatio
        )
        if matched_game:
            # print(score, igdb_game.name, matched_game, sep=" | ")
            top_redump_games.append(redump_games[index])
        else:
            print(f"FAILED TO MATCH: {igdb_game.name}")

    total_bytes = sum_redump_games(top_redump_games)
    human_size = humanize.naturalsize(total_bytes, binary=True)
    print(f"{platform.redump_name}: {human_size}")


def read_platform_dat(platform):
    # Get list of files in the directory
    files = os.listdir(redump_dat_dir)

    # Find the file that starts with the platform string
    matching_files = [
        file
        for file in files
        if file.startswith(platform.redump_name) and file.endswith(".dat")
    ]

    # Assuming only one matching file, read its contents
    if matching_files:
        file_path = os.path.join(redump_dat_dir, matching_files[0])
        with open(file_path, "r") as file:
            file_contents = file.read()
            return file_contents
    else:
        raise FileNotFoundError(
            f"No file found in {redump_dat_dir} matching the platform name: {platform.redump_name}"
        )


def sum_redump_games(redump_games):
    total_bytes = 0
    for redump_game in redump_games:
        biggest_rom = None
        for rom in redump_game.roms:
            if not biggest_rom or rom.size > biggest_rom.size:
                biggest_rom = rom
        total_bytes += biggest_rom.size
        # print(humanize.naturalsize(biggest_rom.size, binary=True), redump_game.name, sep=" | ")
    return total_bytes
