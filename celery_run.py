#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery
from app.crawler import config

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@celery.task(bind=True)
def crawl_timed_task(self, site_name):
    ''' 扫描定时任务 '''
    with app.app_context():
        try:
            crawlerclass = config.get(site_name)
            if crawlerclass:
                crawlerinstance = crawlerclass()
                crawlerinstance.channels()
                crawlerinstance.rooms()
        except Exception as e:
            raise self.retry(exc=e)
