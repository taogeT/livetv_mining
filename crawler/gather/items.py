# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ChannelItem(Item):
    office_id = Field()
    short = Field()
    name = Field()
    image = Field()
    url = Field()


class RoomItem(Item):
    office_id = Field()
    name = Field()
    image = Field()
    url = Field()
    online = Field()
    host = Field()
    channel = Field()
    followers = Field()
    description = Field()
    announcement = Field()
    start_time = Field()


class DailyItem(Item):
    site_id = Field()
    room_id = Field()
    summary_date = Field()
    online = Field()
    followers = Field()
    description = Field()
    announcement = Field()
    fallback = Field()


class OnceItem(Item):
    room_url = Field()
    channel_name = Field()
    host = Field()
    followers = Field()
    start_time = Field()
    donate = Field()
    description = Field()
    announcement = Field()
