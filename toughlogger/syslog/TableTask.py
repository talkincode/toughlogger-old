#!/usr/bin/env python
# coding=utf-8

import sys
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from toughlogger.common.dbengine import get_engine
from sqlalchemy.sql import text as _sql

cteate_sql_tpl = """
CREATE TABLE log_%s (
	id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	host VARCHAR(32) NOT NULL,
	time VARCHAR(19) NOT NULL,
	facility VARCHAR(16) NOT NULL,
	priority VARCHAR(16) NOT NULL,
	message VARCHAR(512) NOT NULL,
	PRIMARY KEY (id)
)
COMMENT='syslog table'
COLLATE='utf8_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=1;
"""


class WriteProc:

    def __init__(self, config):
        self.dbengine = get_engine(config)
        _task = task.LoopingCall(self.process)
        _task.start(60 * 20)

    def process(self):
        sqlstr = ''
        with self.dbengine.begin() as conn:
            try:
                results = conn.execute(_sql(sqlstr))
            except Exception as err:
                log.err(err, 'write syslog error')


def run(config):
    log.startLogging(sys.stdout)
    app = WriteProc(config)
    reactor.run()
