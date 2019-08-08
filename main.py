from timetable import crawl
from gcalendar import calendar_api

# import timetablespider from spider class
from timetable.spiders.timetable import TimeTableSpider

from scrapy import signals
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
import logging


if __name__ == "__main__":
    crawler = Crawler(TimeTableSpider)
    #runner = CrawlerRunner()
    #runner.crawl(TimeTableSpider)
    crawler.crawl()
    #calendar_api.create_timetable()



