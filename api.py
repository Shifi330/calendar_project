from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import time, timedelta
from repository.calendar_repository import CalendarRepository
from services.calendar_service import CalendarService
from models.event import Event
from services.exceptions import CalendarError

app = FastAPI(title="Calendar Management System API", version="1.0.0")

repo = CalendarRepository("data/calendar.csv")
service = CalendarService(repo)

class EventRequest(BaseModel):
    person_name: str
    subject: str
    start_time: str  # פורמט "HH:MM"
    end_time: str    # פורמט "HH:MM"

@app.get("/available-slots")
def get_available_slots(people: str, duration_minutes: int):
    """
    מקבל רשימת אנשים מופרדת בפסיקים ומשך בדקות, ומחזיר את החלונות הפנויים.
    דוגמה: /available-slots?people=Alice,Bob&duration_minutes=60
    """
    people_list = [p.strip() for p in people.split(",") if p.strip()]
    duration = timedelta(minutes=duration_minutes)
    
    try:
        slots = service.find_available_slots(people_list, duration)
        return [
            {"start": slot.start.strftime("%H:%M"), "end": slot.end.strftime("%H:%M")}
            for slot in slots
        ]
    except CalendarError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/events")
def add_event(event_req: EventRequest):
    """
    מוסיף אירוע חדש ללוח השנה לאחר בדיקת תקינות והתנגשויות.
    """
    try:
        start_t = time.strptime(event_req.start_time, "%H:%M") # לחלופין המרה ישירה ל-time
        # המרה בטוחה של שעות:
        start_parts = list(map(int, event_req.start_time.split(":")))
        end_parts = list(map(int, event_req.end_time.split(":")))
        
        start_time = time(start_parts[0], start_parts[1])
        end_time = time(end_parts[0], end_parts[1])

        new_event = Event(event_req.person_name, event_req.subject, start_time, end_time)
        service.add_event_safely(new_event)
        return {"status": "success", "message": "האירוע נוסף בהצלחה"}
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="פורמט שעות שגוי, יש להשתמש ב-HH:MM")
    except CalendarError as e:
        raise HTTPException(status_code=400, detail=str(e))