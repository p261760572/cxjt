# coding=utf-8

ERROR_SYSTEM = -1
ERROR_NOT_FOUND = 2
ERROR_MODULE_NOT_FOUND = 3
ERROR_PERMISSION_DENIED = 4
ERROR_INVALID_SESSION = 5
ERROR_MODULE_CONFIG_ERROR = 6
ERROR_MODULE_PARAM_ERROR = 7
ERROR_EXPR_PARSE = 8
ERROR_EXPR_CALC = 9
ERROR_DATABASE = 10
ERROR_SQL_CONFIG = 11
ERROR_NO_DATA_FOUND = 12
ERROR_DATA_ACCESS = 13
ERROR_GATEWAY = 14

_table = (
    (ERROR_SYSTEM, "系统错误"),
    (ERROR_NOT_FOUND, "未找到功能"),
    (ERROR_MODULE_NOT_FOUND, "未找到功能模块"),
    (ERROR_PERMISSION_DENIED, "没有权限"),
    (ERROR_INVALID_SESSION, "无效会话"),
    (ERROR_MODULE_CONFIG_ERROR, "模块配置错误"),
    (ERROR_MODULE_PARAM_ERROR, "模块参数错误"),
    (ERROR_EXPR_PARSE, "表达式解析失败"),
    (ERROR_EXPR_CALC, "表达式计算错误"),
    (ERROR_DATABASE, "数据库操作失败"),
    (ERROR_SQL_CONFIG, "SQL配置错误"),
    (ERROR_NO_DATA_FOUND, "未找到数据"),
    (ERROR_DATA_ACCESS, "您没有权限访问所需的数据"),
    (ERROR_GATEWAY, "网关调用失败"),
)


def get_errmsg(errcode):
    """"获取错误代码的描述信息"""
    for _errcode, _errmsg in _table:
        if _errcode == errcode:
            return _errmsg

    return None


def set_errmsg(data, errcode, errmsg=None):
    """错误处理"""
    data["errcode"] = errcode
    data["errmsg"] = errmsg or get_errmsg(errcode)
    return data
