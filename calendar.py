import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
# This scope grants access to view/edit/delete events
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Add class to Google Calendar
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

    service = build('calendar', 'v3', credentials=creds)

    start = datetime.datetime.utcnow()
    start_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end = start + datetime.timedelta(hours=2)
    end_timestamp = end.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    recurrence_end = datetime.datetime(year=2019, month=10, day=27).strftime('%Y%m%dT%H%M%SZ')

    event = {
        'summary': 'Colour Test',
        'location': 'The University of Melbourne',
        'description': '',
        'start': {
            'dateTime': start_timestamp,
            'timeZone': 'Australia/Melbourne',
        },
        'end': {
            'dateTime': end_timestamp,
            'timeZone': 'Australia/Melbourne',
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;UNTIL={}".format(recurrence_end),
        ],
        'colorId': '1',
    }
    # Insert event to calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


if __name__ == '__main__':
    main()
