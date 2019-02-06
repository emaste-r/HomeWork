# coding=utf-8
from flask import jsonify
from flask.views import MethodView

from dao.homepage.homepage_dao import HomepageDao


class GetHomepageDataHandler(MethodView):
    methods = ['POST']

    def post(self):
        items = HomepageDao.get_all()
        self.ret_code = 0
        self.ret_msg = "ok"

        ret_map = {
            "ret": self.ret_code,
            "msg": self.ret_msg,
            "list": items
        }
        return jsonify(ret_map)
