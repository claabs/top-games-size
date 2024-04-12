import os

import humanize
from rapidfuzz import fuzz, process, utils

from top_games_size.igdb import get_top_rated_games
from top_games_size.metacritic import get_top_rated_games_metacritic
from top_games_size.parse_archive_org_xml import parse_archive_org_xml
from top_games_size.parse_redump_dat import parse_redump_xml

redump_dat_dir = "redump_datfiles"
archive_org_xml_dir = "archive_org_xml"


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
    print(f"Processing: {platform.name}")
    game_sizes = []
    platform_dat_filename = get_platform_dat(platform)
    archive_org_xml_filename = get_archive_org_xml(platform)
    if platform_dat_filename:
        game_sizes = parse_redump_xml(read_platform_dat(platform_dat_filename))
    elif archive_org_xml_filename:
        game_sizes = parse_archive_org_xml(
            read_archive_org_xml(archive_org_xml_filename)
        )
    else:
        raise FileNotFoundError(
            f"No file game size file matching the platform name: {platform.name}"
        )

    top_games = []
    if use_metacritic:
        if not platform.metacritic_id:
            return (f"{platform.name}: None", 0)
        top_games = get_top_rated_games_metacritic(platform, **kwargs)
    else:
        top_games = get_top_rated_games(platform, **kwargs)

    top_game_sizes = []
    game_size_names = list(map(lambda x: x.name, game_sizes))
    for top_game in top_games:
        result = process.extractOne(
            top_game,
            game_size_names,
            scorer=fuzz.WRatio,
            score_cutoff=60,
            processor=utils.default_process,
        )
        if result:
            matched_game, score, index = result
            # print(score, igdb_game.name, matched_game, sep=" | ")
            top_game_sizes.append(game_sizes[index])
        else:
            print(f"FAILED TO MATCH: {top_game}")

    if not os.path.exists("output"):
        os.makedirs("output")
    with open(f"output/{platform.name}.txt", "w") as file:
        for string in sorted(top_games, key=sort_ignore_articles):
            file.write(string + "\n")

    total_bytes = sum_redump_games(top_game_sizes)
    human_size = humanize.naturalsize(total_bytes, binary=True)
    return (
        f"{platform.name}: {human_size} ({len(top_game_sizes)} games)",
        total_bytes,
    )


def get_platform_dat(platform):
    files = os.listdir(redump_dat_dir)

    # Find the file that starts with the platform string
    matching_files = [
        file
        for file in files
        if file.startswith(platform.name) and file.endswith(".dat")
    ]
    return matching_files[0] if matching_files else None


def read_platform_dat(file_name):
    file_path = os.path.join(redump_dat_dir, file_name)
    with open(file_path, "r") as file:
        file_contents = file.read()
        return file_contents


def get_archive_org_xml(platform):
    files = os.listdir(archive_org_xml_dir)

    # Find the file that starts with the platform string
    matching_files = [
        file
        for file in files
        if file.startswith(platform.name) and file.endswith(".xml")
    ]
    return matching_files[0] if matching_files else None


def read_archive_org_xml(filename):
    file_path = os.path.join(archive_org_xml_dir, filename)
    with open(file_path, "r") as file:
        file_contents = file.read()
        return file_contents


def sum_redump_games(redump_games):
    total_bytes = 0
    for redump_game in redump_games:
        total_bytes += redump_game.size
        # print(humanize.naturalsize(biggest_rom.size, binary=True), redump_game.name, sep=" | ")
    return total_bytes


def sort_ignore_articles(string):
    articles = ["a", "an", "the"]
    words = string.split()
    if words[0].lower() in articles:
        return " ".join(words[1:])
    return string
