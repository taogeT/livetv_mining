#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.crawler import config
from app.crawler.tasks import crawl_task

import os
import sys

app = create_app(os.environ.get('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    from app.crawler.models import LiveTVSite
    return dict(app=app, db=db, LiveTVSite=LiveTVSite, crawl_task=crawl_task)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def crawl(site=None, type=None, channelurl=None, roomurl=None):
    """ Crawl LiveTV URL."""
    if not type:
        print('At Least Input Crawl Type: --type channel/room')
        sys.exit(1)
    crawlerclasslist = []
    if site:
        crawlerclass = config.get(site)
        if crawlerclass:
            crawlerclasslist.append(crawlerclass)
    else:
        crawlerclasslist.extend(config.values())
    for crawlerclass in crawlerclasslist:
        crawlerinstance = crawlerclass()
        if type == 'channel':
            print('Start Crawl Site Channel...')
            crawlerinstance.channels()
        elif type == 'room':
            print('Start Crawl Site Room...')
            if roomurl:
                crawlerinstance.single_room(room_url=roomurl)
            else:
                crawlerinstance.rooms(channel_url=channelurl)


if __name__ == '__main__':
    manager.run()
