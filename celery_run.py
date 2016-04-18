#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery
from app.crawler import config
from app.models import LiveTVSite, LiveTVChannel

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@celery.task(bind=True, default_retry_delay=10)
def crawl_channels_task(self, site_name):
    ''' 扫描定时任务 '''
    with app.app_context():
        try:
            crawlerclass = config.get(site_name)
            if crawlerclass:
                crawlerinstance = crawlerclass()
                crawlerinstance.channels()
        except Exception as e:
            raise self.retry(exc=e)


@celery.task(bind=True, default_retry_delay=10)
def crawl_rooms_task(self, site_name, offset_num=0):
    ''' 扫描定时任务 '''
    with app.app_context():
        try:
            crawlerclass = config.get(site_name)
            offset_index = 0
            if crawlerclass:
                crawlerinstance = crawlerclass()
                site = LiveTVSite.query.filter_by(name=site_name).one_or_none()
                if site:
                    for channel_index, channel in enumerate(site.channels.order_by(LiveTVChannel.officeid.asc()).offset(offset_num)):
                        offset_index = channel_index
                        crawlerinstance.rooms(channel_url=channel.url)
        except Exception as e:
            raise self.retry(exc=e, kwargs={'site_name': site_name, 'offset_num': offset_index})
