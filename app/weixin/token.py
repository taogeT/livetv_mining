# -*- coding: UTF-8 -*-
from flask import request, current_app

from . import weixin

import hashlib


@weixin.route('/')
def checksignature():
    """ 验证微信平台接入 """
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        checklist = [current_app.config['WEIXIN_TOKEN'], timestamp, nonce]
        checklist.sort()
        checkstr = hashlib.sha1(''.join(checklist).encode(encoding='utf-8')).hexdigest()
        return echostr if checkstr == signature else ''
    elif request.method == 'POST':
        return ''
    else:
        return ''
