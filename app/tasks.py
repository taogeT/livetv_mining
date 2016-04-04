# -*- coding: UTF-8 -*-
from . import celery
from .crawler import LiveTVCrawler

import gc


@celery.task
def crawl_timed_task():
    ''' 扫描定时任务 '''
    crawler = LiveTVCrawler()
    # 频道扫描
    crawler.channel()
    # 房间扫描
    crawler.room()
    # 回收资源
    gc.collect()


@celery.task
def test_task(x):
    ''' 测试任务 '''
    import math
    return math.pow(x, 2)
