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
    return clean_name


@lru_cache(maxsize=None)
def scorer(query, choice, **kwargs):
    bonus = 0
    if "(Demo" in choice:
        bonus += -50
    if "(USA)" in choice:
        bonus += 20
    if "(Japan)" in choice:
        bonus += 10

    return fuzz.ratio(query, clean_name(choice), **kwargs) + bonus


def fast_title_match(
    metacritic_game: tuple[str, str, str, str, float],
    rdb_games: List[RdbEntry],
    min_score=60,
) -> tuple[str, int]:
    game_slug, meta_title, meta_developer, meta_publisher, score = metacritic_game

    rdb_titles = list(map(lambda x: x.rom_name, rdb_games))

    meta_title_clean = re.sub(r"\(\d{4}\)$", "", meta_title)
    results = process.extract(
        meta_title_clean,
        rdb_titles,
        score_cutoff=min_score,
        scorer=scorer,
    )
    if not (results and results[0]):
        return
    match_str, score, index = results[0]
    rdb_game = rdb_games[index]
    return rdb_game.rom_name, rdb_game.size


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
