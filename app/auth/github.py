# -*- coding: UTF-8 -*-
from flask import session, current_app, request, jsonify

from . import auth
from .. import oauth

github = oauth.remote_app(
    'github',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    app_key='GITHUB_AUTH'
)


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


@auth.route('/login/authorized/github')
def github_authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return jsonify(me.data)
