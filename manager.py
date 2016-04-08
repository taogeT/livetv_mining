#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import LiveTVSite
from app.crawler import LiveTVCrawler

import os
import sys

app = create_app(os.environ.get('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, LiveTVSite=LiveTVSite, LiveTVCrawler=LiveTVCrawler)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def crawl(site=None, type=None, channel=None):
    """ Crawl LiveTV URL."""
    if not type:
        print('At Least Input Crawl Type: --crawl channel/room')
        sys.exit(1)
    crawler = LiveTVCrawler(name=site) if site else LiveTVCrawler()
    if type == 'channel':
        print('Start Crawl Site Channel...')
        crawler.channel()
    elif type == 'room':
        print('Start Crawl Site Room...')
        crawler.room(channel_url=channel)


if __name__ == '__main__':
    manager.run()
