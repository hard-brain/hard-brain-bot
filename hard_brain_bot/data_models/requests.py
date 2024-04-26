from dataclasses import dataclass
from thefuzz import fuzz

from hard_brain_bot.utils.helpers import VersionHelper


@dataclass
class SongData:
    song_id: str
    filename: str
    title: str
    alt_titles: list[str]
    genre: str
    artist: str
    similarity_threshold = 85

    def __post_init__(self) -> None:
        alt_titles = list(filter(lambda a: len(a) != 0, self.alt_titles))
        correct_answers = set(map(lambda s: s.lower(), (self.title, *alt_titles)))
        self.correct_answers = correct_answers
        self.version = VersionHelper.get_game_version_from_song_id(self.song_id)

    def is_correct_answer(self, answer: str) -> bool:
        # fast check if answer is in alt_titles
        if answer.lower() in self.correct_answers:
            return True

        # fuzzy match answer against correct answers
        normalized_answer = SongData._normalize_text(answer)
        for correct_answer in self.correct_answers:
            score = fuzz.token_sort_ratio(SongData._normalize_text(correct_answer), normalized_answer)
            if len(correct_answer) > 0 and score >= self.similarity_threshold:
                return True
        return False

    @staticmethod
    def _normalize_text(text: str) -> str:
        return ''.join(e.lower() for e in text if e.isalnum())
