import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_NAME = 'mago-demo-api-healthcare'
    args: dict

class DevelopmentConfig(Config):
    DEBUG = True
    host = '0.0.0.0'
    port = 5002


class ProductionConfig(Config):
    DEBUG = False
    host = 'https://mago-demo-healthcare.orotcode.com/'
    port = 5002

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
