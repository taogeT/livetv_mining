# -*- coding: UTF-8 -*-
from flask import session, redirect, request
from flask_login import login_user

from .. import oauth, db
from . import auth
from ..models import User

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


@auth.route('/authorized/github')
def github_authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    userjson = github.get('user').data
    user = User.query.filter_by(office_id=str(userjson['id']), symbol='github').one_or_none()
    if not user:
        user = User(office_id=userjson['id'], username=userjson['login'], url=userjson['url'], symbol='github')
    user.nickname = userjson['name']
    user.email = userjson['email']
    user.image = userjson['avatar_url']
    user.description = userjson['bio']
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(request.args.get('next') or '/')
