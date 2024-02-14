from dataclasses import dataclass
from thefuzz import fuzz


@dataclass
class SongData:
    song_id: int
    filename: str
    title: str
    alt_titles: list[str]
    genre: str
    artist: str

    def __post_init__(self) -> None:
        self.correct_answers = set(
            map(lambda s: s.lower(), (self.title, *self.alt_titles))
        )

    def is_correct_answer(self, answer: str) -> bool:
        # fast check if answer is in alt_titles
        if answer.lower() in self.correct_answers:
            return True

        # fuzzy match answer against correct answers
        similarity_threshold = 95
        for correct_answer in self.correct_answers:
            score = fuzz.partial_ratio(correct_answer, answer)
            if score >= similarity_threshold:
                return True
        return False
