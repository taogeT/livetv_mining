#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from unittest import TestLoader, TextTestRunner
from coverage import Coverage
from datetime import datetime

import os
import sys

cov = None
if os.environ.get('FLASK_COVERAGE'):
    cov = Coverage(branch=True, include=['app/*'])
    cov.start()

from app import create_app, db

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


class GeventServer(Server):

    help = description = 'Runs the Flask development gevent server.'

    def __call__(self, app, host, port, use_debugger, use_reloader, threaded, processes, passthrough_errors):
        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
                if sys.stderr.isatty():
                    print("Debugging is on. DANGER: Do not allow random users to connect to this server.",
                          file=sys.stderr)
        if use_reloader is None:
            use_reloader = app.debug

        if use_debugger:
            from werkzeug.debug import DebuggedApplication
            app = DebuggedApplication(app, True)

        def run():
            from gevent.wsgi import WSGIServer
            gws = WSGIServer((host, port), app)
            gws.base_env['wsgi.multithread'] = threaded
            gws.base_env['wsgi.multiprocess'] = processes > 0
            gws.serve_forever()

        if use_reloader:
            from werkzeug.serving import run_with_reloader
            run_with_reloader(run)
        else:
            run()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    testresult = TextTestRunner(verbosity=2).run(TestLoader().discover('tests'))
    if cov:
        cov.stop()
        cov.save()
        print('Coverage Summary:')
        cov.report()
        covdir = app.config.get('COVERAGE_DIRECTORY', '')
        if covdir:
            covdir = os.path.join(covdir, datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S'))
            if not os.path.exists(covdir):
                os.makedirs(covdir)
            cov.html_report(directory=covdir)
            print('Coverage HTML version: file://{}/index.html'.format(covdir))
        cov.erase()
    if len(testresult.failures) + len(testresult.errors) > 0:
        sys.exit(1)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('rungevent', GeventServer)


if __name__ == '__main__':
    manager.run()
