# coding=utf-8
import json
from itertools import groupby

import cx_Oracle
import flask_login

from . import errors
from . import logger
from .database import get_connection
from .exceptions import WesysException
from .modules import Module


class FunCtx():
    def __init__(self, ip, url, request, op):
        """
        功能上下文
        :param ip: IP地址
        :param url: 请求的URL
        :param request: 请求数据
        :param action: 功能配置
        """
        self.ip = ip
        self.url = url
        self.request = request
        self.data = request
        self.op = op
        self.current = {
            "CurrentIp": ip,
            "CurrentAction": url,
            "CurrentUserID": flask_login.current_user.userid,
            "CurrentLoginName": flask_login.current_user.login_name,
            "CurrentInstID": flask_login.current_user.inst_id,
            "CurrentUserLevel": flask_login.current_user.user_level,
            "CurrentProvince": flask_login.current_user.province,
            "CurrentCity": flask_login.current_user.city,
            "CurrentDistrict": flask_login.current_user.district
        }

    def set(self, data):
        self.data = data

    def get(self, name):
        if name.startswith("Current"):
            return self.current.get(name)
        return self.data.get(name)


class FunManager():
    def __init__(self):
        self._cache = {}
        self._module = Module()
        self._load()

    def _load(self):
        logger.info("加载功能配置")
        conn = get_connection()
        try:
            _, rows = conn.execute("select fun_id, fun_name, url, op, log_flag from fun_info")
            for row in rows:
                self._cache[row["url"]] = row

            _, rows = conn.execute(
                "select a.url, a.module_name, a.param_list, a.exec_type, a.order_no, a.test, a.comments, a.input from fun_config a, fun_info b where a.url = b.url order by a.url, a.order_no")

            temp = [(k, list(g)) for k, g in groupby(rows, key=lambda x: x["url"])]
            for url, steps in temp:
                self._cache[url]["steps"] = [list(g) for k, g in groupby(steps, key=lambda x: x["exec_type"])]

        finally:
            conn.close()
        logger.info("加载功能配置完成")

    def reload(self):
        self._cache.clear()
        self._load()
        self._module.reload()

    def _check_function_acl(self, ctx):
        """
        检查功能权限
        :param ctx:
        :return:
        """
        # return True # 开发测试
        userid = flask_login.current_user.userid
        url = ctx.url
        if url.startswith('/action/user/'):
            return True

        if url.startswith('/action/admin/') and userid == 0:
            return True

        _, rows = ctx.conn.execute(
            "select count(1) total from view_user_fun where userid = :userid and url = :url and rownum = 1",
            [userid, url])
        if rows[0]["total"] > 0:
            return True

        return False

    def _test(self, ctx, test):
        return self._module.test_value(ctx, test)

    def _process(self, ctx, steps, request_data, response_data):
        try:
            steps_len = len(steps)
            trans = True
            for i in range(0, steps_len):
                step = steps[i]
                logger.info(step)
                module_name = step["module_name"]
                input_data = request_data

                # 跳过配置
                ctx.set(request_data)
                # if not self._test(ctx, step["test_input"]):
                #     continue

                if step["input"]:
                    input_data = request_data.get(step["input"])

                fn = self._module.get(module_name)

                if not callable(fn):
                    raise WesysException(errors.ERROR_MODULE_NOT_FOUND)

                ctx.set(input_data)
                if fn(ctx, step, input_data, response_data) != 0:
                    trans = False
                    break

        except WesysException as e:
            logger.error(e, exc_info=1)
            errors.set_errmsg(response_data, e.errcode, e.errmsg)
            trans = False
        except cx_Oracle.Error as e:
            logger.error(e, exc_info=1)

            error, = e.args
            message = error.message
            if error.code == 20999:
                message = error.message.split("\n", 1)[0][11:]
            errors.set_errmsg(response_data, errors.ERROR_DATABASE, message)
            trans = False

        # 事务回滚
        if not trans:
            ctx.conn.rollback()

        return trans

    def process(self, url, ip, session_data, request_data):
        logger.debug(url)
        logger.debug(json.dumps(request_data, ensure_ascii=False))
        response_data = {
            "errcode": 0
        }
        # 查找功能
        action = self._cache.get(url)
        if action is None:
            return errors.set_errmsg(response_data, errors.ERROR_NOT_FOUND)

        if action.get("steps") is None:
            return errors.set_errmsg(response_data, errors.ERROR_NOT_FOUND)

        # logger.info(action)
        # 创建功能上下文
        ctx = FunCtx(ip, url, request_data, action.get("op"))

        # 获取数据库连接
        ctx.conn = get_connection()
        ctx.log_flag = action.get("log_flag")

        try:
            # 检查功能权限
            if not self._check_function_acl(ctx):
                raise WesysException(errors.ERROR_PERMISSION_DENIED)

            trans = False
            for steps in action["steps"]:
                try:
                    trans = self._process(ctx, steps, request_data, response_data)
                except WesysException as e:
                    errors.set_errmsg(response_data, e.errcode, e.errmsg)

            if ctx.log_flag == '1':
                ctx.conn.execute(
                    "insert into oper_log(log_id, login_name, oper_time, login_ip, flag, remark) values (seq_log_id.nextval, :CurrentLoginName, sysdate, :CurrentLoginIp, 1, :CurrentAction)",
                    [ctx.current.get('CurrentLoginName'), ctx.current.get('CurrentIp'),
                     ctx.current.get('CurrentAction')])
            # 最后一次事务是成功的就commit
            if trans:
                ctx.conn.commit()

        except WesysException as e:
            errors.set_errmsg(response_data, e.errcode, e.errmsg)
        finally:
            if ctx.conn:
                ctx.conn.close()

        return response_data
