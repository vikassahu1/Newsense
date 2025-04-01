# backend/app/integrations/google_calendar.py
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """Get or create a Calendar API service object."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def get_upcoming_events(days=7):
    """Get upcoming calendar events for the next n days."""
    service = get_calendar_service()
    
    # Calculate time boundaries
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    then = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=then,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    formatted_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # Format the event data
        formatted_events.append({
            'id': event['id'],
            'summary': event['summary'],
            'start': start,
            'end': event['end'].get('dateTime', event['end'].get('date')),
            'location': event.get('location', ''),
            'description': event.get('description', ''),
            'attendees': [attendee.get('email') for attendee in event.get('attendees', [])]
        })
    
    return formatted_events

def analyze_calendar_data(events):
    """Analyze calendar data to extract patterns and insights."""
    # This is a simple analysis. In a real app, you'd use more sophisticated algorithms.
    meetings_count = len(events)
    meeting_hours = 0
    
    for event in events:
        # For simplicity, we're assuming dateTime format
        if 'T' in event['start'] and 'T' in event['end']:
            start = datetime.datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            end = datetime.datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
            duration = (end - start).total_seconds() / 3600  # Convert to hours
            meeting_hours += duration
    
    return {
        'total_meetings': meetings_count,
        'total_meeting_hours': round(meeting_hours, 1),
        'avg_meeting_duration': round(meeting_hours / meetings_count if meetings_count > 0 else 0, 1),
        'busiest_day': 'Thursday'  # Placeholder - in a real app, calculate this
    }