import scrapy
import os
from LoginCredential import LoginCredential
from pathlib2 import Path
from timetable.items import Class
from scrapy.exceptions import CloseSpider
import logging

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
        # Extract ClassContainer selector to construct iterator
        classContainer = response.xpath("//div[@class='cssClassContainer']")
        # Match subject code and subject name
        subject_pair = self.match_code_name(response)

        timetable = list()

        for class_info in ClassContainerIterator(classContainer):
            # Add subject_name to class_info
            class_info['subject_name'] = subject_pair[class_info['subject_code']]
            yield class_info

    def match_code_name(self, response):
        # TODO: Documentation required
        subject_pair = {}

        # Extract all subject codes in order
        subject_codes = []
        for subject_code_selector in response.xpath(
                "//div[@class='cssTtableRoundBorder cssTtableSspColourBlock']/span/text()"):
            sub_code = subject_code_selector.get().strip()
            if len(sub_code) and sub_code not in subject_codes:
                subject_codes.append(sub_code)

        # Extract all subject names in order
        subject_names = []
        for subject_name_selector in response.xpath("//td[@class='cssTtableSspNavMasterSpkInfo3']/div/text()"):
            subject_name = subject_name_selector.get().strip()
            if len(subject_name) and subject_name not in subject_names:
                subject_names.append(subject_name)

        # Match subject code and name
        for i in range(len(subject_names)):
            subject_pair[subject_codes[i]] = subject_names[i]

        return subject_pair


class ClassContainerIterator:
    """
    This class is used to iterate all subject info in classContainers

    """
    def __init__(self, classContainers, start=0):
        self.num = start
        self.classContainers = classContainers

    def __iter__(self):
      return self

    def __next__(self):
        # TODO: Doc required
        # Stop iteration if last element in classContainer has been reached
        if self.num >= len(self.classContainers):
            raise StopIteration
        else:
            class_info = Class()
            class_info['subject_code'] = self.classContainers.xpath("//div[@class='cssTtableHeaderPanel']/text()").getall()[self.num].strip()
            class_info['class_type'] = self.classContainers.xpath("//span[@class='cssTtableClsSlotWhat']/text()").getall()[self.num].strip()
            class_info['class_time'] = self.classContainers.xpath("//span[@class='cssTtableClsSlotWhen']/text()").getall()[self.num].strip(', ')
            class_info['class_location'] = self.classContainers.xpath("//span[@class='cssTtableClsSlotWhere']/text()").getall()[self.num].strip()
            # go to next element
            self.num += 1
            return class_info