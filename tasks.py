#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from .. import celery
from . import config


@celery.task(bind=True, default_retry_delay=10)
def crawl_task(self, site_name):
    """ 扫描定时任务 """
    try:
        crawlerclass = config.get(site_name)
        if crawlerclass:
            crawlerinstance = crawlerclass()
            crawlerinstance.channels()
            crawlerinstance.rooms()
    except Exception as e:
        raise self.retry(exc=e)
