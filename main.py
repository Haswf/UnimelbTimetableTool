from timetable import crawl
from gcalendar import calendar_api

if __name__ == "__main__":
    crawl.run()
    calendar_api.create_timetable()

