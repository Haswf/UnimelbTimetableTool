# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Class(scrapy.Item):
    subject_code = scrapy.Field()
    class_type = scrapy.Field()
    location = scrapy.Field()
    time = scrapy.Field()