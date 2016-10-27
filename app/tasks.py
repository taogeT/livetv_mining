# -*- coding: UTF-8 -*-
from subprocess import Popen
from flask import current_app

from . import celery


@celery.task(bind=True, default_retry_delay=10)
def crawl_task(self, spider_name):
    """ 扫描定时任务 """
    subp = Popen('scrapy crawl -s SQLALCHEMY_DATABASE_URI={} -s USER_AGENT_FILE={} {} '.format(
        current_app.config['SQLALCHEMY_DATABASE_URI'], current_app.config['USER_AGENT_FILE'], spider_name)
    )
    subp.wait()
    if subp.poll() != 0:
        raise self.retry(exc=subp.stderr)
