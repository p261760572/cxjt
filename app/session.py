# coding=utf-8

import os
from datetime import timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict


class CacheSession(CallbackDict, SessionMixin):
    """存储会话类
    """

    def __init__(self, sid, initial=None, new=False):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class CacheSessionInterface(SessionInterface):
    """缓存会话接口类
    """

    def __init__(self, cache=None, prefix='session:'):
        self.cache = cache
        self.prefix = prefix

    def generate_sid(self):
        """生成会话ID
        """
        return os.urandom(24).hex()

    def get_cache_expiration_time(self, app, session):
        """获取会话过期时间
        """
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return CacheSession(sid, new=True)

        rv = self.cache.get(self.prefix + sid)
        if rv is None:
            return CacheSession(sid, new=True)
        return CacheSession(sid, initial=rv)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if session is None:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        cookie_exp = self.get_expiration_time(app, session)
        cache_exp = self.get_cache_expiration_time(app, session)
        self.cache.set(self.prefix + session.sid, dict(session), int(cache_exp.total_seconds()))
        if session.modified:
            response.set_cookie(app.session_cookie_name, session.sid,
                                expires=cookie_exp, httponly=True,
                                domain=domain)
