# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pickle
from scrapy.exporters import PickleItemExporter, JsonItemExporter, JsonLinesItemExporter
from scrapy.exceptions import DropItem
from os.path import dirname, abspath, join


class JsonWriterPipeline(object):
    def __init__(self):
        self.file_name = "class.json"
        self.file_path = join(dirname(dirname(abspath(__file__))), self.file_name)
        self.file = open(self.file_path, 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
       # self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class DuplicatesPipeline(object):
    """
    DuplicatesPipeline remove duplicates by checking if the hash of the
    combination of subject code and class type has been seen.
    """
    def __init__(self):
        self.class_seen = set()

    def process_item(self, item, spider):
        combination = hash(item['subject_code'] + item['class_type'])
        if combination in self.class_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.class_seen.add(combination)
            return item

class PickleWriterPipeline(object):
    def __init__(self):
        self.file_name = "class.pickle"
        self.file_path = join(dirname(dirname(abspath(__file__))), self.file_name)
        self.file = open(self.file_path, 'wb')
        self.exporter = PickleItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
