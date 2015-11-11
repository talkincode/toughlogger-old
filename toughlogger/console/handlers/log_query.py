#!/usr/bin/env python
# coding:utf-8

from toughlogger.common import utils
from toughlogger.console.handlers.base import BaseHandler, MenuSys
from toughlogger.common.permit import permit
from toughlogger.console import models
from hashlib import md5

###############################################################################
# log query
###############################################################################
PRIORITY = {
        "emerg": u"紧急情况(系统)", "alert": u"警报", "crit": u"严重错误", "err": u"错误",
        "warning": u"警告", "notice" :u"注意预警", "info": u"正常日志", "debug": u"调试"
    }

class LogQueryHandler(BaseHandler):

    def get(self):
        return self.render("log_query.html", priority = PRIORITY)

    def post(self):
        log_level = self.get_argument("log_level","")
        return self.render("log_query.html", priority = PRIORITY, **self.get_params())

permit.add_route(LogQueryHandler, r"/logQuery", u"日志查询", MenuSys, order=3.0000, is_menu=True)