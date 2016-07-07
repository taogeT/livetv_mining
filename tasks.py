#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from .. import celery
from .instance import LiveTVCrawler


@celery.task(bind=True, default_retry_delay=10)
def crawl_task(self, site_code):
    """ 扫描定时任务 """
    try:
        crawler = LiveTVCrawler(site_code)
        crawler.crawl_task()
    except ValueError as e:
        raise self.retry(exc=e)
