# -*- coding: UTF-8 -*-
from flask import url_for, session
from flask_login import login_user

from tests import AbstractTestCase


class AuthTest(AbstractTestCase):

    def test_login(self):
        test_url = url_for('auth.login')
        resp = self.client.get(test_url)
        self.assertTrue(resp.status_code == 200)
        login_user(self.user)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.get(test_url)
        self.assertTrue(resp.status_code == 200)

    def test_logout(self):
        login_user(self.user)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.get(url_for('auth.logout'))
        self.assertTrue(resp.status_code == 302)
        with self.client.session_transaction() as client_session:
            self.assertTrue('user_id' not in client_session)
