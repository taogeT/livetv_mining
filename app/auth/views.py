# -*- coding: UTF-8 -*-
from flask import render_template, request, session, url_for, jsonify

from . import auth
from .github import github


@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/login/<string:authtype>')
def login_authorize(authtype):
    return github.authorize(callback=url_for('auth.{}_authorized'.format(authtype), _external=True))
