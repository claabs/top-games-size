import bisect
import json
from typing import List

from rapidfuzz import fuzz

from common.metacritic import get_all_game_ratings, get_all_game_slugs_metacritic
from common.parse_rdb import parse_rdb
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


def metacritic_matcher(platform: RomMatchPlatform):
    db = MetacriticDatabase()
    rdb_games = parse_rdb(platform)
    metacritic_games = db.get_platform_games_critic_user(platform.platform_slug)
    weights = [1, 0.0, 0.0]
    min_avg_score = 40
    for metacritic_game in metacritic_games:
        print(metacritic_game)
        game_slug, meta_title, meta_developer, meta_publisher, best_score = (
            metacritic_game
        )
        matches = []
        for rdb_game in rdb_games:
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
                }
                bisect.insort(matches, match, key=lambda x: -1 * x["score"])

        if matches:
            # match_str, score, index = result
            print(matches[0])
