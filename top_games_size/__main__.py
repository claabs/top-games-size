from top_games_size.get_top_sizes import get_top_sizes
from top_games_size.platform import Platform

IGDB_MIN_RATINGS = 4
TOP_N_GAMES = 200
MINIMUM_RATING = 75
CRITIC_SCORE = True  # False for user score
USE_METACRITIC = True  # False for IGDB

platforms = [
    Platform("Sony - PlayStation", 7, 1500000078, TOP_N_GAMES),
    Platform("Sony - PlayStation 2", 8, 1500000094, TOP_N_GAMES),
    Platform("Sony - PlayStation Portable", 38, 1500000109, TOP_N_GAMES),
    Platform("Sony - PlayStation Vita", None, 1500000117, TOP_N_GAMES),
    Platform("Nintendo - GameCube", 21, 1500000099, TOP_N_GAMES),
    Platform("Nintendo - Wii", 5, 1500000114, TOP_N_GAMES),
    # Platform("Sega - Saturn", 32, None, TOP_N_GAMES),
    Platform("Sega - Dreamcast", 23, 1500000067, TOP_N_GAMES),
    Platform("Microsoft - Xbox", 11, 1500000098, 500, filter_list=True),
    # Platform("Microsoft - Xbox 360", 12, 1500000111, TOP_N_GAMES),
]

if __name__ == "__main__":
    get_top_sizes(
        platforms,
        min_ratings=IGDB_MIN_RATINGS,
        use_critic_ratings=CRITIC_SCORE,
        use_metacritic=USE_METACRITIC,
        min_rating=MINIMUM_RATING,
    )
