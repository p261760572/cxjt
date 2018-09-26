# coding=utf-8
from . import errors
from .exceptions import WesysException


class Expression():
    """表达式管理类
    """
    _priority = {
        "(": 9,
        ")": 9,
        "<": 8,
        "<=": 8,
        ">": 8,
        ">=": 8,
        "=": 7,
        "!=": 7,
        "and": 6,
        "or": 5
    }

    _types_name = (
        "TK_ILLEGAL",
        "TK_SPACE",
        "TK_LP",
        "TK_RP",
        "TK_EQ",
        "TK_LE",
        "TK_NE",
        "TK_LT",
        "TK_GE",
        "TK_GT",
        "TK_STRING",
        "TK_INTEGER",
        "TK_VARIABLE",
        "TK_AND",
        "TK_OR"
    )

    _TK_ILLEGAL = 0
    _TK_SPACE = 1
    _TK_LP = 2
    _TK_RP = 3
    _TK_EQ = 4
    _TK_LE = 5
    _TK_NE = 6
    _TK_LT = 7
    _TK_GE = 8
    _TK_GT = 9
    _TK_STRING = 10
    _TK_INTEGER = 11
    _TK_VARIABLE = 12
    _TK_AND = 13
    _TK_OR = 14
    _TK_BOOL = 15

    _keyword_code = {
        "and": _TK_AND,
        "or": _TK_OR
    }

    def __init__(self):
        self._cache = {}

    def _get_token(self, expr_str, expr_len, start):
        """解析token
        @param expr_str: 表达式字符串
        @param start: 解析开始下标
        @return (token长度,token类型)
        """
        i = start
        if expr_str[i].isspace():
            i = i + 1
            while i < expr_len and expr_str[i].isspace():
                i = i + 1
            return i - start, Expression._TK_SPACE
        elif expr_str[i] == "(":
            return 1, Expression._TK_LP
        elif expr_str[i] == ")":
            return 1, Expression._TK_RP
        elif expr_str[i] == "=":
            return 1, Expression._TK_EQ
        elif expr_str[i] == "<":
            if expr_str[i + 1:i + 2] == "=":
                return 2, Expression._TK_LE
            elif expr_str[i + 1:i + 2] == ">":
                return 2, Expression._TK_NE
            else:
                return 1, Expression._TK_LT
        elif expr_str[i] == ">":
            if expr_str[i + 1:i + 2] == "=":
                return 2, Expression._TK_GE
            else:
                return 1, Expression._TK_GT
        elif expr_str[i] == "!":
            if expr_str[i + 1] == "=":
                return 2, Expression._TK_NE
            else:
                return 2, Expression._TK_ILLEGAL
        elif expr_str[i] == "'":
            i = i + 1
            while i < expr_len:
                if expr_str[i] != "'":
                    i = i + 1
                elif expr_str[i:i + 2] == "''":
                    i = i + 2
                else:
                    i = i + 1
                    return i - start, Expression._TK_STRING
            return i - start, Expression._TK_ILLEGAL
        elif expr_str[i].isdigit():
            i = i + 1
            while i < expr_len and expr_str[i].isdigit():
                i = i + 1
            return i - start, Expression._TK_INTEGER
        elif expr_str[i].isalpha() or expr_str[i] == "_":
            i = i + 1
            while i < expr_len and (expr_str[i].isalnum() or expr_str[i] == "_"):
                i = i + 1
            k = expr_str[start:i]
            if k in Expression._keyword_code:
                return i - start, Expression._keyword_code[k]
            return i - start, Expression._TK_VARIABLE
        return 1, Expression._TK_ILLEGAL

    def _parse(self, expr_str):
        """解析表达式
        @param expr_str: 表达式字符串
        @return 中缀表达式
        """
        infix = []
        expr_len = len(expr_str)
        i = 0
        while i < expr_len:
            token_len, token_type = self._get_token(expr_str, expr_len, i)
            if token_type == Expression._TK_ILLEGAL:
                raise WesysException(errors.ERROR_EXPR_PARSE)

            if token_type != Expression._TK_SPACE:
                if token_type == Expression._TK_STRING:
                    # 去掉单引号
                    infix.append((expr_str[i + 1:i + token_len - 1], token_type))
                # elif token_type == Expression._TK_INTEGER:
                #                     # 转数字
                #                     infix.append((int(expr_str[i:i + token_len]), token_type))
                else:
                    infix.append((expr_str[i:i + token_len], token_type))
            i = i + token_len
        return infix

    def _to_suffix(self, infix):
        """中缀表达式转后缀表达式
        @param infix: 中缀表达式
        @return 后缀表达式
        """
        suffix = []
        stack = []
        for element in infix:
            if element[1] in (Expression._TK_STRING, Expression._TK_INTEGER, Expression._TK_VARIABLE):
                suffix.append(element)
            elif element[1] == Expression._TK_LP:
                stack.append(element)
            elif element[1] == Expression._TK_RP:
                op = stack.pop()
                while op[1] != Expression._TK_LP:
                    suffix.append(op)
                    op = stack.pop()
            else:
                while len(stack) > 0:
                    top = stack[-1]
                    if top[1] != Expression._TK_LP and Expression._priority[top[0]] >= Expression._priority[element[0]]:
                        suffix.append(stack.pop())
                    else:
                        break
                stack.append(element)
        while len(stack) > 0:
            suffix.append(stack.pop())
        return suffix


    def _to_string(self, obj):
        if obj is None:
            return ''
        return str(obj)

    def _calc_logic(self, ctx, opd, opd2, op):
        """计算两个操作数的逻辑布尔值
        @param ctx: 上下文
        @param opd: 操作数1，(值,类型)
        @param opd2: 操作数2，(值,类型)
        @param op: 操作符
        @return 计算后的布尔值，(值,布尔类型)
        """
        res = False
        opd_val = opd[0]
        opd_tp = opd[1]
        opd2_val = opd2[0]
        opd2_tp = opd2[1]
        op_tp = op[1]

        if opd_tp == Expression._TK_VARIABLE:
            opd_val = self._to_string(ctx.get(opd_val))

        if opd2_tp == Expression._TK_VARIABLE:
            opd2_val = self._to_string(ctx.get(opd2_val))

        if op_tp == Expression._TK_EQ:
            res = (opd_val == opd2_val)
        elif op_tp == Expression._TK_LE:
            res = (opd_val <= opd2_val)
        elif op_tp == Expression._TK_NE:
            res = (opd_val != opd2_val)
        elif op_tp == Expression._TK_LT:
            res = (opd_val < opd2_val)
        elif op_tp == Expression._TK_GE:
            res = (opd_val >= opd2_val)
        elif op_tp == Expression._TK_GT:
            res = (opd_val > opd2_val)
        elif op_tp == Expression._TK_AND:
            res = (opd_val and opd2_val)
        elif op_tp == Expression._TK_OR:
            res = (opd_val or opd2_val)

        return res, Expression._TK_BOOL

    def _calc(self, expr_str, ctx, suffix):
        """计算后缀表达式
        @param expr_str: 表达式字符串
        @param ctx: 上下文
        @param suffix: 后缀表达式
        @return 计算后的布尔值
        """
        stack = []
        for operand in suffix:
            operand_tp = operand[1]
            if operand_tp in (Expression._TK_STRING, Expression._TK_INTEGER, Expression._TK_VARIABLE):
                stack.append(operand)
            else:
                try:
                    opd2 = stack.pop()
                    opd = stack.pop()
                except IndexError:
                    raise WesysException(errors.ERROR_EXPR_CALC, "表达式计算错误,%s" % expr_str)
                stack.append(self._calc_logic(ctx, opd, opd2, operand))

        if len(stack) != 1:
            raise WesysException(errors.ERROR_EXPR_CALC, "表达式计算错误,%s" % expr_str)

        return stack[0][0]

    def calc(self, ctx, expr_str):
        """计算表达式
        @param ctx: 上下文
        @param expr_str: 表达式字符串
        @return 计算后的布尔值
        """
        if not expr_str in self._cache:
            infix = self._parse(expr_str)
            suffix = self._to_suffix(infix)
            self._cache[expr_str] = suffix
        else:
            suffix = self._cache.get(expr_str)

        return self._calc(expr_str, ctx, suffix)

    def test_case(self, string):
        print([(element[0], Expression._types_name[element[1]])
               for element in self._parse(string)])


def test():
    expr = Expression()

    # 正常测试
    expr.test_case("(")
    expr.test_case(")")
    expr.test_case("=")
    expr.test_case("!=")
    expr.test_case("<>")
    expr.test_case("<")
    expr.test_case("<=")
    expr.test_case(">")
    expr.test_case(">=")
    expr.test_case("and")
    expr.test_case("or")
    expr.test_case("'string'")
    expr.test_case("123456789")
    expr.test_case("_b0")
    expr.test_case("b1")

    res = expr.calc({
        'b1': 123,
        'b2': 1234
    }, "b1=123 and b2=123")
    print(res)


if __name__ == "__main__":
    test()
