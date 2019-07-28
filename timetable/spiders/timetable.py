import scrapy
import os
from LoginCredential import LoginCredential
from pathlib2 import Path
from timetable.items import Class
from scrapy.exceptions import CloseSpider
import logging
import datetime
import time

class TimeTableSpider(scrapy.Spider):
    name = "timetable"
    start_urls = ['https://prod.ss.unimelb.edu.au/student/Login.aspx']
    # credential file name that contains username and password
    credential_file = 'uom.json'
    credential_obj = None

    def __init__(self):
        super().__init__()
        self.credential_obj = LoginCredential(filepath=self.get_credential_path())

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.log_in, dont_filter=False)

    def log_in(self, response):
        # TODO: Doc required
        self.log(level=logging.INFO, message="Getting tokens for login")
        # call credential_obj to get username and password
        self.credential_obj.get_credential()

        # Construct form data
        # TODO：get __EVENTTARGET from response instead of hard coding it
        formdata = {'__EVENTTARGET': 'ctl00$Content$cmdLogin',
                    '__VIEWSTATE': response.xpath("//div/input[@name='__VIEWSTATE']/@value").get(),
                    '__VIEWSTATEGENERATOR': response.xpath("//*/div/input[@name='__VIEWSTATEGENERATOR']/@value").get(),
                    '__EVENTVALIDATION': response.xpath("//div/input[@name='__EVENTVALIDATION']/@value").get(),
                    'ctl00$Content$txtUserName$txtText': self.credential_obj.username,
                    'ctl00$Content$txtPassword$txtText': self.credential_obj.password
                    }

        # validate tokens
        for token in formdata.values():
            if not len(token):
                # close spider if invalid was provided
                self.log(level=logging.CRITICAL, message="Invalid login token(s): {}".format(token))
                raise CloseSpider("Invalid login token(s): {}".format(token))

        return scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.open_timetable)
    #
    # def parse(self, response):
    #    return

    def get_credential_path(self):
        """
        Get real path of credential json file
        :return:
        """
        __location__ = Path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
        return Path(os.path.join(__location__.parent.parent,  # equivalent to .../uom.json
                                            self.credential_file))

    def validate_login(self, response):
        # Validate if log in was successful
        login_summary = response.xpath("//div[@class='cssT1SmBasicFormValidationSummary']").get()

        if (login_summary and "Your login attempt was not successful" in login_summary):
            # In this case, close spider and delete credential file
            self.log(level=logging.CRITICAL, message='Login failed: Incorrect username or/and password')
            self.credential_obj.remove_file()
            raise CloseSpider(reason='Login failed: Incorrect username and/or password')

    def open_timetable(self, response):
        # validate if login is successful
        self.validate_login(response)
        # get url of timetable
        # TODO: this xpath expression is ugly...It's probably better to rewrite it someday.
        self.log(level=logging.INFO, message='Login succeed')
        timetable_url = response.xpath("//div[@class='nav-collapse']/ul/li[2]/a/@href").get()
        yield response.follow(timetable_url, callback=self.parse_timetable)

    def parse_timetable(self, response):
        # TODO: Doc required
        for subject in response.xpath("//div[@class='cssTtableSspNavContainer']"):
            subject_code = subject.xpath(".//div[@class='cssTtableRoundBorder cssTtableSspColourBlock']/span/text()").get().strip()
            subject_name = subject.xpath(".//td[@class='cssTtableSspNavMasterSpkInfo3']/div/text()").get().strip()
            semester = subject.xpath(".//span[@class='cssTtablePeriod']/text()").get().strip()
            for each_class in subject.xpath(".//div[@class='cssTtableNavActvTop']"):
                class_info = Class()
                class_info['subject_name'] = subject_name
                class_info['subject_code'] = subject_code
                class_info['semester'] = semester
                class_info['class_type'] = each_class.xpath(".//div[@class='cssTtableSspNavActvNm']/text()").get().strip()
                class_info['class_location'] = each_class.xpath(".//span[@class='cssTtableNavMainWhere']/span[@class='cssTtableNavMainContent']/text()").get().strip()

                # TODO:　Implement paese_time function to separate weekday, start_time and finish_time
                class_info['class_weekday'], \
                class_info['class_start_time'], \
                class_info['class_finish_time']= self.parse_time(each_class.xpath(".//span[@class='cssTtableNavMainWhen']/span[@class='cssTtableNavMainContent']/text()").get().strip())

                yield class_info

    def parse_time(self, raw_text):
        AM_OFFSET = 0 # add 0 hours if time is between 0 AM to 1 PM
        PM_OFFSET = 12 # add 12 hours if time is between 1 PM to 0 AM

        # start_am and end_am denotes am/pm. I could't come up with a better name.
        week_day, start_time, start_am, finish_time, end_am = raw_text.replace('-', ' ', 1).split(" ")

        # typecast start_time, finish_time to datetime.time object
        start_time = datetime.time(*tuple([int(i) for i in start_time.split(':')]))
        finish_time = datetime.time(*tuple([int(i) for i in finish_time.split(':')]))

        # lambda function to get time offset for am/pm
        offset = lambda x, y: (PM_OFFSET if 'pm' in x and y.hour!=12 else AM_OFFSET)

        # apply am/pm offset to start_time
        start_time = (datetime.datetime.combine(datetime.date.today(), start_time)
                      + datetime.timedelta(hours=offset(start_am, start_time))).time()
        # apply am/pm offset to end_time
        finish_time = (datetime.datetime.combine(datetime.date.today(), finish_time)
                      + datetime.timedelta(hours=offset(end_am, finish_time))).time()
        return week_day, start_time, finish_time