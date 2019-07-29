from __future__ import print_function
import datetime
import pickle
import os.path
import json
import pytz
import calendar
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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

    with open('class.json', 'r') as f:
        timetable = json.load(f)

    for each_class in timetable:
        start_time = datetime.time(*tuple([int(i) for i in each_class['class_start_time'].split(":")]))
        finish_time = datetime.time(*tuple([int(i) for i in each_class['class_finish_time'].split(":")]))

        start_timestamp = generate_timestamp(start_time, get_int_weekday(each_class['class_weekday']))
        end_timestamp = generate_timestamp(finish_time, get_int_weekday(each_class['class_weekday']))
        recurrence_end = datetime.datetime(year=2019, month=10, day=27).strftime('%Y%m%dT%H%M%SZ')

        event = {
            'summary': "{}: {}".format(each_class['subject_code'], each_class['class_type']),
            'location': each_class['class_location'],
            'description': '',
            'start': {
                'dateTime': start_timestamp,
                'timeZone': 'Australia/Melbourne',
            },
            'end': {
                'dateTime': end_timestamp,
                'timeZone': 'Australia/Melbourne',
            },
            'recurrence': [
                "RRULE:FREQ=WEEKLY;UNTIL={}".format(recurrence_end),
            ],
            'colorId': '1',
            'reminders': {
                "useDefault": 'false'
            }
        }
        # Insert event to calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

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



if __name__ == '__main__':
    main()
