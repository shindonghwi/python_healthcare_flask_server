import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_NAME = 'mago-demo-api-healthcare'
    args: dict


class DevelopmentConfig(Config):
    DEBUG = False
    host = '127.0.0.1'
    port = 5000


class ProductionConfig(Config):
    DEBUG = False
    host = 'https://mago-demo-healthcare.orotcode.com/'
    port = 5000


config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
