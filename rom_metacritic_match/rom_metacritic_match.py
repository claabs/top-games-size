import dataclasses
import json
from typing import List

from common.metacritic import get_all_game_ratings, get_all_game_slugs_metacritic
from rom_metacritic_match.metacritic_db import MetacriticDatabase
from top_games_size.platform import Platform


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


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
    with open("output/all_game_ratings.json", "w") as file:
        json.dump(all_game_ratings, file, cls=EnhancedJSONEncoder)
    db.close()
