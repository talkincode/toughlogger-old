#!/usr/bin/env python
# coding:utf-8

from toughlogger.console.handlers.base import BaseHandler, MenuStat
from toughlogger.console import models
from toughlogger.common.permit import permit
import datetime

###############################################################################
# log query
###############################################################################
PRIORITY = {
        "emerg": u"严重错误", "alert": u"警戒性错误", "crit": u"临界值错误", "err": u"一般错误",
        "warning": u"警告", "notice" :u"通知", "info": u"信息", "debug": u"调试"
    }
FACILITY = {
        "kern": u"kern", "user": u"user", "mail": u"mail", "daemon": u"daemon",
        "auth" : u"auth", "syslog": u"syslog", "lpr": u"lpr", "news": u"news",
        "uucp" : u"uucp", "cron": u"cron", "": "authpriv", "ftp": u"ftp",
        "ntp": u"ntp", "security": u"security", "console": u"console", "mark": u"mark",
        "local0": u"local0", "local1": u"local1", "local2": u"local2", "local3": u"local3",
        "local4": u"local4", "local5": u"local5", "local6": u"local6", "local7": u"local7"
    }

class LogQueryHandler(BaseHandler):

    def get(self):
        self.post()

    def post(self):
        _now = datetime.datetime.now()
        priority = self.get_argument("priority","")
        facility = self.get_argument("facility","")
        host = self.get_argument("host","")
        start_time = self.get_argument("s_log_time", _now.strftime("%Y-%m-%d %H") + ':00')
        end_time = self.get_argument("e_log_time", _now.strftime("%Y-%m-%d %H") + ':59')
        username = self.get_argument("username","")
        keyword = self.get_argument("keyword","")

        _start = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        _end = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        if (_start.year,_start.month,_start.day,_start.hour) != (_end.year, _end.month, _end.day, _end.hour):
            return self.render_error(msg=u"不支持跨小时查询")

        table_name = "log_{0}".format(_start.strftime("%Y%m%d%H"))

        logcls = models.get_logtable(table_name)

        _query = self.db.query(logcls).filter(
            logcls.time >= start_time + ':00',
            logcls.time <= end_time + ':59'
        )

        if priority:
            _query = _query.filter(logcls.priority == priority)
        if facility:
            _query = _query.filter(logcls.facility == facility)
        if host:
            _query = _query.filter(logcls.host == host)
        if username:
            _query = _query.filter(logcls.username == username)

        if keyword:
            _query = _query.filter(logcls.message.like('%' + keyword + '%'))

        _query = _query.order_by(logcls.time.desc())

        self.render("log_query.html",
                    prioritys=PRIORITY,
                    facilitys=FACILITY,
                    page_data=self.get_page_data(_query),
                    **self.get_params())


permit.add_route(LogQueryHandler, r"/log/query", u"日志查询", MenuStat, order=3.0000, is_menu=True)