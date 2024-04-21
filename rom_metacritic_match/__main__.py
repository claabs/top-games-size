from rom_metacritic_match.generate_top_lists import list_top_games
from rom_metacritic_match.rom_match_platform import RomMatchPlatform

platforms = [
    RomMatchPlatform(["Sony - PlayStation"], "playstation", 1500000078),
    RomMatchPlatform(["Sony - PlayStation 2"], "playstation-2", 1500000094),
    RomMatchPlatform(
        ["Sony - PlayStation Portable", "Sony - PlayStation Portable (PSN)"],
        "psp",
        1500000109,
    ),
    RomMatchPlatform(["Sony - PlayStation Vita"], "playstation-vita", 1500000117),
    RomMatchPlatform(
        ["Sony - PlayStation 3", "Sony - PlayStation 3 (PSN)"],
        "playstation-3",
        1500000113,
    ),
    RomMatchPlatform(["Nintendo - Game Boy Advance"], "game-boy-advance", 1500000091),
    RomMatchPlatform(
        ["Nintendo - Nintendo DS", "Nintendo - Nintendo DSi"], "ds", 1500000108
    ),
    RomMatchPlatform(["Nintendo - Nintendo 3DS"], "3ds", 1500000116),
    RomMatchPlatform(
        ["Nintendo - Nintendo 64", "Nintendo - Nintendo 64DD"],
        "nintendo-64",
        1500000084,
    ),
    RomMatchPlatform(["Nintendo - GameCube"], "gamecube", 1500000099),
    RomMatchPlatform(["Nintendo - Wii", "Nintendo - Wii (Digital)"], "wii", 1500000114),
    RomMatchPlatform(["Sega - Dreamcast"], "dreamcast", 1500000067),
    RomMatchPlatform(["Microsoft - Xbox"], "xbox", 1500000098),
]

if __name__ == "__main__":
    # scrape_metacritic_games(platforms)
    # scrape_scores()
    list_top_games(platforms)
