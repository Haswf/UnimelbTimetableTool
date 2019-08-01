from __future__ import print_function
import datetime
import pickle
import os.path
import json
import pytz
import calendar
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import defaultdict

# If modifying these scopes, delete the file token.pickle.
# This scope grants access to view/edit/delete events
SCOPES = ['https://www.googleapis.com/auth/calendar']

TIMEZONE = 'Australia/Melbourne'
"""str: timezone of Melbourne"""

CALENDAR_SUMMARY = 'Unimelb Timetable'
"""str: calendar summary(name)"""

SEMESTER_END_YEAR = 2019
"""int: On which year the semester ends"""
SEMESTER_END_MONTH = 10
"""int: On which month the semester ends"""
SEMESTER_END_DAY = 27
"""int: On which day the semester ends"""

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

def main():
    service = build_service()

    calendarId = find_calendar(service, CALENDAR_SUMMARY)
    if not calendarId:
        calendarId = new_calendar(service, CALENDAR_SUMMARY, TIMEZONE)
    else:
        remove_calendar(service, calendarId=calendarId)
    # load timetable from class.json
    with open('class.json', 'r') as f:
        timetable = json.load(f)
        groupby = groupby_subject(timetable)

    color_id = 1
    for subject in groupby:
        for _class in groupby[subject]:
            start_time = datetime.time(*tuple([int(i) for i in _class['class_start_time'].split(":")]))
            finish_time = datetime.time(*tuple([int(i) for i in _class['class_finish_time'].split(":")]))

            start_timestamp = generate_timestamp(start_time, get_int_weekday(_class['class_weekday']))
            end_timestamp = generate_timestamp(finish_time, get_int_weekday(_class['class_weekday']))

            recurrence_end = datetime.datetime(year=SEMESTER_END_YEAR,
                                               month=SEMESTER_END_MONTH,
                                               day=SEMESTER_END_DAY).strftime('%Y%m%dT%H%M%SZ')

            event = {
                'summary': "{}: {}".format(_class['subject_code'], _class['class_type']),
                'location': _class['class_location'],
                'description':  "This event was added by UnimelbTimetableTool. "
                                "Support us by starring this project at "
                                "https://github.com/Haswf/UnimelbTimetableTool",

                'start': {
                    'dateTime': start_timestamp,
                    'timeZone': TIMEZONE,
                },
                'end': {
                    'dateTime': end_timestamp,
                    'timeZone': TIMEZONE,
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
            event = service.events().insert(calendarId=calendarId, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        color_id += 1

def next_weekday(d, weekday):
    # credit: phihag
    # reference: https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def next_weekday(d, weekday):
    # credit: phihag
    # reference: https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def get_int_weekday(weekday):
    """
    Returns int representation of given weekday from 0 to 6
    :param weekday:
    :return:
    """
    return list(calendar.day_name).index(weekday)

def generate_timestamp(time, weekday):
    """
    Generate timestamp for Google Event API
    :param time:
    :param weekday:
    :return:
    """
    weekday = next_weekday(datetime.date.today(), weekday)  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    local_datetime = datetime.datetime(weekday.year, weekday.month, weekday.day, time.hour, time.minute)
    utc_datetime = convert_to_UTC(local_datetime, 'Australia/Melbourne')
    return utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def convert_to_UTC(localdatetime, timezone):
    """
    Convert a localised datetime to UTC datetime
    :param localdatetime: a datetime object
    :return:
    """
    localtime = pytz.timezone(timezone).localize(localdatetime)
    # Transform the time to UTC
    utc_time = localdatetime.astimezone(pytz.utc)
    return utc_time

def groupby_subject(timetable):
    groupby = defaultdict(list)
    for _class in timetable:
        groupby[_class["subject_code"]].append(_class)
    return groupby

if __name__ == '__main__':
    main()