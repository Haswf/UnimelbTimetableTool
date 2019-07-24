import scrapy
import os
from pathlib2 import Path
import json
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

class TimeTableSpider(scrapy.Spider):
    name = "timetable"
    start_urls = ['https://prod.ss.unimelb.edu.au/student/Login.aspx']
    def get_login_credential(self):
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
        self.log("Getting tokens for login")
        view_state = response.xpath("//div/input[@name='__VIEWSTATE']/@value").get()
        event_validation = response.xpath("//div/input[@name='__EVENTVALIDATION']/@value").get()
        view_state_generator = response.xpath("//*/div/input[@name='__VIEWSTATEGENERATOR']/@value").get()
        username, password = self.get_login_credential();
        formdata = {'__EVENTTARGET': 'ctl00$Content$cmdLogin',
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_generator,
            '__EVENTVALIDATION': event_validation,
            'ctl00$Content$txtUserName$txtText': username,
            'ctl00$Content$txtPassword$txtText': password,
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
        # open_in_browser(response)
        #for class_info in response.xpath("//div[@class=cssTtableHeaderPanel]").getall():
        class_names = response.xpath("//div[@class='cssTtableRoundBorder cssTtableSspColourBlock']")
        class_info = response.xpath("//div[@class='cssClassContainer']")

        subject_code_name = []
        subject_code_info = []

        temp_codes = []
        for temp_code in class_names.xpath(
                "//div[@class='cssTtableRoundBorder cssTtableSspColourBlock']/span/text()").getall():
            if temp_code.strip() == "":
                continue
            elif not temp_code.strip() in temp_codes:
                temp_codes.append(temp_code.strip())

        temp_names = []
        for temp_name in class_names.xpath("//td[@class='cssTtableSspNavMasterSpkInfo3']/div/text()").getall():
            if temp_name.strip() == "":
                continue
            elif not temp_name.strip() in temp_names:
                temp_names.append(temp_name.strip())

        for i in range (0, len(temp_codes)):
            subject_code_name.append((temp_codes[i], temp_names[i]))

        temp_codes =[x.strip() for x in class_info.xpath("//div[@class='cssTtableHeaderPanel']/text()").getall()]
        temp_types =[x.strip() for x in class_info.xpath("//span[@class='cssTtableClsSlotWhat']/text()").getall()]
        temp_times =[x.strip() for x in class_info.xpath("//span[@class='cssTtableClsSlotWhen']/text()").getall()]
        temp_locs =[x.strip() for x in class_info.xpath("//span[@class='cssTtableClsSlotWhere']/text()").getall()]
        for i in range(0, len(temp_codes)):
            if (temp_codes[i], temp_types[i], temp_times[i], temp_locs[i]) not in subject_code_info:
                subject_code_info.append((temp_codes[i], temp_types[i], temp_times[i], temp_locs[i]))

        # merge all
        subject_code_name_info = []
        for sub_c_n in subject_code_name:
            for sub_c_i in subject_code_info:
                #  if same code
                if sub_c_n[0] == sub_c_i[0]:
                    subject_code_name_info.append((sub_c_n[0], sub_c_n[1], sub_c_i[1], sub_c_i[2], sub_c_i[3]))

        self.log("{} class info retrieved".format(len(subject_code_name_info)))

#if __name__ == "__main__":
#