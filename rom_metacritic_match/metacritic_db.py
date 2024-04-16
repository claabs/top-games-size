import sqlite3


class MetacriticDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("metacritic_games.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_slug TEXT PRIMARY KEY,
            user_score FLOAT,
            user_reviews INT,
            critic_score FLOAT,
            critic_reviews INT,
            developer TEXT,
            publisher TEXT
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_platforms (
            platform TEXT,
            game_slug TEXT,
            user_score FLOAT,
            user_reviews INT,
            critic_score FLOAT,
            critic_reviews INT,
            PRIMARY KEY (platform, game_slug),
            FOREIGN KEY (game_slug) REFERENCES games(game_slug)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_platform_roms (
            name TEXT,
            platform TEXT,
            game_slug TEXT,
            size INT,
            region TEXT,
            PRIMARY KEY (name, platform, game_slug),
            FOREIGN KEY (platform, game_slug) REFERENCES game_platforms(platform, game_slug),
            FOREIGN KEY (game_slug) REFERENCES games(game_slug)
        )
        """)
        self.conn.commit()

    def insert_game(
        self,
        game_slug,
        user_score,
        user_reviews,
        critic_score,
        critic_reviews,
        developer,
        publisher,
    ):
        self.cursor.execute(
            """
        INSERT OR REPLACE INTO games 
            (game_slug, user_score, user_reviews, critic_score, critic_reviews, developer, publisher)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                game_slug,
                user_score,
                user_reviews,
                critic_score,
                critic_reviews,
                developer,
                publisher,
            ),
        )

    def insert_platform_game(
        self,
        platform,
        game_slug,
        user_score,
        user_reviews,
        critic_score,
        critic_reviews,
    ):
        self.cursor.execute(
            """
        INSERT OR REPLACE INTO game_platforms 
            (platform, game_slug, user_score, user_reviews, critic_score, critic_reviews)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                platform,
                game_slug,
                user_score,
                user_reviews,
                critic_score,
                critic_reviews,
            ),
        )

    def insert_rom(self, name, platform, game_slug, size, region=None):
        self.cursor.execute(
            """
        INSERT OR REPLACE INTO game_platform_roms (name, platform, game_slug, size, region)
        VALUES (?, ?, ?, ?, ?)
        """,
            (name, platform, game_slug, size, region),
        )

    def game_exists(self, game_slug):
        self.cursor.execute(
            "SELECT game_slug FROM games WHERE game_slug = ?", (game_slug,)
        )
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
