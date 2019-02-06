# coding=utf-8
import ConfigParser
import os

from common import config
from common import constant
from common import mylog

logger = mylog.logger


class MyConfig(object):
    def __init__(self, config_file):
        try:
            self.cf = ConfigParser.ConfigParser()
            self.cf.read(config_file)
        except Exception, ex:
            logger.warn("open config file (" + config_file + ") failed:" + str(ex))
            self.cf = None

    def get(self, section, key, default=None):
        if self.cf:
            try:
                return self.cf.get(section, key)
            except Exception, ex:
                logger.error(ex, exc_info=1)
                logger.error("get conf(" + section + ":" + str(key) + ") failed, return default value:" + str(default))
                return default
        else:
            logger.warn("init config failed when get conf(" + section + ":" + str(
                key) + ") failed, return default value:" + str(default))
            return default


def get_db_conf(section):
    """
    获取数据库配置的函数

    因为没有测试机，就用同一份配置文件...
    :param section:
    :return:
    """
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if config.run_venv == constant.RUN_EVEN_PRODUCE:
        config_path = os.path.join(cur_dir, './conf/db.conf')
    else:
        config_path = os.path.join(cur_dir, './conf/db.conf')

    cf = MyConfig(config_path)
    db_host = cf.get(section, "host", 'localhost')
    db_port = int(cf.get(section, "port", '3306'))
    db_user = cf.get(section, "user", 'root')
    db_pass = cf.get(section, "password", 'password')
    db_charset = cf.get(section, "charset", 'utf8')
    db_conn_count = int(cf.get(section, "connection_count", 1))
    db_name = cf.get(section, "db", "gsnovel")
    return {'host': db_host,
            'port': db_port,
            'user': db_user,
            'password': db_pass,
            'charset': db_charset,
            'conn_count': db_conn_count,
            "db": db_name
            }


def get_redis_conf(section):
    """
    获取redis配置的函数

    因为没有测试机，就用同一份配置文件...
    :param section:
    :return:
    """
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if config.run_venv == constant.RUN_EVEN_PRODUCE:
        config_path = os.path.join(cur_dir, './conf/redis.conf')
    else:
        config_path = os.path.join(cur_dir, './conf/redis.conf')

    cf = MyConfig(config_path)
    redis_host = cf.get(section, "host", 'localhost')
    redis_port = int(cf.get(section, "port", '6379'))
    redis_dbnum = cf.get(section, "db", '0')

    return {'host': redis_host, 'port': redis_port, 'db': redis_dbnum}
