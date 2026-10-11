import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import timedelta, time
from models.event import Event, TimeInterval
from repository.calendar_repository import CalendarRepository
from services.calendar_service import CalendarService
from services.exceptions import EventConflictError, InvalidTimeRangeError
from unittest.mock import MagicMock

def test_find_available_slots_basic():
    repo = MagicMock(spec=CalendarRepository)
    repo.get_all_events.return_value = [
        Event("Alice", "Meeting", time(9, 0), time(10, 0))
    ]
    service = CalendarService(repo)
    slots = service.find_available_slots(["Alice"], timedelta(minutes=60))
    assert len(slots) > 0

def test_empty_calendar():
    repo = MagicMock(spec=CalendarRepository)
    repo.get_all_events.return_value = []
    service = CalendarService(repo)
    slots = service.find_available_slots(["Alice"], timedelta(hours=1))
    assert len(slots) == 1

def test_person_with_no_events():
    repo = MagicMock(spec=CalendarRepository)
    repo.get_all_events.return_value = [
        Event("Bob", "Meeting", time(9, 0), time(10, 0))
    ]
    service = CalendarService(repo)
    slots = service.find_available_slots(["Alice"], timedelta(hours=1))
    assert len(slots) == 1

def test_full_day_busy():
    repo = MagicMock(spec=CalendarRepository)
    repo.get_all_events.return_value = [
        Event("Alice", "All Day", time(7, 0), time(19, 0))
    ]
    service = CalendarService(repo)
    slots = service.find_available_slots(["Alice"], timedelta(hours=1))
    assert len(slots) == 0

def test_has_conflict():
    repo = MagicMock(spec=CalendarRepository)
    repo.get_all_events.return_value = [
        Event("Alice", "Meeting", time(10, 0), time(11, 0))
    ]
    service = CalendarService(repo)
    conflict_event = Event("Alice", "Overlap", time(10, 30), time(11, 30))
    assert service.has_conflict(conflict_event) is True

def test_add_event_safely_invalid_range():
    repo = MagicMock(spec=CalendarRepository)
    service = CalendarService(repo)
    invalid_event = Event("Alice", "Bad", time(11, 0), time(10, 0))
    try:
        service.add_event_safely(invalid_event)
        assert False
    except InvalidTimeRangeError:
        assert True