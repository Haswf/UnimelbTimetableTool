# Unimelb Timetable Tool

A python spider to automatically add your Melbourne university timetable to Google Calendar. 

![2019730000201dama.png](https://i.loli.net/2019/07/29/5d3efcac87fb623378.png)

## Quickstart

1. Download this repository.

2. Since there project is still at a very early stage of development at the moment, you need a working Google calendar API to run this script, which can be obtained at [here](https://developers.google.com/calendar/quickstart/python). Click `ENABLE THE GOOGLE CALENDAR API`, log in your google account, then save `credentials.json` to the project directory.

   ![123.png](https://i.loli.net/2019/07/29/5d3efece91c4e24939.png)

3. Make sure you have `Scrapy` installed correctly in your Python3 environment. This can be done with `scarpy -v`. A `requirements.txt` will be released shortly.

4. Run `main.py` in timetable directory. This will run spider to fetch your timetable.

5. Run `calendar_api.py` to insert class information to google account. During this process, an authorization page will pop up. Please log in the google account to where you want events to be inserted.

6. Have fun.

## Features

- [x] Log into My Unimelb timetable page
- [x] Save login credential locally
- [x] Extract class information from the page
- [x] Save class information in `JSON` format
- [x] Add class to google calendar using calendar API
- [x] Set recurrence event
- [x] Label subjects with colors
- [ ] Customize reminders 
- [x] Insert events to a separate calendar
- [ ] Update event details if your timetable has changed
- [ ] Delete events added by `UnimelbTimetableTool`
- [ ] Project-level setting file
  
## Contributor

  [Haswf](https://github.com/Haswf)

  [hanx7](https://github.com/hanx7)

  Thank you for your contribution to this project.