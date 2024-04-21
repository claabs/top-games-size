# Some matches are too difficult for fuzzy matching, so this manually maps the best ROM to the game.
# The second parameter is size, which is only required for multi-disc overrides.
# It should be the sum of all disc sizes.
overrides: dict[dict[tuple[str, int | None]]] = {
    "Nintendo - GameCube": {
        "Resident Evil (Remake)": ("Resident Evil (USA) (Disc 2).iso", 2919956480),
    },
    "Nintendo - Wii": {
        "Resident Evil (Remake)": (
            "Resident Evil Archives - Resident Evil (USA).iso",
            None,
        ),
        "The Godfather": ("Godfather, The - Blackhand Edition (USA).iso", None),
        "EA Sports Active 2": (
            "EA Sports Active 2 - Personal Trainer (USA) (En,Fr,Es).iso",
            None,
        ),
        "Sam & Max: Save the World": (
            "Sam & Max - Season One (USA) (En,Fr,Es).iso",
            None,
        ),
    },
    "Sega - Dreamcast": {
        "Virtua Tennis 2": (
            "Tennis 2K2 (USA) (En,Ja,Fr,De,Es) (Rev A) (Track 3).bin",
            None,
        ),
        "The Last Blade 2": (
            "Last Blade 2, The - Heart of the Samurai (USA) (Track 5).bin",
            None,
        ),
    },
    "Nintendo - Nintendo DS": {},
    "Sony - PlayStation 2": {},
}
