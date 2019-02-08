# coding=utf-8
from flask.views import MethodView


class HelloHandler(MethodView):
    methods = ['GET']

    def get(self):
        print "hello world..."

        return "hello world..."
