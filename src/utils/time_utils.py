from datetime import datetime, timezone, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def get_ist_time() -> dict:
    now = datetime.now(timezone.utc)
    ist_now = now + IST_OFFSET
    return {
        "datetime": ist_now,
        "hours": ist_now.hour,
        "minutes": ist_now.minute,
        "day": DAY_NAMES[ist_now.weekday()],
        "timestamp": ist_now.timestamp(),
        "iso": ist_now.isoformat(),
    }


def convert_to_12_hour(time24: str | None) -> str:
    if not time24 or ":" not in time24:
        return time24 or ""
    parts = time24.split(":")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except (ValueError, IndexError):
        return time24
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        return time24
    period = "PM" if hours >= 12 else "AM"
    hour12 = hours % 12
    if hour12 == 0:
        hour12 = 12
    return f"{hour12}:{minutes:02d} {period}"


def parse_time(time_str: str) -> int:
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def format_minutes(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def _is_closed_slot(open_str: str | None, close_str: str | None) -> bool:
    if not open_str or not close_str:
        return True
    return open_str in ("closed", "00:00") and close_str in ("closed", "00:00")


def get_business_status(business: dict) -> dict:
    hours = business.get("hours")
    if not hours:
        return {
            "isOpen": None,
            "message": "Hours not available",
            "cssClass": "status-unknown",
            "nextChange": None,
            "minutesUntilClose": None,
            "minutesUntilOpen": None,
            "showCountdown": False,
        }
    ist = get_ist_time()
    day_hours = hours.get(ist["day"])
    if not day_hours:
        return {
            "isOpen": False,
            "message": "Closed today",
            "cssClass": "status-closed",
            "nextChange": None,
            "minutesUntilClose": None,
            "minutesUntilOpen": None,
            "showCountdown": False,
        }
    open1 = day_hours.get("open", "00:00")
    close1 = day_hours.get("close", "00:00")
    open2 = day_hours.get("open2")
    close2 = day_hours.get("close2")
    shift1_closed = _is_closed_slot(open1, close1)
    shift2_exists = not _is_closed_slot(open2, close2)
    if shift1_closed and not shift2_exists:
        return {
            "isOpen": False,
            "message": "Closed today",
            "cssClass": "status-closed",
            "nextChange": None,
            "minutesUntilClose": None,
            "minutesUntilOpen": None,
            "showCountdown": False,
        }
    try:
        current_minutes = ist["hours"] * 60 + ist["minutes"]
        shifts = []
        if not shift1_closed:
            shifts.append({
                "open": parse_time(open1),
                "close": parse_time(close1),
                "open_str": open1,
                "close_str": close1,
            })
        if shift2_exists:
            shifts.append({
                "open": parse_time(open2),  # type: ignore[arg-type]
                "close": parse_time(close2),  # type: ignore[arg-type]
                "open_str": open2,
                "close_str": close2,
            })
        for shift in shifts:
            if shift["open"] <= current_minutes < shift["close"]:
                minutes_left = shift["close"] - current_minutes
                message = f"Open \u2022 Closes in {format_minutes(minutes_left)}"
                if minutes_left >= 120:
                    message = f"Open \u2022 Closes at {convert_to_12_hour(shift['close_str'])}"
                return {
                    "isOpen": True,
                    "message": message,
                    "cssClass": "status-open",
                    "nextChange": shift["close_str"],
                    "minutesUntilClose": minutes_left,
                    "minutesUntilOpen": None,
                    "showCountdown": minutes_left <= 60,
                }
        for shift in shifts:
            if current_minutes < shift["open"]:
                minutes_until = shift["open"] - current_minutes
                message = f"Closed \u2022 Opens in {format_minutes(minutes_until)}"
                return {
                    "isOpen": False,
                    "message": message,
                    "cssClass": "status-closed",
                    "nextChange": shift["open_str"],
                    "minutesUntilClose": None,
                    "minutesUntilOpen": minutes_until,
                    "showCountdown": minutes_until <= 60,
                }
        return {
            "isOpen": False,
            "message": "Closed today",
            "cssClass": "status-closed",
            "nextChange": None,
            "minutesUntilClose": None,
            "minutesUntilOpen": None,
            "showCountdown": False,
        }
    except (ValueError, KeyError):
        return {
            "isOpen": None,
            "message": "Hours not available",
            "cssClass": "status-unknown",
            "nextChange": None,
            "minutesUntilClose": None,
            "minutesUntilOpen": None,
            "showCountdown": False,
        }
