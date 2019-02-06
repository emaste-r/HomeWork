# coding:utf-8
import json
import time

from flask import jsonify
from flask import request
from flask.views import MethodView

from common import config
from common import constant
from common import errcode
from common.mylog import logger


class BaseHandler(MethodView):
    def __init__(self, expect_request_para, need_para):
        """
        # 这是每个请求的公共参数如net、version
        "common_param": {
            "client": "android_7.0",
            "cuid": "ffffffff-f5c5-8962-ffff-ffff8a0d869e",
            "did": "479f4826-472d-4913-866d-e94cfc68418c",
            "flavor": "main",
            "network": 1,
            "utc": 1524299337188,
            "version": "1.4.4"
        }

        :param expect_request_para:
        :param need_para:
        """
        super(BaseHandler, self).__init__()

        t = time.time()
        self.trace_id = self.__class__.__name__ + str(int(round(t * 1000)))
        self.request = None
        self.ret_data = {}
        self.ret_code = errcode.NO_ERROR
        self.ret_msg = "ok"
        self.ret_user_msg = None
        self.parse_from_body = True
        self.para_map = {}
        self.expected_para = expect_request_para
        self.required_para = need_para
        self.common_param = {}
        self.os = ""  # android 或者ios
        self.flavor = ""  # 渠道
        self.version = ""  # 版本

        # 默认所有的api 接口的sid都必须是正确，如果有特殊如登录，则特殊去指定
        self.sid_control_level = constant.SID_NEED_BE_CORRECT

    def _handle_request(self):
        body = {}
        if self.parse_from_body:
            try:
                body = json.loads(request.data)

                # 统一打印下请求参数
                for key, value in body.iteritems():
                    if key == "common_param":
                        self.common_param = value
                        self.os = self.common_param["device_type"]
                        self.app_version = self.common_param["app_version"]

                        self.cuid = self.common_param["cuid"]  # 游客id
                        self.user_id = self.common_param["user_id"]  # 用户id

                        # tid 游客(tourist) id
                        # rid 注册用户(registed user) id
                        self.tid = self.common_param["tid"] if "tid" in self.common_param else 0
                        self.rid = self.common_param["rid"] if "rid" in self.common_param else 0

                        # 用户类型
                        self.user_type = constant.USER_SOURCE_UNKNOWN
                        if self.tid > 0:
                            self.user_type = constant.USER_SOURCE_TOURIST
                        if self.rid > 0:
                            self.user_type = constant.USER_SOURCE_LOGIN_USER

                        # 摇摆用户变量, 要么是tid，要么是rid
                        if self.user_type == constant.USER_SOURCE_LOGIN_USER:
                            self.swing_id = self.rid
                        elif self.user_type == constant.USER_SOURCE_TOURIST:
                            self.swing_id = self.tid
                        else:
                            self.swing_id = 0

                logger.debug(body)
            except Exception, ex:
                logger.error("[%s] request.body not json str, ex: %s", self.trace_id, ex, exc_info=1)
                self.ret_code = errcode.JSON_BODY_DECODE_ERROR
                self.ret_msg = "request.body not json str"
                return False

        return self._check_sid() & self._parse_and_check_parameters()

    def _check_sid(self):
        """
        校验每一个请求的sid，后台服务，就是通过sid来控制整个app的生命账户的生命周期！！
        :return:
        """

        # 检查是否携带sid，即使不需要也要传个空字符串
        if config.debug_mode == 1:
            logger.info("调试模式开启，不检查sid!")
            return True

        try:
            sid = self.common_param["sid"]
        except KeyError, _:
            self.ret_code = errcode.SID_NOT_CARRY
            self.ret_msg = "common_param without sid..."
            logger.error("common_param without sid...")
            return False

        # 检查接口是否允许空字符串的sid，如登录、注册、忘记密码等可以允许空字符串
        if self.sid_control_level == constant.SID_CAN_BE_NULL:
            logger.info("sid can be null...")
            return True

        return True

    def _parse_and_check_parameters(self):
        """
        1、解析参数 -> self.para_map中。
        2、检验参数是否正确？是否必传的参数没有传？

        :return: True, False
        """
        body = json.loads(request.data)

        for key, default_value in self.expected_para.iteritems():
            value = body.get(key, default_value)
            if isinstance(value, unicode):
                value = value.encode("utf-8")
            self.para_map[key] = value
        if request.cookies:
            for key, default_value in self.expected_para.iteritems():
                value = request.cookies.get(key, default_value)
                if value != default_value:
                    self.para_map[key] = value

        for key in self.required_para:
            if self.para_map[key] is None:
                logger.error("request param is blank：%s" % key)
                self.ret_code = errcode.PARAM_REQUIRED_IS_BLANK
                self.ret_msg = "request param is blank"
                return False
        return True

    def _return_map(self):
        ret_map = {
            "ret": self.ret_code,
            "msg": self.ret_msg
        }
        if self.ret_data:
            ret_map["data"] = self.ret_data
        else:
            ret_map["data"] = {}
        if self.ret_user_msg:
            ret_map["user_msg"] = self.ret_user_msg
        return ret_map

    def _construct_cache_key(self):
        """
        子类可返回具体key, 过期时间
        :return: (key, expire_seconds)
        """
        return None, None

    def _process_imp(self):
        logger.critical("need implement!!")
        pass

    def _handle_return(self):
        ret_map = self._return_map()
        logger.debug("[%s ###### END] 返回值: code=%s, msg=%s", self.trace_id, ret_map['ret'], ret_map['msg'])
        return jsonify(ret_map)

    def _stat(self):
        """
        每个接口自己实现相关的统计代码
        :return:
        """
        pass

    def _version_control(self):
        """
        每个接口实现自己的版本控制
        :return:
        """
        pass

    def post(self):
        self.request = request
        logger.debug("[%s ###### START]", self.trace_id)

        ret = self._handle_request()
        if ret is False:
            return self._handle_return()

        # 在最上层处理异常
        try:
            self._version_control()
            self._process_imp()
        except Exception, ex:
            logger.error(ex, exc_info=1)
            self.ret_code = errcode.DB_OPERATION_ERROR
            self.ret_msg = "operation error"

        return self._handle_return()

    def _output_error(self, name):
        logger.error("不正确的参数：%s=%s" % (name, self.para_map[name]))
        self.ret_code = errcode.PARAMETER_ERROR
        self.ret_msg = "invalid parameter: %s" % name
