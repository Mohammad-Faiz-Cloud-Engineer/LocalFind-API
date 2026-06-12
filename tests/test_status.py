import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.time_utils import (
    get_ist_time,
    convert_to_12_hour,
    get_business_status,
    parse_time,
    format_minutes,
)
from src.data.loader import get_listing_by_id
from src.services.status_service import get_status_for_business, get_open_businesses


def test_get_ist_time():
    ist = get_ist_time()
    assert "hours" in ist
    assert "minutes" in ist
    assert "day" in ist
    assert "datetime" in ist
    assert 0 <= ist["hours"] <= 23
    assert 0 <= ist["minutes"] <= 59
    assert ist["day"] in ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def test_convert_to_12_hour():
    assert convert_to_12_hour("09:00") == "9:00 AM"
    assert convert_to_12_hour("12:00") == "12:00 PM"
    assert convert_to_12_hour("15:30") == "3:30 PM"
    assert convert_to_12_hour("00:00") == "12:00 AM"
    assert convert_to_12_hour("23:59") == "11:59 PM"
    assert convert_to_12_hour("") == ""
    assert convert_to_12_hour(None) == ""


def test_parse_time():
    assert parse_time("09:00") == 540
    assert parse_time("00:00") == 0
    assert parse_time("23:59") == 1439
    assert parse_time("12:30") == 750


def test_format_minutes():
    assert format_minutes(30) == "30 min"
    assert format_minutes(60) == "1h"
    assert format_minutes(90) == "1h 30m"
    assert format_minutes(0) == "0 min"


def test_get_business_status_found():
    biz = get_listing_by_id("aman-garments")
    assert biz is not None
    status = get_business_status(biz)
    assert "isOpen" in status
    assert "message" in status
    assert "cssClass" in status
    assert status["cssClass"] in ("status-open", "status-closed", "status-unknown")


def test_get_business_status_no_hours():
    status = get_business_status({})
    assert status["isOpen"] is None
    assert status["cssClass"] == "status-unknown"


def test_get_status_for_business():
    status = get_status_for_business("aman-garments")
    assert status is not None
    assert "businessId" in status
    assert "businessName" in status
    assert "currentTime" in status
    assert "todayHours" in status


def test_get_status_for_nonexistent():
    status = get_status_for_business("nonexistent")
    assert status is None


def test_get_open_businesses():
    open_biz = get_open_businesses()
    assert isinstance(open_biz, list)
    for biz in open_biz:
        assert biz.get("isOpen") is True


if __name__ == "__main__":
    test_get_ist_time()
    test_convert_to_12_hour()
    test_parse_time()
    test_format_minutes()
    test_get_business_status_found()
    test_get_business_status_no_hours()
    test_get_status_for_business()
    test_get_status_for_nonexistent()
    test_get_open_businesses()
    print("All status tests passed!")
