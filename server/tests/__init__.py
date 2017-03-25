# -*- coding: UTF-8 -*-
from unittest import TestCase
from datetime import datetime
from flask import current_app

from app import db, create_app
from app.models import LiveTVSite, LiveTVChannel, LiveTVRoom, \
                       User, UserRoomLink


class AbstractTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = current_app if current_app else create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SESSION_PROTECTION'] = 'basic'
        db.create_all()
        cls.test_site = {
            'code': 'test_site_code',
            'name': 'test_site_name',
            'description': 'test_site_description',
            'url': 'test_site_url',
            'image': 'test_site_image',
            'show_seq': 1,
        }
        site = LiveTVSite(code=cls.test_site['code'], name=cls.test_site['name'],
                          description=cls.test_site['description'], url=cls.test_site['url'],
                          image=cls.test_site['image'], show_seq=cls.test_site['show_seq'])
        db.session.add(site)
        db.session.commit()
        cls.test_site['id'] = site.id
        cls.test_channel = {
            'office_id': 'test_channel_office',
            'short': 'test_short',
            'name': 'test_channel_name',
            'url': 'test_channel_url',
            'image': 'test_channel_image',
            'total': 1,
            'crawl_date': datetime.utcnow()
        }
        channel = LiveTVChannel(office_id=cls.test_channel['office_id'], short=cls.test_channel['short'],
                                name=cls.test_channel['name'], url=cls.test_channel['url'],
                                image=cls.test_channel['image'], total=cls.test_channel['total'],
                                crawl_date=cls.test_channel['crawl_date'], site=site)
        db.session.add(channel)
        db.session.commit()
        cls.test_channel['id'] = channel.id
        cls.test_room = {
            'office_id': 'test_room_office',
            'name': 'test_room_name',
            'url': 'test_room_url',
            'image': 'test_room_image',
            'host': 'test_room_host',
            'online': 1000,
            'crawl_date': datetime.utcnow()
        }
        room = LiveTVRoom(office_id=cls.test_room['office_id'], name=cls.test_room['name'],
                          url=cls.test_room['url'], image=cls.test_room['image'],
                          host=cls.test_room['host'], online=cls.test_room['online'],
                          crawl_date=cls.test_room['crawl_date'], channel=channel, site=site)
        db.session.add(room)
        db.session.commit()
        cls.test_room['id'] = room.id
        cls.user = User(symbol='test_symbol', office_id='test_user_office',
                        username='test_username', nickname='test_nickname',
                        email='test_user_email', url='test_user_url', image='test_user_image',
                        description='test_user_description')
        db.session.add(cls.user)
        db.session.commit()
        db.session.add(UserRoomLink(room_id=room.id, user_id=cls.user.id))
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.request_context.pop()
