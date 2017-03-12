# -*- coding: UTF-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Running multiple spiders in the same process.')
    parser.add_argument('--db-uri', dest='db_uri', action='store', default='',
                        help='set sqlalchemy database uri.')
    parser.add_argument('--user-agents', dest='user_agents', action='store', default='',
                        help='set user agents file path.')
    parser.add_argument('--crawler', dest='crawler', action='append', nargs='*',
                        help='run crawler name.')
    args = parser.parse_args()

    settings = get_project_settings()
    settings.set('SQLALCHEMY_DATABASE_URI', args.db_uri)
    settings.set('USER_AGENT_FILE', args.user_agents)

    process = CrawlerProcess(settings)
    if args.crawler:
        for each_crawler in args.crawler:
            process.crawl(each_crawler)
    else:
        process.crawl('bilibili')
        process.crawl('douyu')
        process.crawl('longzhu')
        process.crawl('panda')
        process.crawl('zhanqi')
    process.start()
