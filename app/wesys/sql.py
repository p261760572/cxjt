# coding=utf-8
import json
from io import StringIO
from json import JSONDecodeError

from app.wesys import parser
from . import errors
from .exceptions import WesysException
from .database import get_connection
from ..wesys import logger


class Sql():
    """sql管理类
    """

    def __init__(self):
        self._cache = {}
        self._rules_cache = {}
        self._load()

    def _load(self):
        logger.info('加载SQL配置')
        conn = get_connection()

        try:
            _, rows = conn.execute("select sql_id, sql_name, sql_stmt from sql_info")
            for row in rows:
                # print(row["sql_stmt"])
                try:
                    self._cache[row["sql_id"]] = json.loads(row["sql_stmt"])
                except JSONDecodeError as e:
                    logger.error("%s解析失败" % row["sql_id"], exc_info=1)

            self._rules_cache.clear()
            _, rows = conn.execute("select data_rule_id, res_code, data_rule, rule_name, op from data_rule")
            for row in rows:
                row["rules"] = json.loads(row["data_rule"])
                self._rules_cache[row["data_rule_id"]] = row

        finally:
            conn.close()
        logger.info('加载SQL配置完成')

    def reload(self):
        self._cache.clear()
        self._load()

    def gen_data_acl(self, ctx, res_code, alias):
        userid = ctx.get('CurrentUserID')
        op = ctx.op

        _, rows = ctx.conn.execute(
            "select a.role_id, b.data_rule_id from (select role_id from data_role start with role_id in (select role_id from user_data_role where userid=:userid) connect by prior role_pid = role_id) a,data_role_rule b,data_rule c where a.role_id = b.role_id and b.data_rule_id = c.data_rule_id and c.res_code = :res_code order by a.role_id,c.op desc",
            [userid, res_code])

        sqlbuf = StringIO()

        flag = False
        pre_role_id = None
        for row in rows:
            if row["role_id"] != pre_role_id:
                flag = False

            rule = self._rules_cache.get(row["data_rule_id"])
            if rule["op"] == op:
                rules = rule["rules"]
                if len(rules) > 0:
                    sqlbuf.write(" and ")
                    parser.gen_group_where(ctx, sqlbuf, rules, None, alias, False)
                flag = True
            elif not flag and rule.op == "*":
                rules = rule.rules
                if len(rules) > 0:
                    sqlbuf.write(" and ")
                    parser.gen_group_where(ctx, sqlbuf, rules, None, alias, False)
                flag = True

        return sqlbuf.getvalue()

    def generate_sql(self, ctx, sql_id):
        stmt = self._cache.get(sql_id)

        if stmt:
            sqlbuf = StringIO()
            bind = []
            ctx.data_access = self.gen_data_acl
            parser.generate_sql(ctx, stmt, sqlbuf, bind)
            sql = sqlbuf.getvalue()
            return sql, bind
        else:
            raise WesysException(errors.ERROR_SQL_CONFIG, " 未找到SQL:%s" % sql_id)
