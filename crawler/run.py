# -*- coding: UTF-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Running multiple spiders in the same process.')
    parser.add_argument('--db-uri', dest='db_uri', action='store', default='',
                        help='set sqlalchemy database uri.')
    parser.add_argument('--user-agents', dest='user_agents', action='store', default=None,
                        help='set user agents file path.')
    parser.add_argument('--log-file', dest='log_file', action='store', default=None,
                        help='set log file path.')
    parser.add_argument('--log-level', dest='log_level', action='store', default=None,
                        help='set log level.')
    parser.add_argument('--crawler', dest='crawler', action='append', help='run crawler name.')
    parser.add_argument('--daily', dest='daily', action= 'store_true', default=False, help='run daily crawler.')
    args = parser.parse_args()

    settings = get_project_settings()
    if args.db_uri:
        settings.set('SQLALCHEMY_DATABASE_URI', args.db_uri)
    if args.user_agents:
        settings.set('USER_AGENT_FILE', args.user_agents)
    if args.log_file:
        settings.set('LOG_FILE', args.log_file)
    if args.log_level:
        settings.set('LOG_LEVEL', args.log_level)

    process = CrawlerProcess(settings)
    if args.crawler:
        for each_crawler in args.crawler:
            process.crawl(each_crawler)
    elif args.daily:
        process.crawl('douyu_daily')
        process.crawl('panda_daily')
        process.crawl('quanmin_daily')
        process.crawl('bilibili_daily')
    else:
        settings.set('CLOSESPIDER_TIMEOUT', 1000)
        process.crawl('bilibili')
        process.crawl('douyu')
        process.crawl('longzhu')
        process.crawl('panda')
        process.crawl('zhanqi')
        process.crawl('huya')
        process.crawl('quanmin')
        process.crawl('huomao')
    process.start()
