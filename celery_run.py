#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery
from app.crawler import LiveTVCrawler

import os
import gc

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@celery.task
def crawl_timed_task(site_name):
    ''' 扫描定时任务 '''
    with app.app_context():
        crawler = LiveTVCrawler(name=site_name)
        # 频道扫描
        crawler.channel()
        # 房间扫描
        crawler.room()
    # 回收资源
    gc.collect()

