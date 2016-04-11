# -*- coding: UTF-8 -*-
from app import celery
from app.crawler import LiveTVCrawler

import gc


@celery.task
def crawl_timed_task(site_name):
    ''' 扫描定时任务 '''
    crawler = LiveTVCrawler(name=site_name)
    # 频道扫描
    crawler.channel()
    # 房间扫描
    crawler.room()
    # 回收资源
    gc.collect()
