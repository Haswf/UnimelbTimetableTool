import calendar
import datetime
import pytz

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
