#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db

import sys

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
                    print("Debugging is on. DANGER: Do not allow random users to connect to this server.", file=sys.stderr)
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


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('rungevent', GeventServer)


if __name__ == '__main__':
    manager.run()
