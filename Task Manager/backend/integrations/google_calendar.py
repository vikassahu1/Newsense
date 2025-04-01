from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

def get_upcoming_events() -> List[Dict[str, Any]]:
    """
    Get upcoming events from the calendar.
    For now, return mock data.
    """
    # Mock data for testing
    mock_events = [
        {
            "id": "1",
            "summary": "Team Meeting",
            "start": (datetime.now() + timedelta(hours=1)).isoformat(),
            "end": (datetime.now() + timedelta(hours=2)).isoformat(),
            "location": "Conference Room A"
        },
        {
            "id": "2",
            "summary": "Project Review",
            "start": (datetime.now() + timedelta(hours=3)).isoformat(),
            "end": (datetime.now() + timedelta(hours=4)).isoformat(),
            "location": "Virtual Meeting"
        }
    ]
    return mock_events

def analyze_calendar_data() -> Dict[str, Any]:
    """
    Analyze calendar data to provide insights.
    For now, return mock data.
    """
    # Mock analysis data
    analysis = {
        "total_meetings": 2,
        "total_meeting_hours": 2,
        "avg_meeting_duration": 1.0,
        "busiest_day": datetime.now().strftime("%A"),
        "meeting_distribution": {
            "morning": 1,
            "afternoon": 1,
            "evening": 0
        }
    }
    return analysis

def get_today_events() -> List[Dict[str, Any]]:
    """
    Get today's events from the calendar.
    For now, return mock data.
    """
    today = datetime.now().date()
    mock_today_events = [
        {
            "id": "1",
            "summary": "Daily Standup",
            "start": datetime.combine(today, datetime.min.time().replace(hour=10)).isoformat(),
            "end": datetime.combine(today, datetime.min.time().replace(hour=10, minute=30)).isoformat(),
            "location": "Virtual Meeting"
        }
    ]
    return mock_today_events 