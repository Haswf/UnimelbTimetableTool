# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Class(scrapy.Item):
    subject_name = scrapy.Field()
    subject_code = scrapy.Field()
    class_type = scrapy.Field()
    class_location = scrapy.Field()
    class_time = scrapy.Field()