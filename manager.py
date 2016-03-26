#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import get_instance_class, LiveTVConfig, LiveTVSite

import os
import sys

cov = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    cov = coverage.coverage(branch=True, include='app/*')
    cov.start()

app = create_app(os.environ.get('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, LiveTVSite=LiveTVSite)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if cov:
        cov.stop()
        cov.save()
        print('Coverage Summary:')
        cov.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        cov.html_report(directory=covdir)
        print('HTML version: file:// % s/index.html' % covdir)
        cov.erase()


@manager.command
def scan(site=None, channel=False, room=False):
    """ Scan Douyu URL."""
    if not (channel or room):
        print('At Least Choose One Scan Mode: --channel/--room')
        sys.exit(1)
    if site:
        siteobj = LiveTVSite.query.filter_by(name=site, valid=True).one_or_none()
        if not siteobj:
            print('Site {} dose not exist'.format(site))
            sys.exit(1)
        livetv_class_tuple = get_instance_class(siteobj.name)
        if not livetv_class_tuple:
            print('Site {} Configuration dose not exist'.format(site))
            sys.exit(1)
        livetv_class_list = [(siteobj.name, siteobj.scan_url, livetv_class_tuple)]
    else:
        livetv_class_list = []
        for siteobj in LiveTVSite.query.filter_by(valid=True):
            livetv_class_tuple = LiveTVConfig.get(siteobj.name)
            if not livetv_class_tuple:
                print('Site {} Configuration dose not exist'.format(site))
                continue
            livetv_class_list.append((siteobj.name, siteobj.scan_url, livetv_class_tuple))
    for site_name, site_scan_url, livetv_class_tuple in livetv_class_list:
        livetvchannel, livetvroom = livetv_class_tuple
        if channel:
            print('Start Scan Site {} Channel...'.format(site_name))
            livetvchannel.scan_channel(site_scan_url)
        if room:
            print('Start Scan Site {} Room...'.format(site_name))
            livetvroom.scan_room(site_scan_url=site_scan_url)


@manager.command
def profile(length=25, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
