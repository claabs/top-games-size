class Platform:
    def __init__(self, name, igdb_id, metacritic_id, limit, filter_list=False):
        self.name = name
        self.igdb_id = igdb_id
        self.metacritic_id = metacritic_id
        self.limit = limit
        self.filter_list = filter_list
