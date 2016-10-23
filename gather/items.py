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
    channel = Field()
