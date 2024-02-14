from dataclasses import dataclass


@dataclass
class SongData:
    song_id: int
    filename: str
    title: str
    alt_titles: list[str]
    genre: str
    artist: str

    def __post_init__(self) -> None:
        self.correct_answers = set(map(lambda s: s.lower(), (self.title, *self.alt_titles)))

    def is_correct_answer(self, answer: str) -> bool:
        return answer.lower() in self.correct_answers  # todo: fuzzy matching answers goes here
