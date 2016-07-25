# -*- coding: UTF-8 -*-
from flask import render_template, request, jsonify, current_app
from markdown import markdown
from gevent.subprocess import Popen

import hmac
import hashlib
import codecs


def about():
    """ 关于 """
    with codecs.open('README.md', 'r', encoding='utf-8') as mdf:
        mdhtml = markdown(mdf.read())
    return render_template('about.html', mdhtml=mdhtml)


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
