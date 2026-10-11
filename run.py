import argparse
import logging
from datetime import datetime, timedelta
from models.event import Event
from repository.calendar_repository import CalendarRepository
from services.calendar_service import CalendarService
from services.exceptions import CalendarError

# הגדרת לוגינג מקצועי
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Calendar Management System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # פקודת חיפוש חלונות פנויים: python run.py find --people Alice,Bob --duration 60
    find_parser = subparsers.add_parser("find", help="Find available time slots")
    find_parser.add_argument("--people", required=True, help="Comma-separated list of people names")
    find_parser.add_argument("--duration", type=int, required=True, help="Duration in minutes")

    # פקודת הוספת אירוע: python run.py add --person Alice --subject Meeting --start 09:00 --end 10:00
    add_parser = subparsers.add_parser("add", help="Add a new calendar event")
    add_parser.add_argument("--person", required=True, help="Person name")
    add_parser.add_argument("--subject", required=True, help="Event subject")
    add_parser.add_argument("--start", required=True, help="Start time (HH:MM)")
    add_parser.add_argument("--end", required=True, help="End time (HH:MM)")

    args = parser.parse_args()

    repo = CalendarRepository("data/calendar.csv")
    service = CalendarService(repo)

    if args.command == "find":
        people = [p.strip() for p in args.people.split(",") if p.strip()]
        duration = timedelta(minutes=args.duration)
        try:
            slots = service.find_available_slots(people, duration)
            logger.info("נמצאו %d חלונות פנויים.", len(slots))
            print(f"Available slots found ({len(slots)}):")
            for slot in slots:
                print(f" - From {slot.start.strftime('%H:%M')} to {slot.end.strftime('%H:%M')}")
        except CalendarError as e:
            logger.error("שגיאה בחיפוש חלונות: %s", e)
            print(f"Error: {e}")

    elif args.command == "add":
        try:
            start_time = datetime.strptime(args.start, "%H:%M").time()
            end_time = datetime.strptime(args.end, "%H:%M").time()
            new_event = Event(args.person, args.subject, start_time, end_time)
            service.add_event_safely(new_event)
            logger.info("האירוע נוסף בהצלחה עבור %s.", args.person)
            print("Event added successfully!")
        except (ValueError, CalendarError) as e:
            logger.error("שגיאה בהוספת אירוע: %s", e)
            print(f"Error: {e}")

    else:
        # במקרה שלא הועברו ארגומנטים בשורת הפקודה, המערכת תרוץ במצב אינטראקטיבי רגיל
        run_interactive_mode(service)

def run_interactive_mode(service):
    logger.info("מערכת ניהול לוח השנה הופעלה במצב אינטראקטיבי.")
    while True:
        print("\n--- Calendar Management System ---")
        print("1. Find available slots")
        print("2. Add new event")
        print("3. Exit")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            people_input = input("Enter names separated by comma (e.g., Alice,Bob): ").strip()
            people = [p.strip() for p in people_input.split(",") if p.strip()]
            try:
                minutes_input = input("Enter duration in minutes (e.g., 60): ").strip()
                duration = timedelta(minutes=int(minutes_input))
                slots = service.find_available_slots(people, duration)
                print(f"Available slots found ({len(slots)}):")
                for slot in slots:
                    print(f" - From {slot.start.strftime('%H:%M')} to {slot.end.strftime('%H:%M')}")
            except ValueError:
                print("שגיאה: נא להזין מספר דקות תקין.")

        elif choice == "2":
            person = input("Person name: ").strip()
            subject = input("Event subject: ").strip()
            
            while True:
                start_input = input("Start time (format HH:MM): ").strip()
                try:
                    start_time = datetime.strptime(start_input.split()[0], "%H:%M").time()
                    break
                except (ValueError, IndexError):
                    print("שגיאה: נא להזין שעה תקינה בפורמט HH:MM (לדוגמה 09:00)")
            
            while True:
                end_input = input("End time (format HH:MM): ").strip()
                try:
                    end_time = datetime.strptime(end_input.split()[0], "%H:%M").time()
                    break
                except (ValueError, IndexError):
                    print("שגיאה: נא להזין שעה תקינה בפורמט HH:MM (לדוגמה 10:00)")
            
            try:
                new_event = Event(person, subject, start_time, end_time)
                service.add_event_safely(new_event)
                print("Event added successfully!")
            except CalendarError as e:
                print(f"Error: {e}")
            
        elif choice == "3":
            logger.info("סגירת המערכת לבקשת המשתמש.")
            print("Goodbye!")
            break
        else:
            logger.warning("הוזנה בחירה לא חוקית בתפריט: %s", choice)
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()