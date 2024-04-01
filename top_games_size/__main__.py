from top_games_size.get_top_sizes import get_top_sizes
from top_games_size.igdb import get_platforms
from top_games_size.platform import Platform

platforms = [
    Platform("Sony - PlayStation 2", 8),
    Platform("Sony - PlayStation", 7),
    Platform("Sony - PlayStation Portable", 38),
    Platform("Nintendo - Wii", 5),
    Platform("Nintendo - GameCube", 21),
    Platform("Sega - Saturn", 32),
    Platform("Sega - Dreamcast", 23),
    Platform("Microsoft - Xbox", 11),
    Platform("Microsoft - Xbox 360", 12),
]

if __name__ == "__main__":
    # get_platforms()
    get_top_sizes(platforms)
