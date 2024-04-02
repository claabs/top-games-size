import os

import humanize
from rapidfuzz import fuzz, process

from top_games_size.igdb import get_top_rated_games
from top_games_size.metacritic import get_top_rated_games_metacritic
from top_games_size.parse_redump_dat import parse_redump_xml

redump_dat_dir = "redump_datfiles"


def get_top_sizes(platforms, **kwargs):
    lines = []
    grand_total_bytes = 0
    for platform in platforms:
        line, total_bytes = get_top_sizes_platform(platform, **kwargs)
        lines.append(line)
        grand_total_bytes += total_bytes
    print("===RESULTS===")
    print(*lines, sep="\n")
    print("-------------")
    print(f"GRAND TOTAL: {humanize.naturalsize(grand_total_bytes, binary=True)}")


def get_top_sizes_platform(platform, **kwargs):
    use_metacritic = kwargs.get("use_metacritic")
    print(f"Processing: {platform.redump_name}")
    redump_games = parse_redump_xml(read_platform_dat(platform))

    top_games = []
    if use_metacritic:
        if not platform.metacritic_id:
            return (f"{platform.redump_name}: None", 0)
        top_games = get_top_rated_games_metacritic(platform, **kwargs)
    else:
        top_games = get_top_rated_games(platform, **kwargs)

    top_redump_games = []
    redump_names = list(map(lambda x: x.name, redump_games))
    for top_game in top_games:
        result = process.extractOne(
            top_game, redump_names, scorer=fuzz.WRatio, score_cutoff=60
        )
        if result:
            matched_game, score, index = result
            # print(score, igdb_game.name, matched_game, sep=" | ")
            top_redump_games.append(redump_games[index])
        else:
            print(f"FAILED TO MATCH: {top_game}")

    if not os.path.exists("output"):
        os.makedirs("output")
    with open(f"output/{platform.redump_name}.txt", "w") as file:
        for string in sorted(top_games, key=sort_ignore_articles):
            file.write(string + "\n")

    total_bytes = sum_redump_games(top_redump_games)
    human_size = humanize.naturalsize(total_bytes, binary=True)
    return (
        f"{platform.redump_name}: {human_size} ({len(top_redump_games)} games)",
        total_bytes,
    )


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


def sort_ignore_articles(string):
    articles = ["a", "an", "the"]
    words = string.split()
    if words[0].lower() in articles:
        return " ".join(words[1:])
    return string
