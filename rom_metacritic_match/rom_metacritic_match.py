import bisect
import json
import re
from functools import lru_cache
from typing import List

from rapidfuzz import fuzz, process

from common.metacritic import get_all_game_ratings, get_all_game_slugs_metacritic
from common.parse_rdb import RdbEntry, parse_rdb
from rom_metacritic_match.metacritic_db import MetacriticDatabase
from rom_metacritic_match.rom_match_platform import RomMatchPlatform
from top_games_size.platform import Platform


def scrape_metacritic_games(platforms: List[Platform]):
    game_slugs = get_all_game_slugs_metacritic(platforms)
    with open("output/game_slugs.json", "w") as file:
        json.dump(game_slugs, file)


def scrape_scores():
    with open("output/game_slugs.json", "r") as file:
        game_slugs = json.load(file)

    all_game_ratings = []
    count = 0
    db = MetacriticDatabase()

    for game_slug in game_slugs:
        if count % 10 == 0:
            print(f"Fetching scores for game {count}")
        try:
            # if db.game_exists(game_slug):
            #     continue
            game_rating = get_all_game_ratings(game_slug)
            all_game_ratings.append(game_rating)
            db.insert_game(
                game_rating.game_slug,
                game_rating.title,
                game_rating.overall_score.user_score.score,
                game_rating.overall_score.user_score.review_count,
                game_rating.overall_score.critic_score.score,
                game_rating.overall_score.critic_score.review_count,
                game_rating.developer,
                game_rating.publisher,
            )
            for platform in game_rating.platform_scores:
                db.insert_platform_game(
                    platform.platform_slug,
                    game_rating.game_slug,
                    platform.user_score.score,
                    platform.user_score.review_count,
                    platform.critic_score.score,
                    platform.critic_score.review_count,
                )
            db.commit()
        except Exception as e:
            print(e)
            with open("output/failed_game_slugs.txt", "a") as file:
                file.write(game_slug + "\n")
        count += 1
    db.close()


@lru_cache(maxsize=None)
def clean_name(rom_name: str) -> str:
    # Remove parenthesis groups
    clean_name = re.sub(r"\([^()]*\)", "", rom_name)
    # Remove file extension
    clean_name = re.sub(r"\.[^.]+$", "", clean_name)
    clean_name = clean_name.strip()

    words = clean_name.split()
    if words[-1] in {"The", "A", "An"}:
        # Move the article to the beginning of the title
        reordered_name = f"{words[-1]} {' '.join(words[:-1])}"
        reordered_name = reordered_name.rstrip(",")
    else:
        # Title doesn't end with an article, keep it unchanged
        reordered_name = clean_name

    return reordered_name


@lru_cache(maxsize=None)
def scorer(query, choice, **kwargs):
    return fuzz.ratio(query, clean_name(choice), **kwargs)


def refine_results(
    results: list[tuple[str, float, int]], rdb_games: list[RdbEntry]
) -> list[tuple[str, float, int]]:
    highest_score = results[0][1]
    highest_score_results = []

    # Iterate through the list and collect tuples with the highest score
    for result in results:
        if result[1] == highest_score:
            highest_score_results.append(result)
        else:
            # Since the list is sorted, once we find a score lower than the highest score, we can stop
            break
    # Apply bonus scores to best matches to break ties
    sorted_results = []
    for result in highest_score_results:
        match_str, score, index = result
        rom_name = rdb_games[index].rom_name
        bonus = 0
        if "(Demo" in rom_name:
            bonus += -50
        if "(Bonus Disc" in rom_name:
            bonus += -25
        if "(Preview Disc" in rom_name:
            bonus += -25
        if "(USA" in rom_name:
            bonus += 20
        if "(Japan" in rom_name:
            bonus += 10

        disc_match = re.search(r"\(Disc (\d+)\)", rom_name)
        if disc_match:
            disc_number = int(disc_match.group(1))
            bonus += disc_number * 5  # Adjust bonus proportionally to the disc number

        rev_match = re.search(r"\(Rev (\d+)\)", rom_name)
        if rev_match:
            rev_number = int(rev_match.group(1))
            bonus += rev_number * 5  # Adjust bonus proportionally to the rev number

        bisect.insort(
            sorted_results, (rom_name, score + bonus, index), key=lambda x: -1 * x[1]
        )

    return sorted_results


def find_all_discs_size(
    results: list[tuple[str, float, int]], rdb_games: list[RdbEntry]
) -> int:
    match_str, score, index = results[0]
    rdb_game = rdb_games[index]
    disc_match = re.search(r"\(Disc (\d+)\)", rdb_game.rom_name)
    if not disc_match:
        return rdb_game.size
    max_disc_number = int(disc_match.group(1))

    # Generate titles for each disc number
    total_size = rdb_game.size
    for disc_number in range(1, max_disc_number):
        disc_match = next((x for x in results if f"(Disc {disc_number})" in x[0]), None)
        if disc_match:
            match_str, score, index = disc_match
            total_size += rdb_games[index].size
    return total_size


def fast_title_match(
    metacritic_game: tuple[str, str, str, str, float],
    rdb_games: List[RdbEntry],
    min_score=60,
) -> tuple[str, int]:
    game_slug, meta_title, meta_developer, meta_publisher, score = metacritic_game

    rdb_titles = list(map(lambda x: x.rom_name, rdb_games))

    meta_title_clean = re.sub(r"\(\d{4}\)$", "", meta_title)
    meta_title_clean = re.sub(r"\(Remake\)$", "", meta_title_clean)
    results = process.extract(
        meta_title_clean, rdb_titles, score_cutoff=min_score, scorer=scorer, limit=None
    )
    if not (results and results[0]):
        return
    refined_results = refine_results(results, rdb_games)
    size = find_all_discs_size(refined_results, rdb_games)
    rom_name = refined_results[0][0]
    return rom_name, size


def match_metacritic_to_rom(
    metacritic_game: tuple[str, str, str, str, float],
    rdb_games: List[RdbEntry],
    weights=[1, 0.05, 0.05],
    min_avg_score=40,
) -> tuple[str, int] | None:
    print(metacritic_game)
    game_slug, meta_title, meta_developer, meta_publisher, score = metacritic_game

    matches = []
    for index, rdb_game in enumerate(rdb_games):
        title_result = fuzz.ratio(
            meta_title,
            rdb_game.clean_name,
        )
        developer_result = fuzz.ratio(
            meta_developer,
            rdb_game.developer,
        )
        publisher_result = fuzz.ratio(
            meta_publisher,
            rdb_game.publisher,
        )
        weighted_average = (
            title_result * weights[0]
            + developer_result * weights[1]
            + publisher_result * weights[2]
        ) / sum(weights)
        if weighted_average >= min_avg_score:
            match = {
                "score": weighted_average,
                "rdb_game": rdb_game,
                "title_result": title_result,
                "developer_result": developer_result,
                "publisher_result": publisher_result,
                "index": index,
            }
            bisect.insort(matches, match, key=lambda x: -1 * x["score"])

    if matches and matches[0]:
        rdb_game = rdb_games[matches[0]["index"]]
        return rdb_game.rom_name, rdb_game.size
