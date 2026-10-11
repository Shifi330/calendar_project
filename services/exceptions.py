class CalendarError(Exception):
    """מחלקת בסיס גלובלית לשגיאות במערכת לוח השנה"""
    pass

class EventConflictError(CalendarError):
    """נזרקת כאשר מנסים לקבוע אירוע בזמן שכבר קיים אירוע חופף"""
    pass

class InvalidTimeRangeError(CalendarError):
    """נזרקת כאשר טווח הזמנים שגוי (למשל שעת סיום שווה או קודמת לשעת ההתחלה)"""
    pass