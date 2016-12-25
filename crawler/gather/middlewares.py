# -*-coding:utf-8-*-
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

import random


class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent='Scrapy', user_agent_list=None):
        super(RandomUserAgentMiddleware, self).__init__(user_agent=user_agent)
        self.user_agent_list = user_agent_list

    @classmethod
    def from_crawler(cls, crawler):
        user_agent_list = crawler.settings.get('USER_AGENT_LIST', None)
        if not user_agent_list:
            user_agent_file = crawler.settings.get('USER_AGENT_FILE', None)
            if user_agent_file:
                with open(user_agent_file) as fr:
                    user_agent_list = fr.readlines()
        o = cls(crawler.settings['USER_AGENT'], user_agent_list)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_request(self, request, spider):
        if isinstance(self.user_agent_list, tuple) and len(self.user_agent_list) > 0:
            user_agent = random.choice(self.user_agent_list)
        else:
            user_agent = self.user_agent
        request.headers.setdefault(b'User-Agent', user_agent)
