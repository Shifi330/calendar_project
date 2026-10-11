from dataclasses import dataclass
from datetime import time

@dataclass(frozen=True)
class Event:
    person_name: str
    subject: str
    start_time: time
    end_time: time

@dataclass(frozen=True)
class TimeInterval:
    start: time
    end: time