from rom_metacritic_match.rom_match_platform import RomMatchPlatform
from rom_metacritic_match.rom_metacritic_match import (
    metacritic_matcher,
    scrape_metacritic_games,
    scrape_scores,
)

platforms = [
    RomMatchPlatform("Sony - PlayStation", "playstation", 1500000078),
    RomMatchPlatform("Sony - PlayStation 2", "playstation-2", 1500000094),
    RomMatchPlatform("Sony - PlayStation Portable", "psp", 1500000109),
    RomMatchPlatform("Sony - PlayStation Vita", "playstation-vita", 1500000117),
    RomMatchPlatform("Sony - PlayStation 3", "playstation-3", 1500000113),
    RomMatchPlatform("Nintendo - GBA", "game-boy-advance", 1500000091),
    RomMatchPlatform("Nintendo - DS", "ds", 1500000108),
    RomMatchPlatform("Nintendo - 3DS", "3ds", 1500000116),
    RomMatchPlatform("Nintendo 64", "nintendo-64", 1500000084),
    RomMatchPlatform("Nintendo - GameCube", "gamecube", 1500000099),
    RomMatchPlatform("Nintendo - Wii", "wii", 1500000114),
    RomMatchPlatform("Sega - Dreamcast", "dreamcast", 1500000067),
    RomMatchPlatform("Microsoft - Xbox", "xbox", 1500000098),
    RomMatchPlatform("Microsoft - Xbox 360", "xbox-360", 1500000111),
]

if __name__ == "__main__":
    # scrape_metacritic_games(platforms)
    # scrape_scores()
    metacritic_matcher(platforms[0])
