from dataclasses import dataclass

from disnake import Webhook, Thread

from hard_brain_bot.services.quiz_service import QuizService


@dataclass
class Game:
    quiz_service: QuizService
    message_receiver: Webhook | Thread
