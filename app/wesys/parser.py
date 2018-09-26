# coding=utf-8
# import StringIO
from io import StringIO

from app.wesys import errors
from app.wesys.exceptions import WesysException
from app.wesys.exp import Expression

_expr = Expression()

_types_name = ("_TK_ILLEGAL", "_TK_OTHER", "_TK_STRING", "_TK_BIND_VAR", "_TK_REPLACE")

_TK_ILLEGAL = 0
_TK_OTHER = 1
_TK_STRING = 2
_TK_BIND_VAR = 3
_TK_REPLACE = 4


def _to_string(obj):
    if obj is None:
        return ''
    return str(obj)


def _get_token(sql, sql_len, start):
    i = start

    if sql[i] == "'":
        i += 1
        while i < sql_len:
            if sql[i] != "'":
                i += 1
            elif sql[i:i + 2] == "''":
                i += 2
            else:
                i += 1  # if sql[i] == "'"
                return i - start, _TK_STRING
        return i - start, _TK_ILLEGAL
    elif sql[i] == ":":
        i += 1
        while i < sql_len and (sql[i].isalnum() or sql[i] == "_"):
            i += 1
        token_len = i - start
        if token_len > 1:
            return token_len, _TK_BIND_VAR
        return token_len, _TK_ILLEGAL
    elif sql[i] == "$":
        i += 1
        if sql[i:i + 1] == "{":
            while i < sql_len and sql[i] != "}":
                i += 1
            token_len = i - start + 1
            if i < sql_len and token_len > 3:
                return i - start + 1, _TK_REPLACE
        return i - start, _TK_ILLEGAL
    else:
        while i < sql_len and sql[i] not in ("'", ":", "$"):
            i += 1
        return i - start, _TK_OTHER


_tags = {
    "for": True
}


def _parse_data_access(ctx, sql, res_alias, sqlbuf, bind):
    sql_len = len(sql)
    i = 0
    while i < sql_len:
        token_len, token_type = _get_token(sql, sql_len, i)
        if token_type == _TK_ILLEGAL:
            raise WesysException(errors.ERROR_SQL_CONFIG, ",解析SQL出错:%s" % sql)

        token = sql[i:i + token_len]
        if token_type == _TK_REPLACE:
            values = token[2:-1].split(",", 2)
            res_code = values[0]
            if res_code == "T":
                sqlbuf.write(res_alias)
            else:
                raise WesysException(errors.ERROR_SQL_CONFIG, ",解析SQL出错:%s" % sql)
        elif token_type == _TK_BIND_VAR:
            name = token[1:]
            sqlbuf.write(":b" + str(len(bind)))
            bind.append(ctx.get(name))
        else:
            sqlbuf.write(token)

        i = i + token_len


def parse(ctx, sql, sqlbuf, bind):
    sql_len = len(sql)
    i = 0
    while i < sql_len:
        token_len, token_type = _get_token(sql, sql_len, i)
        if token_type == _TK_ILLEGAL:
            raise WesysException(errors.ERROR_SQL_CONFIG, ",解析SQL出错:%s" % sql)

        token = sql[i:i + token_len]
        if token_type == _TK_REPLACE:
            values = token[2:-1].split(",", 2)
            res_code = values[0]
            alias = values[1] if len(values) > 1 else "a"
            psql = ctx.data_access(ctx, res_code, alias)
            _parse_data_access(ctx, psql, alias, sqlbuf, bind)
        elif token_type == _TK_BIND_VAR:
            name = token[1:]
            sqlbuf.write(":b" + str(len(bind)))
            bind.append(ctx.get(name))
        else:
            sqlbuf.write(token)

        i = i + token_len


def for_tag(ctx, stmt, item, sqlbuf, bind):
    v = ctx.get(item)
    if v:
        parse(ctx, stmt[0], sqlbuf, bind)

        insql = ""
        if isinstance(v, list):
            for i in v:
                insql += ",:" + item
                bind.append(i)
        else:
            insql += ",:" + item
            bind.append(v)
        sqlbuf.write(insql[1:])

        parse(ctx, stmt[1], sqlbuf, bind)


def generate_sql(ctx, stmt, sqlbuf, bind):
    """
    生成SQL
    :param ctx:
    :param stmt:
    :param sqlbuf:
    :param bind:
    :return:
    """
    for value in stmt:
        if isinstance(value, str):
            parse(ctx, value, sqlbuf, bind)
        elif isinstance(value, dict):
            test_value = True
            test = value.get("test")
            if test:
                test_value = _expr.calc(ctx, test)
            if test_value:
                has_tag = False
                for tag in _tags:
                    tag_value = value.get(tag)
                    if tag_value:
                        if tag == 'for':
                            for_tag(ctx, value.get("sql"), tag_value, sqlbuf, bind)
                            has_tag = True
                            break
                if not has_tag:
                    generate_sql(ctx, value.get("sql"), sqlbuf, bind)
        else:
            raise WesysException(errors.ERROR_SQL_CONFIG, ',不支持的类型:%s' % str(type(value)))


def gen_rule_where(ctx, sqlbuf, rule, alias, lo_flag):
    """
    生成数据规则的条件SQL
    :param ctx:
    :param sqlbuf:
    :param rule:
    :param alias:
    :param lo_flag:
    :return:
    """
    field = rule.get("field")
    op = rule.get("op")
    value = rule.get("value")
    lo = rule.get("lo")

    if alias is None:
        alias = ""
    else:
        alias = alias + "."

    if op == "in":
        sqlbuf.write("%s%s %s (%s)" % (alias, field, op, value))
    elif op == "like":
        sqlbuf.write("%s%s %s '%%'||'%s'||'%%'" % (alias, field, op, value))
    elif op in ("exists", "not exists"):
        sqlbuf.write("%s (%s)" % (op, value))
    else:
        sqlbuf.write("%s%s %s %s" % (alias, field, op, value))

    if lo_flag:
        sqlbuf.write(" %s " % (lo))


def gen_group_where(ctx, sqlbuf, rules, lo, alias, lo_flag):
    """
    生成数据规则组的条件SQL
    :param ctx:
    :param sqlbuf:
    :param rules:
    :param lo:
    :param alias:
    :param lo_flag:
    :return:
    """
    not_last = True
    rules_len = len(rules)

    sqlbuf.write("(")

    for i in range(0, rules_len):
        if i == rules_len - 1:
            not_last = False

        rule = rules[i]

        tag = rule.get("tag")
        if tag is None or tag == "rule":
            gen_rule_where(ctx, sqlbuf, rule, alias, not_last)
        elif tag == "group":
            group_rules = rule.get("rules")
            group_lo = rule.get("lo")
            gen_group_where(ctx, sqlbuf, group_rules, group_lo, alias, not_last)

    sqlbuf.write(")")

    if lo_flag:
        sqlbuf.append(" %s " % lo)


def generate_print_sql(sql, bind):
    """
    生成打印SQL
    :param sql:
    :param bind:
    :return:
    """
    sqlbuf = StringIO()
    count = 0
    sql_len = len(sql)
    i = 0
    while i < sql_len:
        token_len, token_type = _get_token(sql, sql_len, i)
        if token_type == _TK_ILLEGAL:
            raise WesysException(errors.ERROR_SQL_CONFIG, ",解析SQL出错:%s" % sql)

        token = sql[i:i + token_len]
        if token_type == _TK_BIND_VAR:
            name = token[1:]
            sqlbuf.write("'")
            sqlbuf.write(_to_string(bind[count]))
            sqlbuf.write("'")
            count += 1
        else:
            sqlbuf.write(token)

        i = i + token_len

    return sqlbuf.getvalue()
