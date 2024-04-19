import csv
import os
from dataclasses import dataclass
from typing import Callable, List

import humanize

from common.parse_rdb import parse_rdb
from rom_metacritic_match.metacritic_db import MetacriticDatabase
from rom_metacritic_match.rom_match_platform import RomMatchPlatform
from rom_metacritic_match.rom_metacritic_match import (
    fast_title_match,
)


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
        rdb_games = parse_rdb(platform)
        for query_setting in queries:
            games = query_setting.func(platform.platform_slug)
            list_dir = os.path.join(
                "game_lists", query_setting.type, query_setting.setting
            )
            if not os.path.exists(list_dir):
                os.makedirs(list_dir)
            csv_writer = csv.writer(
                open(os.path.join(list_dir, f"{platform.rdb_names[0]}.csv"), "w")
            )
            csv_writer.writerow(
                [
                    "title",
                    "score",
                    "developer",
                    "publisher",
                    "rom_name",
                    "size",
                    "running_total",
                ]
            )
            running_size_total = 0
            for metacritic_game in games:
                game_slug, title, developer, publisher, score = metacritic_game
                human_size = None
                human_size_total = None
                match = fast_title_match(metacritic_game, rdb_games)
                rom_name, size = match if match else (None, None)
                if size:
                    running_size_total += size
                    human_size = humanize.naturalsize(size, binary=True)
                    human_size_total = humanize.naturalsize(
                        running_size_total, binary=True
                    )
                csv_writer.writerow(
                    [
                        title,
                        score,
                        developer,
                        publisher,
                        rom_name,
                        human_size,
                        human_size_total,
                    ]
                )
