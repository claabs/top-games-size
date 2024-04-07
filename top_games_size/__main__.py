from top_games_size.get_top_sizes import get_top_sizes
from top_games_size.platform import Platform

IGDB_MIN_RATINGS = 4
TOP_N_GAMES = 200
MINIMUM_RATING = 75
CRITIC_SCORE = True  # False for user score
USE_METACRITIC = True  # False for IGDB

platforms = [
    Platform("Sony - PlayStation", 7, 1500000078),
    Platform("Sony - PlayStation 2", 8, 1500000094),
    Platform("Sony - PlayStation Portable", 38, 1500000109),
    Platform("Nintendo - GameCube", 21, 1500000099),
    Platform("Nintendo - Wii", 5, 1500000114),
    Platform("Sega - Saturn", 32, None),
    Platform("Sega - Dreamcast", 23, 1500000067),
    Platform("Microsoft - Xbox", 11, 1500000098),
    Platform("Microsoft - Xbox 360", 12, 1500000111),
]

if __name__ == "__main__":
    get_top_sizes(
        platforms,
        limit=TOP_N_GAMES,
        min_ratings=IGDB_MIN_RATINGS,
        use_critic_ratings=CRITIC_SCORE,
        use_metacritic=USE_METACRITIC,
        min_rating=MINIMUM_RATING,
    )
