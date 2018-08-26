# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('BLOCKFLIX_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = True

    database = os.environ.get('MYSQL_DATABASE','blockflix')
    user = os.environ.get('MYSQL_USER','blockflix')
    password = os.environ.get('MYSQL_PASSWORD','blockflix')
    host = os.environ.get('MYSQL_HOST','blockflix')
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}/{database}'\
                              .format(user=user, password=password, host=host, database=database)
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    database = os.environ.get('MYSQL_DATABASE','blockflix_development')
    user = os.environ.get('MYSQL_USER','blockflix')
    password = os.environ.get('MYSQL_PASSWORD','blockflix')
    host = os.environ.get('MYSQL_HOST','localhost')
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}/{database}'\
                              .format(user=user, password=password, host=host, database=database)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/blockflix_test'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
