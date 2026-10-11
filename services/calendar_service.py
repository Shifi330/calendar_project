from datetime import time, timedelta
from models.event import Event, TimeInterval
from typing import List, Tuple
from functools import reduce
from services.exceptions import EventConflictError, InvalidTimeRangeError

WORK_START_TIME = time(7, 0)
WORK_END_TIME = time(19, 0)

class CalendarService:
    """מחלקת השירות המרכזית לניהול הלוגיקה העסקית של לוח השנה."""

    def __init__(self, repo) -> None:
        self.repo = repo

    def _merge_intervals_functional(self, intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        מיזוג טווחים ממוינים תוך שימוש בתכנות פונקציונלי (functools.reduce).
        """
        if not intervals:
            return []

        sorted_intervals = sorted(intervals)

        def reducer(acc: List[Tuple[int, int]], current: Tuple[int, int]) -> List[Tuple[int, int]]:
            if not acc:
                return [current]
            last_start, last_end = acc[-1]
            curr_start, curr_end = current

            if curr_start <= last_end:
                acc[-1] = (last_start, max(last_end, curr_end))
            else:
                acc.append(current)
            return acc

        return reduce(reducer, sorted_intervals, [])

    def find_available_slots(self, people: List[str], duration: timedelta) -> List[TimeInterval]:
        """
        מוצא את כל חלונות הזמן הפנויים המשותפים לרשימת האנשים הנתונה
        במסגרת שעות העבודה, בהינתן משך הזמן הנדרש לפגישה.
        """
        if not people or duration.total_seconds() <= 0:
            return []

        existing_events: List[Event] = self.repo.get_all_events()
        person_events: List[Event] = [e for e in existing_events if e.person_name in people]
        
        work_start: time = WORK_START_TIME
        work_end: time = WORK_END_TIME
        
        def time_to_minutes(t: time) -> int:
            return t.hour * 60 + t.minute

        def minutes_to_time(m: int) -> time:
            return time(m // 60, m % 60)

        busy_intervals: List[Tuple[int, int]] = [
            (time_to_minutes(e.start_time), time_to_minutes(e.end_time))
            for e in person_events
        ]
        
        # שימוש במיזוג פונקציונלי המבוסס על reduce
        merged_busy = self._merge_intervals_functional(busy_intervals)

        free_slots: List[TimeInterval] = []
        current_m: int = time_to_minutes(work_start)
        end_work_m: int = time_to_minutes(work_end)
        duration_m: int = int(duration.total_seconds() // 60)

        for b_start, b_end in merged_busy:
            if b_start > current_m:
                gap: int = b_start - current_m
                if gap >= duration_m:
                    free_slots.append(TimeInterval(minutes_to_time(current_m), minutes_to_time(b_start)))
            current_m = max(current_m, b_end)

        if current_m < end_work_m:
            gap = end_work_m - current_m
            if gap >= duration_m:
                free_slots.append(TimeInterval(minutes_to_time(current_m), minutes_to_time(end_work_m)))

        return free_slots

    def has_conflict(self, new_event: Event) -> bool:
        """בודק האם קיים אירוע מתנגש עבור אותו אדם בטווח השעות המבוקש."""
        existing_events: List[Event] = self.repo.get_all_events()
        for event in existing_events:
            if event.person_name == new_event.person_name:
                if not (new_event.end_time <= event.start_time or new_event.start_time >= event.end_time):
                    return True
        return False

    def add_event_safely(self, new_event: Event) -> None:
        """מוסיף אירוע חדש לבסיס הנתונים לאחר בדיקת תקינות טווח שעות והיעדר התנגשויות."""
        if new_event.end_time <= new_event.start_time:
            raise InvalidTimeRangeError("שעת הסיום חייבת להיות מאוחרת משעת ההתחלה.")
        
        if self.has_conflict(new_event):
            raise EventConflictError("קיים אירוע מתנגש בטווח השעות המבוקש!")
            
        self.repo.add_event(new_event)