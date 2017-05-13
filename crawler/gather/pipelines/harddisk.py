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
        utc_date = datetime.utcnow()
        self.csvfile = open(spider.name + '-' + utc_date.strftime('%Y%m%d') + '.csv', 'w')
        self.csvwriter = csv.writer(self.csvfile)

    def close_spider(self, spider):
        self.csvfile.close()

    def process_item(self, item, spider):
        if isinstance(item, OnceItem):
            self.csvwriter.writerow((item['room_url'], item['channel_name'], item['host'], item['followers'],
                                     item['start_time'], item['donate'], item['announcement'], item['description']))
        return item
