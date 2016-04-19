# -*- coding: UTF-8 -*-
from flask import current_app, jsonify

from . import crawler

import codecs


def _log():
    rowcount = current_app.config['CELERY_SUPERVISOR_ROWCOUNT']
    crawllog = ''
    with codecs.open(current_app.config['CELERY_SUPERVISOR_LOGFILE'], 'r', encoding='utf-8') as crawllogfile:
        crawllines = crawllogfile.readlines()
        for crawllogrow in crawllines[0-rowcount:]:
            crawllog += crawllogrow
    return crawllog


@crawler.route('/api/log', methods=['GET'])
def api_log():
    return jsonify({'log': _log().encode('latin-1').decode('unicode_escape')})
