from __future__ import print_function
import datetime
import pickle
import os.path
import json
from os.path import dirname, abspath, join

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from gcalendar.time import generate_timestamp, get_int_weekday
from gcalendar.subject import groupby_subject
# import project settings
import settings

# If modifying these scopes, delete the file token.pickle.
# This scope grants access to view/edit/delete events
SCOPES = ['https://www.googleapis.com/auth/calendar']

def build_service():
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
    return service

def find_calendar(service, summary):
    """Look for a calendar which has `summary`. Return calendarId if found,
    return None if not found.

    Args:
        service (:obj:`service`) service built by googleapiclient.discovery.build.
        summary (str, optional) calendar summary. Refers to
            https://developers.google.com/calendar/v3/reference/calendarList.
        calendarId (str, optional) calendar ID

    Returns:
        str: calendarID of the calendar specified by `summary`.
                return None if the calendar does't exist.
    """
    page_token = None
    calendarID = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if (calendar_list_entry['summary']) == summary:
                calendarID = calendar_list_entry['id']
                break
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendarID

def remove_calendar(service, summary=None, calendarId=None):
    """remove a calendar specified by either summary or
    calendar ID from Google Calendar.

    Args:
        service (:obj:`service`) service built by googleapiclient.discovery.build.
        summary (str, optional) calendar summary. Refers to
            https://developers.google.com/calendar/v3/reference/calendarList.
        calendarId (str, optional) calendar ID

    Returns:
        No value will be returned.

    Raises:
        ValueError: if neither summary nor calendarId was provided as required.

    """
    if not summary and not calendarId:
        raise ValueError("Neither summary nor calendarId was provided")
    if not calendarId:
        calendarID = find_calendar(service, summary)
    service.calendarList().delete(calendarId=calendarId).execute()

def new_calendar(service, summary, timezone):
    """Insert a new calendar to Google Calendar.

    Args:
        service (:obj:`service`) service built by googleapiclient.discovery.build.
        summary (str) calendar summary. Refers to
            https://developers.google.com/calendar/v3/reference/calendarList.
        timezone (str) string which represents a timezone, e.g, "Australia/Melbourne"

    Returns:
        str: CalendarId of newly created calendar
    """

    calendar = {
        'summary': summary,
        'timeZone': timezone
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']

def create_timetable():
    service = build_service()

    calendarId = find_calendar(service, settings.CALENDAR_SUMMARY)
    if not calendarId:
        calendarId = new_calendar(service, settings.CALENDAR_SUMMARY, settings.TIMEZONE)
    else:
        remove_calendar(service, calendarId=calendarId)
    # load timetable from class.json
    file_path = join(dirname(dirname(abspath(__file__))), 'class.json')

    with open(file_path, 'r') as f:
        timetable = json.load(f)
        groupby = groupby_subject(timetable)

    color_id = 1
    for subject in groupby:
        for _class in groupby[subject]:
            start_time = datetime.time(*tuple([int(i) for i in _class['class_start_time'].split(":")]))
            finish_time = datetime.time(*tuple([int(i) for i in _class['class_finish_time'].split(":")]))

            start_timestamp = generate_timestamp(start_time, get_int_weekday(_class['class_weekday']))
            end_timestamp = generate_timestamp(finish_time, get_int_weekday(_class['class_weekday']))

            recurrence_end = datetime.datetime(year=settings.SEMESTER_END_YEAR,
                                               month=settings.SEMESTER_END_MONTH,
                                               day=settings.SEMESTER_END_DAY).strftime('%Y%m%dT%H%M%SZ')

            event = {
                'summary': "{}: {}".format(_class['subject_code'], _class['class_type']),
                'location': _class['class_location'],
                'description':  "This event was added by UnimelbTimetableTool. "
                                "Support us by starring this project at "
                                "https://github.com/Haswf/UnimelbTimetableTool",

                'start': {
                    'dateTime': start_timestamp,
                    'timeZone': settings.TIMEZONE,
                },
                'end': {
                    'dateTime': end_timestamp,
                    'timeZone': settings.TIMEZONE,
                },
                'recurrence': [
                    "RRULE:FREQ=WEEKLY;UNTIL={}".format(recurrence_end),
                ],
                'colorId': color_id,
                'reminders': {
                    "useDefault": 'false'
                }
            }
            # Insert event to calendar
            if not settings.READ_ONLY:
                event = service.events().insert(calendarId=calendarId, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        color_id += 1



if __name__ == "__main__":
    create_timetable()