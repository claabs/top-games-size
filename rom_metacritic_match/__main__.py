from rom_metacritic_match.rom_metacritic_match import (
    scrape_metacritic_games,
    scrape_scores,
)
from top_games_size.platform import Platform

TOP_N_GAMES = 200
platforms = [
    Platform("Sony - PlayStation", 7, 1500000078, TOP_N_GAMES),
    Platform("Sony - PlayStation 2", 8, 1500000094, TOP_N_GAMES),
    Platform("Sony - PlayStation Portable", 38, 1500000109, TOP_N_GAMES),
    Platform("Sony - PlayStation Vita", None, 1500000117, TOP_N_GAMES),
    Platform("Sony - PlayStation 3", None, 1500000113, TOP_N_GAMES),
    Platform("Nintendo - GBA", None, 1500000091, TOP_N_GAMES),
    Platform("Nintendo - DS", None, 1500000108, TOP_N_GAMES),
    Platform("Nintendo - 3DS", None, 1500000116, TOP_N_GAMES),
    Platform("Nintendo 64", None, 1500000084, TOP_N_GAMES),
    Platform("Nintendo - GameCube", 21, 1500000099, TOP_N_GAMES),
    Platform("Nintendo - Wii", 5, 1500000114, TOP_N_GAMES),
    Platform("Sega - Dreamcast", 23, 1500000067, TOP_N_GAMES),
    Platform("Microsoft - Xbox", 11, 1500000098, TOP_N_GAMES),
    Platform("Microsoft - Xbox 360", 12, 1500000111, TOP_N_GAMES),
]

if __name__ == "__main__":
    # scrape_metacritic_games(platforms)
    scrape_scores()
