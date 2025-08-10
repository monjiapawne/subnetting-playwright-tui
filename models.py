from dataclasses import dataclass

@dataclass
class UIModel:
    timer: float
    question: str = ""
    score: str = ""
    num_of_questions: int = 1
    selected_answer: int = 1
    answer1_context: str | None = None
    answer2_context: str | None = None
    answer1: str = ""
    answer2: str = ""
