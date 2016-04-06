# -*- coding: UTF-8 -*-
from flask import render_template, current_app, g, jsonify

from . import crawler

import codecs


def _log():
    rowcount = current_app.config['CELERY_SUPERVISOR_ROWCOUNT']
    crawllog = ''
    with codecs.open(current_app.config['CELERY_SUPERVISOR_LOGFILE'], 'r', encoding='utf-8') as crawllogfile:
        crawllines = crawllogfile.readlines()
        for crawllogrow in crawllines[0-rowcount:]:
            crawllog += crawllogrow
    return crawllog.encode('latin-1').decode('unicode_escape')


@crawler.route('/log', methods=['GET'])
def log():
    ''' 扫描日志 '''
    g.celery_interval = current_app.config['CELERY_SUPERVISOR_INTERVAL']
    return render_template('log.html', crawllog=_log())


@crawler.route('/api/log', methods=['GET'])
def api_log():
    return jsonify({'log': _log()})
