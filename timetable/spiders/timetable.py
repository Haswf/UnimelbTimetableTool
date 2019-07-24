import scrapy
import os
from pathlib2 import Path
import json
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

class TimeTableSpider(scrapy.Spider):
    name = "timetable"
    start_urls = ['https://prod.ss.unimelb.edu.au/student/Login.aspx']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.log_in, dont_filter=False)

    def log_in(self, response):
        self.log("Getting tokens for login")
        username, password = self.get_login_credential()
        # TODO：get __EVENTTARGET from response instead of hard coding it
        formdata = {'__EVENTTARGET': 'ctl00$Content$cmdLogin',
                    '__VIEWSTATE': response.xpath("//div/input[@name='__VIEWSTATE']/@value").get(),
                    '__VIEWSTATEGENERATOR': response.xpath("//*/div/input[@name='__VIEWSTATEGENERATOR']/@value").get(),
                    '__EVENTVALIDATION': response.xpath("//div/input[@name='__EVENTVALIDATION']/@value").get(),
                    'ctl00$Content$txtUserName$txtText': username,
                    'ctl00$Content$txtPassword$txtText': password,
                    }

        # validate tokens
        for token in formdata.values():
            if not len(token):
                raise ValueError("Invalid login token(s): {}".format(token))

        return scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.open_timetable)


    def get_login_credential(self):
        # credential file name that contains username and password
        CREDENTIAL_FILE_NAME = 'uom.json'

        # Get path of credential json file
        __location__ = Path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
        credential_path = Path(os.path.join(__location__.parent.parent,  # equivalent to .../uom.json
                                            CREDENTIAL_FILE_NAME))

        # if credential exists in project directory
        if credential_path.exists():
            self.log('Reading credential from json')
            with open(credential_path) as f:
                credential = json.load(f)

        # read and save credential from user input
        else:
            credential = dict()
            credential['username'] = input("What's your UoM username: ")
            credential['password'] = input("Then, what's your password: ")
            with open(credential_path, 'w') as f:
                json.dump(credential, f)
                self.log("Credential saved to {}".format(credential_path))

        # return username and password
        return credential['username'], credential['password']

    def parse(self, response):
       return
        
    def open_timetable(self,response):
        # get url of timetable
        # TODO: this xpath expression is ugly...It's probably better to rewrite it someday.
        timetable_url = response.xpath("//div[@class='nav-collapse']/ul/li[2]/a/@href").get()
        if timetable_url is not None:
           # yield scrapy.Request(timetable_url, callback=self.parse_timetable)
            yield response.follow(timetable_url, callback=self.parse_timetable)
        else:
            raise ValueError("Invalid timetable url {}".format(timetable_url))

    def parse_timetable(self, response):
        # Extract ClassContainer selector to construct iterator
        classContainer = response.xpath("//div[@class='cssClassContainer']")
        # Match subject code and subject name
        subject_pair = self.match_name_and_info(response)

        timetable = list()

        for class_info in ClassContainerIterator(classContainer):
            # Add subject_name to class_info
            class_info['subject_name'] = subject_pair[class_info['subject_code']]
            if class_info not in timetable:
                timetable.append(class_info)

        self.log("{} class(s) information retrieved".format(len(timetable)))

    def match_name_and_info(self, response):

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
        # Stop iteration if last element in classContainer has been reached
        if self.num > len(self.classContainers):
            raise StopIteration
        else:
            subject_dict = {
                "subject_code": self.classContainers.xpath("//div[@class='cssTtableHeaderPanel']/text()").getall()[self.num].strip(),
                "class_type": self.classContainers.xpath("//span[@class='cssTtableClsSlotWhat']/text()").getall()[self.num].strip(),
                "class_time": self.classContainers.xpath("//span[@class='cssTtableClsSlotWhen']/text()").getall()[self.num].strip(),
                "class_location": self.classContainers.xpath("//span[@class='cssTtableClsSlotWhere']/text()").getall()[self.num].strip()
            }
            # go to next element
            self.num += 1
            return subject_dict