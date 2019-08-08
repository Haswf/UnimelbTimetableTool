from timetable import crawl
from gcalendar import calendar_api

# import timetablespider from spider class
from timetable.spiders.timetable import TimeTableSpider
from timetable import crawl

if __name__ == "__main__":
    crawl.run()

