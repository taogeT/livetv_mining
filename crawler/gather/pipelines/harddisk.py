# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

from ..items import OnceItem

import csv


class HardDiskPipeline(object):

    def open_spider(self, spider):
        self.utc_date = datetime.utcnow()
        self.once_csvfile = None
        self.once_csvwriter = None

    def close_spider(self, spider):
        if self.once_csvfile:
            self.once_csvfile.close()

    def process_item(self, item, spider):
        if isinstance(item, OnceItem):
            if not self.once_csvfile:
                self.once_csvfile = open(spider.name + '-' + self.utc_date.strftime('%Y%m%d') + '.csv', 'w')
                self.once_csvwriter = csv.writer(self.once_csvfile)
            self.once_csvwriter.writerow((item['room_url'], item['channel_name'], item['host'], item['followers'],
                                          item['start_time'], item['donate'], item['announcement'],
                                          item['description']))
        return item
