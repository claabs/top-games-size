class Platform:
    def __init__(self, name, igdb_id, metacritic_id, limit, exclusive_key=False):
        self.name = name
        self.igdb_id = igdb_id
        self.metacritic_id = metacritic_id
        self.limit = limit
        self.exclusive_key = exclusive_key
