# -*- coding: UTF-8 -*-
from flask import url_for, session
from flask_login import login_user

from app.restful import restful_api as user_api
from app.restful.user import Verify, User
from tests import AbstractTestCase

import json


class AuthTest(AbstractTestCase):

    def test_login(self):
        login_user(self.user)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.get(user_api.url_for(Verify))
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertTrue(respjson['username'] == self.user.username)
        resp = self.client.get(user_api.url_for(User))
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertTrue(respjson['nickname'] == self.user.nickname)

    def test_logout(self):
        login_user(self.user)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.get(url_for('auth.logout'))
        self.assertTrue(resp.status_code == 302)
        with self.client.session_transaction() as client_session:
            self.assertTrue('user_id' not in client_session)
