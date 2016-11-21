# -*- coding: UTF-8 -*-
from flask import url_for, session
from flask_login import login_user

from app.main import main_api
from app.main.apis import SiteMultiple, Site, ChannelMultiple, Channel, RoomMultiple, Room
from tests import AbstractTestCase

import json


class MainViewTest(AbstractTestCase):

    def test_room_index(self):
        resp = self.client.get(url_for('main.room_index'))
        self.assertTrue(resp.status_code == 200)

    def test_channel_index(self):
        resp = self.client.get(url_for('main.channel_index'))
        self.assertTrue(resp.status_code == 200)

    def test_site_detail(self):
        resp = self.client.get(url_for('main.site_detail', site_id=self.test_site['id']))
        self.assertTrue(resp.status_code == 200)

    def test_channel_detail(self):
        resp = self.client.get(url_for('main.channel_detail', channel_id=self.test_channel['id']))
        self.assertTrue(resp.status_code == 200)

    def test_room_detail(self):
        resp = self.client.get(url_for('main.room_detail', room_id=self.test_room['id']))
        self.assertTrue(resp.status_code == 200)

    def test_about(self):
        resp = self.client.get(url_for('about'))
        self.assertTrue(resp.status_code == 200)

    def test_search(self):
        login_user(self.user)
        resp = self.client.get(url_for('main.room_search'))
        self.assertTrue(resp.status_code == 302)
        with self.client.session_transaction() as client_session:
            client_session.update(session.items())
        resp = self.client.get(url_for('main.room_search'))
        self.assertTrue(resp.status_code == 200)


class MainApiTest(AbstractTestCase):

    def test_api_site(self):
        resp = self.client.get(main_api.url_for(SiteMultiple))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(resplist, list)
        resp = self.client.get(main_api.url_for(Site, site_id=1000))
        self.assertTrue(resp.status_code == 400)
        resp = self.client.get(main_api.url_for(Site, site_id=self.test_site['id']))
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(respjson, dict)
        self.assertEqual(resplist[0]['code'], respjson['code'])

    def test_api_channel(self):
        resp = self.client.get(main_api.url_for(ChannelMultiple, site_id=self.test_site['id'], isvue='true'))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertTrue('links' in resplist)
        resp = self.client.get(main_api.url_for(ChannelMultiple, site_id=self.test_site['id']))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(resplist, list)
        resp = self.client.get(main_api.url_for(Channel, channel_id=1000))
        self.assertTrue(resp.status_code == 400)
        resp = self.client.get(main_api.url_for(Channel, site_id=self.test_site['id'],
                                                channel_id=self.test_channel['id']))
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(respjson, dict)
        self.assertEqual(resplist[0]['office_id'], respjson['office_id'])

    def test_api_room(self):
        resp = self.client.get(main_api.url_for(RoomMultiple, site_id=1000))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertTrue(len(resplist) == 0)
        resp = self.client.get(main_api.url_for(RoomMultiple, channel_id=self.test_channel['id'], isvue='true'))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertTrue('links' in resplist)
        resp = self.client.get(main_api.url_for(RoomMultiple, site_id=self.test_site['id'],
                                                channel_id=self.test_channel['id'],
                                                name=self.test_room['name'], host=self.test_room['host']))
        self.assertTrue(resp.status_code == 200)
        resplist = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(resplist, list)
        resp = self.client.get(main_api.url_for(Room, site_id=1000, channel_id=1000, room_id=1000))
        self.assertTrue(resp.status_code == 400)
        resp = self.client.get(main_api.url_for(Room, room_id=self.test_room['id']))
        self.assertTrue(resp.status_code == 200)
        respjson = json.loads(resp.get_data(as_text=True))
        self.assertIsInstance(respjson, dict)
        self.assertEqual(resplist[0]['office_id'], respjson['office_id'])
