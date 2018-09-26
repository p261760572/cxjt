# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler

import flask_login
from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import MemcachedCache

from .session import CacheSessionInterface

# 应用
app = Flask(__name__)
app.config.from_object('config')

# 缓存
cache = MemcachedCache(app.config['MEMCACHE_SERVERS'])
app.session_interface = CacheSessionInterface(cache)

# 国际化和本地化
babel = Babel(app)

# 数据库
db = SQLAlchemy(app)

# 日志
# logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=20 * 1024 * 1024, encoding='utf-8')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(process)d %(filename)s[line:%(lineno)d] %(levelname)s\n%(message)s\n'
))

loggers = [app.logger, logging.getLogger('wesys')]
for logger in loggers:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from . import views, models
