from typing import TypedDict

class CollegeState(TypedDict):
    question: str
    intent: str
    matched_entity: str
    source: str
    answer: str