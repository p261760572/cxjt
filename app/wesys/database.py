# coding=utf-8
import datetime

from decimal import Decimal

from app import db
from app.wesys import parser
from ..wesys import logger
# from .sql import generate_print_sql


class Connection():
    def __init__(self, conn):
        self._conn = conn

    def close(self):
        # self._conn.close()
        # session的connection不要关闭
        pass

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def makedict(self, cursor):
        cols = [d[0].lower() for d in cursor.description]

        def createrow(*args):
            values = []
            for v in args:
                # 解决日期类型的序列化问题
                if isinstance(v, datetime.datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(v, Decimal):
                    v = float(v)
                values.append(v)
            return dict(zip(cols, values))

        return createrow

    def execute(self, statement, parameters=[], limit=0):
        logger.info(parser.generate_print_sql(statement, parameters))
        cur = self._conn.cursor()
        try:
            cur.execute(statement, parameters)
            rows = None
            if cur.description is not None:
                cur.rowfactory = self.makedict(cur)
                if limit == 0:
                    rows = cur.fetchall()
                else:
                    rows = cur.fetchmany(limit)
        finally:
            cur.close()

        return cur.rowcount, rows

    def cursor(self):
        return self._conn.cursor()


def get_connection():
    # dbapi_conn = db.engine.raw_connection()

    # 取session里的connection
    connection = db.session.connection()
    dbapi_conn = connection.connection

    return Connection(dbapi_conn)
