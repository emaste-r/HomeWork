# coding=utf-8
import os

from flask import Flask

from handlers.hello_handler import HelloHandler
from handlers.homepage.get_homepage_data_handler import GetHomepageDataHandler

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF', "docx"])

app.add_url_rule('/hello', view_func=HelloHandler.as_view("index"))

# 首页模块
app.add_url_rule('/homepage/novel/get', view_func=GetHomepageDataHandler.as_view("get_homepage_data"))

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8008, debug=True)
