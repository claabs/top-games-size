import csv
import os
from dataclasses import dataclass
from typing import Callable, List

from rom_metacritic_match.metacritic_db import MetacriticDatabase
from rom_metacritic_match.rom_match_platform import RomMatchPlatform


@dataclass
class QuerySetting:
    type: str
    setting: str
    func: Callable


def list_top_games(platforms: List[RomMatchPlatform]):
    db = MetacriticDatabase()
    queries = [
        QuerySetting(
            "all",
            "best_critic_4_user_10",
            lambda platform: db.get_platform_games_critic_user(
                platform, min_critic_score=0, min_user_score=0
            ),
        ),
        QuerySetting(
            "all",
            "best_critic_4",
            lambda platform: db.get_platform_games_critic(platform, min_critic_score=0),
        ),
        QuerySetting(
            "platform_exclusives",
            "best_critic_4_user_10",
            lambda platform: db.get_platform_exclusive_games_critic_user(
                platform, min_critic_score=0, min_user_score=0
            ),
        ),
        QuerySetting(
            "platform_exclusives",
            "best_critic_4",
            lambda platform: db.get_platform_exclusive_games_critic(
                platform, min_critic_score=0
            ),
        ),
    ]

    for platform in platforms:
        for query_setting in queries:
            games = query_setting.func(platform.platform_slug)
            list_dir = os.path.join(
                "game_lists", query_setting.type, query_setting.setting
            )
            if not os.path.exists(list_dir):
                os.makedirs(list_dir)
            csv_writer = csv.writer(
                open(os.path.join(list_dir, f"{platform.rdb_name}.csv"), "w")
            )
            csv_writer.writerow(["title", "score", "developer", "publisher"])
            for game_slug, title, developer, publisher, score in games:
                csv_writer.writerow([title, score, developer, publisher])
