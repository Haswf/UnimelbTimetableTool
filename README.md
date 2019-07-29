# Unimelb Timetable Tool
A spider to automatically add your Melbourne university timetable to Google Calendar. New exciting features coming soon!

## How-to Guide

1. Download this repository.
2. Make sure you have `Scrapy` installed correctly in your Python3 environment. This can be done with `scarpy -v`
3. Navigate to the directory of this project`UnimelbTimetableTool` in your preferred terminal. 
4. Run `scrapy crawl timetable` to run the spider.

## Features

- [x] Log into My Unimelb timetable page
- [x] Save login credential locally
- [x] Extract class information from the page
- [x] Save class information in `JSON` format
- [x] Add class to google calendar using calendar API
  - [x] Set recurrence event
  - [ ] Label subjects with colors
  - [ ] Customize reminders 
- [ ] Update event details if your timetable has changed
- [ ] Delete events added by `UnimelbTimetableTool`