# -*- coding: UTF-8 -*-
from flask import request, current_app

from . import weixin

import hashlib


@weixin.route('/')
def checksignature():
    """ 验证微信平台接入 """
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    checklist = [current_app.config['WEIXIN_TOKEN'], timestamp, nonce]
    checklist.sort()
    checkstr = ''.join(checklist).encode(encoding='utf-8')
    checkstr = hashlib.sha1(checkstr).hexdigest()
    return echostr if checkstr == signature else ''
