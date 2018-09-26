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

ERROR_MISSING_TOKEN = 1001
ERROR_MISSING_SERVICE = 1002
ERROR_MISSING_SERVERID = 1003
ERROR_MISSING_FILE = 1004
ERROR_MISSING_FILENAME = 1005
ERROR_MISSING_REFERRAL_ID = 1006

ERROR_INVALID_VCODE = 2001
ERROR_INVALID_MOBILE_VCODE = 2002
ERROR_INVALID_TOKEN = 2003
ERROR_EXIST_MOBILE = 2004
ERROR_INVALID_REFERRAL_ID = 2005

ERROR_USER_AUTH = 3001
ERROR_PASSWORD = 3002
ERROR_INVALID_FORM_DATA = 3003
ERROR_UPLOAD_FILE = 3004

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
    (ERROR_NO_DATA_FOUND, "未来找到数据"),
    (ERROR_DATA_ACCESS, "您没有权限访问所需的数据"),
    #
    (ERROR_MISSING_TOKEN, '缺少token参数'),
    (ERROR_MISSING_SERVICE, '缺少service参数'),
    (ERROR_MISSING_SERVERID, '缺少serverid参数'),
    (ERROR_MISSING_FILE, '缺少file参数'),
    (ERROR_MISSING_FILENAME, '缺少filename参数'),
    (ERROR_MISSING_REFERRAL_ID, '缺少referral_id参数'),
    # 不合法的参数
    (ERROR_INVALID_VCODE, '无效的验证码'),
    (ERROR_INVALID_MOBILE_VCODE, '无效的短信验证码'),
    (ERROR_INVALID_TOKEN, '不合法的token'),
    (ERROR_EXIST_MOBILE, '手机号已存在'),
    (ERROR_INVALID_REFERRAL_ID, '无效的推荐码'),
    # 功能/业务
    (ERROR_USER_AUTH, '用户名或密码错误'),
    (ERROR_PASSWORD, '密码错误'),
    (ERROR_INVALID_FORM_DATA, '表单验证失败'),
    (ERROR_UPLOAD_FILE, '上传文件失败'),
)


def get_errmsg(errcode):
    """"获取错误代码的描述信息"""
    for _errcode, _errmsg in _table:
        if _errcode == errcode:
            return _errmsg

    return None


def error_handler(errcode, errmsg=None):
    """错误处理"""
    return {
        'errcode': errcode,
        'errmsg': errmsg or get_errmsg(errcode)
    }
