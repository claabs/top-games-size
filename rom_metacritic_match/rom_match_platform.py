from dataclasses import dataclass
from typing import List


@dataclass
class RomMatchPlatform:
    rdb_names: List[str]
    platform_slug: str
    metacritic_id: int
