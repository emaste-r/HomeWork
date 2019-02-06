# coding=utf-8
from support.novel_pool import novel_conn


class HomepageDao(object):
    @classmethod
    def get_all(cls):
        sql = "select * from gsnovel.homepage"
        items = novel_conn.fetchall(sql)
        return items
