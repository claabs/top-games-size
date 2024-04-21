# Some matches are too difficult for fuzzy matching, so this manually maps the best ROM to the game
overrides: dict[dict[str]] = {
    "Nintendo - GameCube": {
        "Resident Evil (Remake)": "Resident Evil (USA) (Disc 2).iso",
    },
    "Nintendo - Wii": {
        "Resident Evil (Remake)": "Resident Evil Archives: Resident Evil (USA).iso",
        "The Godfather": "The Godfather: Blackhand Edition (USA).iso",
        "EA Sports Active 2": "EA Sports Active 2 - Personal Trainer (USA) (En,Fr,Es).iso",
        "Sam & Max: Save the World": "Sam & Max - Season One (USA) (En,Fr,Es).iso",
    },
    "Sega - Dreamcast": {
        "Virtua Tennis 2": "Tennis 2K2 (USA) (En,Ja,Fr,De,Es) (Rev A) (Track 3).bin",
        "The Last Blade 2": "Last Blade 2, The - Heart of the Samurai (USA) (Track 5).bin",
    },
    "Nintendo - Nintendo DS": {},
    "Sony - PlayStation 2": {},
}
