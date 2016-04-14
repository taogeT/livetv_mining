#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery
from app.crawler import LiveTVCrawler

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@celery.task(bind=True)
def crawl_timed_task(self, site_name):
    ''' 扫描定时任务 '''
    with app.app_context():
        try:
            crawler = LiveTVCrawler(name=site_name)
            # 频道扫描
            crawler.channel()
            # 房间扫描
            crawler.room()
        except Exception as e:
            raise self.retry(exc=e)
