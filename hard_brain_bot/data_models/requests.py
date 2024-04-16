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
    similarity_threshold = 85  # todo: should we be able to configure this?

    def __post_init__(self) -> None:
        self.correct_answers = set(
            map(lambda s: s.lower(), (self.title, *self.alt_titles))
        )

    def is_correct_answer(self, answer: str) -> bool:
        # fast check if answer is in alt_titles
        if answer.lower() in self.correct_answers:
            return True

        # fuzzy match answer against correct answers
        normalized_answer = SongData._normalize_text(answer)
        for correct_answer in self.correct_answers:
            score = fuzz.token_sort_ratio(SongData._normalize_text(correct_answer), normalized_answer)
            if score >= self.similarity_threshold:
                return True
        return False

    @staticmethod
    def _normalize_text(text: str) -> str:
        return ''.join(e.lower() for e in text if e.isalnum())
