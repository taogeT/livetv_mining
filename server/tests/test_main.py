# -*- coding: UTF-8 -*-
from app.restful import restful_api as main_api
from app.restful.main import SiteMultiple, Site, ChannelMultiple, Channel, RoomMultiple, Room
from tests import AbstractTestCase

import json


class MainTest(AbstractTestCase):

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
        self.assertTrue('pagination' in resplist)
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
        self.assertTrue('pagination' in resplist)
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
