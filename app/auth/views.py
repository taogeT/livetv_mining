# -*- coding: UTF-8 -*-
from flask import render_template, current_app, url_for, g, session, redirect
from datetime import datetime, timedelta

from .. import db
from . import auth
from .models import User
from .github import github


@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/login/<string:authtype>')
def login_authorize(authtype):
    return github.authorize(callback=url_for('auth.{}_authorized'.format(authtype), _external=True))


@auth.before_app_request
def before_request():
    if 'token_authtype' in session:
        token_name = '{}_token'.format(session['token_authtype'])
        user = User.query.filter_by(symbol=session['token_authtype'], session_value=session[token_name]).one_or_none()
        if user:
            currtime = datetime.utcnow()
            if user.last_seen + timedelta(minutes=current_app.config['USER_VALID_MINS']) > currtime:
                user.last_seen = currtime
                db.session.add(user)
                db.session.commit()
                g.user = user


@auth.route('/logout')
def logout():
    token_authtype = session.pop('token_authtype', '')
    if token_authtype:
        session.pop('{}_token'.format(token_authtype), '')
    return redirect(url_for('index'))
