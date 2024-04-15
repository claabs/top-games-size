import dataclasses
import json
from typing import List

from common.metacritic import get_all_game_ratings, get_all_game_slugs_metacritic
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
    for game_slug in game_slugs:
        if count % 10 == 0:
            print(f"Fetching scores for game {count}")
        all_game_ratings.append(get_all_game_ratings(game_slug))
        with open("output/all_game_ratings.json", "w") as file:
            json.dump(all_game_ratings, file, cls=EnhancedJSONEncoder)
        count += 1
