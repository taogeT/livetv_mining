# -*- coding: UTF-8 -*-
from flask import request, jsonify, current_app
from gevent.subprocess import Popen

from . import api

import hmac
import hashlib


@api.route('/github')
def github():
    """ github回调 """
    deliveryid = request.headers.get('X-GitHub-Delivery', None)
    if deliveryid:
        signature = request.headers.get('X-Hub-Signature', None)
        if not signature or signature == hmac.new(current_app.config['GITHUB_WEBHOOK_SECRET'], digestmod=hashlib.sha1).hexdigest():
            event = request.headers.get('X-GitHub-Event', '')
            if event == 'push':
                subp = Popen('git checkout .;git pull', shell=True)
                subp.wait()
    return jsonify({})
