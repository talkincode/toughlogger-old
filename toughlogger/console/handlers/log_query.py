#!/usr/bin/env python
# coding:utf-8

from toughlogger.console.handlers.base import BaseHandler, MenuSys
from toughlogger.common.permit import permit
from sqlalchemy.sql import text as _sql
from toughlogger.common.paginator import Paginator

###############################################################################
# log query
###############################################################################
PRIORITY = {
        "emerg": u"紧急情况(系统)", "alert": u"警报", "crit": u"严重错误", "err": u"错误",
        "warning": u"警告", "notice" :u"注意预警", "info": u"正常日志", "debug": u"调试"
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
        return self.render("log_query.html", prioritys = PRIORITY,facilitys=FACILITY)

    def post(self):
        priority = self.get_argument("priority","")
        facility = self.get_argument("facility","")
        host = self.get_argument("priority","")
        s_log_time = self.get_argument("s_log_time","")
        e_log_time = self.get_argument("e_log_time","")
        username = self.get_argument("username","")
        sort_way = self.get_argument("sort_way","")

        page_size = self.application.settings.get("page_size", 10)
        page = int(self.get_argument("page", 1))
        offset = (page - 1) * page_size



        table_names = 'table_name'

        sql = '''select * from %s where'''  %table_names[1]

        if priority:
            sql += " priority=%s" %priority
        if facility:
            sql += " facility=%s" %facility
        if host:
            sql += " host=%s" %host
        if s_log_time:
            sql += " time >= %s" %s_log_time
        if e_log_time:
            sql += " time <= %s" %e_log_time
        if username:
            sql += " username like '%%s%'" %username

        with self.db_engine.begin() as conn:
            total_cur = conn.execute(_sql('''select count(*) from log_:table_names'''),table_names=table_names)
            if self.config.database.dbtype == 'mysql':
                sql += " order by time :sort limit :offset,:size"
            if self.config.database.dbtype == 'sqlite':
                sql += " order by time :sort limit :size offset :offset"

            res_cur = conn.execute(_sql(sql),sort=sort_way,offset=offset,size=page_size)
            result = [log for log in res_cur]

        page_data = Paginator(self.get_page_url, result, total_cur[0], page_size)
        page_data.result = result

        return self.render("log_query.html", prioritys = PRIORITY,facilitys=FACILITY, **self.get_params())

permit.add_route(LogQueryHandler, r"/logQuery", u"日志查询", MenuSys, order=3.0000, is_menu=True)