# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pickle
from scrapy.exceptions import DropItem


class JsonWriterPipeLine(object):
    """
    JsonWriterPipeLine saves class information to a json file.
    """
    def __init__(self):
        # file name where class information will be saved
        self.file_name = 'class.json'

    def open_spider(self, spider):
        self.file = open(self.file_name, 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # Write new line contains subject information to file
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
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

class PickleWriterPipeLine(object):
    """
    PickleWriterPipeLine serializes a list of Class object and save it to a pickle file.
    """
    def __init__(self):
        # file name where class information will be saved
        self.file_name = 'class.pickle'
        self.class_list = list()

    def open_spider(self, spider):
        self.file = open(self.file_name, 'w')

    def close_spider(self, spider):
        # serialize class_list and dump to file
        pickle.dump(self.class_list, self.file)
        self.file.close()

    def process_item(self, item, spider):
        # append each class to class_list
        self.class_list.append(item)
        return item

