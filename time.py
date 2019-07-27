import datetime


def next_weekday(d, weekday):
    # credit: phihag
    # reference: https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def generate_timestamp(time, weekday):
    weekday = next_weekday(datetime.date.today(), weekday)  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    return datetime.datetime(weekday.year, weekday.month, weekday.day, time.hour, time.minute).strftime(
        '%Y-%m-%dT%H:%M:%S.%fZ')


if __name__ == '__main__':
    semester_start = datetime.date(2019, 7, 29)
    semester_end = datetime.date(2019, 10, 27)
    print(generate_timestamp(datetime.time(10, 30), 3))
