# -*- coding: UTF-8 -*-
from flask import session
from flask_login import login_user

from app.restful import restful_api as subscribe_api
from app.restful.subscribe import Subscribe, SubscribeModify
from tests import AbstractTestCase

import json


class SubscribeTest(AbstractTestCase):

    def test_api_subscribe(self):
        login_user(self.user)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.delete(subscribe_api.url_for(SubscribeModify, room_id=self.test_room['id']))
        self.assertTrue(resp.status_code == 200)
        subscribe_url = subscribe_api.url_for(Subscribe)
        resp = self.client.get(subscribe_url)
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertTrue(len(respjson) == 0)
        resp = self.client.post(subscribe_url,
            data={'url': self.test_room['url']},
            headers={'Accept': 'application/json'}
        )
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertTrue(respjson['office_id'] == self.test_room['office_id'])
        resp = self.client.get(subscribe_url)
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertTrue(len(respjson) == 1)
