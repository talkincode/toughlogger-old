#!/usr/bin/env python
# coding=utf-8

import sys
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from toughlogger.common.dbengine import get_engine
from sqlalchemy.sql import text as _sql
import datetime
import time

create_sql_tpl = """
CREATE TABLE {0} (
    id INTEGER NOT NULL PRIMARY KEY autoincrement,
    host VARCHAR(32) NOT NULL,
    time VARCHAR(19) NOT NULL,
    facility VARCHAR(16) NOT NULL,
    priority VARCHAR(16) NOT NULL,
    username VARCHAR(16) NULL,
    message VARCHAR(512) NOT NULL
);
"""

mysql_create_sql_tpl = """
CREATE TABLE {0} (
    id INT(11) NOT NULL PRIMARY KEY  AUTO_INCREMENT ,
    host VARCHAR(32) NOT NULL,
    time VARCHAR(19) NOT NULL,
    facility VARCHAR(16) NOT NULL,
    priority VARCHAR(16) NOT NULL,
    username VARCHAR(16) NULL,
    message VARCHAR(512) NOT NULL
)
COMMENT='syslog table'
COLLATE='utf8_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=1;
"""

class CreateTableTask:

    def __init__(self, config):
        self.sql_tpl = config.database.dbtype == 'mysql' and mysql_create_sql_tpl or create_sql_tpl
        self.dbengine = get_engine(config)
        print self.dbengine.driver
        _task = task.LoopingCall(self.process)
        _task.start(60 * 29)

    def process(self):
        table_name = "log_{0}".format((datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y%m%d%H"))
        sqlstr = self.sql_tpl.format(table_name)
        with self.dbengine.begin() as conn:
            try:
                conn.execute(_sql(sqlstr))
                log.msg("create table {0} success;".format(table_name))
            except Exception as err:
                log.msg('create table error {0}'.format(err.message))


def run(config):
    time.sleep(1.0)
    log.startLogging(sys.stdout)
    app = CreateTableTask(config)
    reactor.run()
