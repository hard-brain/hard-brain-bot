from collections import Counter


class ScoringService:
    def __init__(self):
        self.players = Counter()

    def get_scores(self) -> Counter:
        return self.players

    def add_points(self, username: str, points: int = 1):
        self.players[username] += points
