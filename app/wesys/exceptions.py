# coding=utf-8
from .errors import get_errmsg


def _to_string(obj):
    if obj is None:
        return ''
    return str(obj)

class WesysException(Exception):
    """wesys错误异常"""

    def __init__(self, errcode, errmsg=None):
        """
        @param errcode: 错误代码
        @param errmsg: 错误信息
        """
        self.errcode = errcode
        self.errmsg = get_errmsg(errcode) + _to_string(errmsg)
