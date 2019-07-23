import scrapy
import logging
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

class TimeTableSpider(scrapy.Spider):
    name = "timetable"
    start_urls = ['https://prod.ss.unimelb.edu.au/student/Login.aspx']

    def parse(self, response):
        self.log("Getting tokens for login")
        view_state = response.xpath("//div/input[@name='__VIEWSTATE']/@value").extract_first()
        event_validation = response.xpath("//div/input[@name='__EVENTVALIDATION']/@value").extract_first()
        view_state_generator = response.xpath("//*/div/input[@name='__VIEWSTATEGENERATOR']/@value").extract_first()
        formdata = {'__EVENTTARGET': 'ctl00$Content$cmdLogin', 
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_generator,
            '__EVENTVALIDATION': event_validation,
            'ctl00$Content$txtUserName$txtText':'SHUYANGF',
            'ctl00$Content$txtPassword$txtText': 'UnimelbHaswf0204',
            }
        return scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.open_timetable)
        
    def open_timetable(self,response):
        # get url of timetable
        # this xpath expression is ulgy...
        timetable_url = response.xpath("//div[@class='nav-collapse']/ul/li[2]/a/@href").get()
        if timetable_url is not None:
           # yield scrapy.Request(timetable_url, callback=self.parse_timetable)
            yield response.follow(timetable_url, callback=self.parse_timetable)

    def parse_timetable(self, response):
        open_in_browser(response)
        #for class_info in response.xpath("//div[@class=cssTtableHeaderPanel]").getall():
        class_info = response.xpath("//div[@class='cssClassContainer']")
        for i in class_info:
            subject_code = i.xpath("//div[@class='cssTtableHeaderPanel']/text()").get()
            class_type = i.xpath("//span[@class='cssTtableClsSlotWhat']/text()").get()
            self.log(subject_code, class_type)
