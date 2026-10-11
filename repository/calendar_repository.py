from typing import Protocol, List
from datetime import datetime
from models.event import Event
import csv
import os

class AbstractCalendarRepository(Protocol):
    """פרוטוקול המגדיר את ממשק ה-Repository עבור ניהול אירועי לוח השנה."""
    
    def get_all_events(self) -> List[Event]:
        ...

    def add_event(self, event: Event) -> None:
        ...

class CalendarRepository:
    """מימשק קונקרטי לעבודה מול קובץ CSV בהתאם לפרוטוקול."""
    
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)

    def get_all_events(self) -> List[Event]:
        events: List[Event] = []
        if not os.path.exists(self.file_path):
            return events
            
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    person_name: str = row[0].strip()
                    title: str = row[1].strip()
                    start_time = datetime.strptime(row[2].strip(), "%H:%M").time()
                    end_time = datetime.strptime(row[3].strip(), "%H:%M").time()
                    events.append(Event(person_name, title, start_time, end_time))
        return events

    def add_event(self, event: Event) -> None:
        with open(self.file_path, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                event.person_name,
                event.subject,
                event.start_time.strftime('%H:%M'),
                event.end_time.strftime('%H:%M')
            ])