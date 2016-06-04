# -*- coding: UTF-8 -*-


class Config(object):
    SECRET_KEY = ''
    CELERY_BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
    CELERY_SUPERVISOR_LOGFILE = ''
    SQLALCHEMY_DATABASE_URI = ''

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 10
    FLASKY_CHANNELS_PER_PAGE = 20
    FLASKY_ROOMS_PER_PAGE = 20
    FLASKY_SEARCH_PER_PAGE = 30
    CELERY_TIMEZONE = 'UTC'
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    CELERY_SEND_TASK_ERROR_EMAILS = True
    CELERY_ADMINS = [('taogeT', 'zwtzjd@gmail.com')]
    CELERY_SUPERVISOR_ROWCOUNT = 80

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        # set production log to file
        from logging import FileHandler, Formatter
        import logging
        filehd = FileHandler('var/logs/production.log')
        fileformat = Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        filehd.setFormatter(fileformat)
        filehd.setLevel(logging.INFO)
        app.logger.addHandler(filehd)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
