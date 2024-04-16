from dataclasses import dataclass


@dataclass
class RomMatchPlatform:
    rdb_name: str
    platform_slug: str
    metacritic_id: int
