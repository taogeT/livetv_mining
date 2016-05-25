#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery
from app.crawler import config

import os
import gc

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@celery.task(bind=True, default_retry_delay=10)
def crawl_task(self, site_name):
    """ 扫描定时任务 """
    try:
        with app.app_context():
            crawlerclass = config.get(site_name)
            if crawlerclass:
                crawlerinstance = crawlerclass()
                crawlerinstance.channels()
                crawlerinstance.rooms()
    except Exception as e:
        raise self.retry(exc=e)
    finally:
        gc.collect()
