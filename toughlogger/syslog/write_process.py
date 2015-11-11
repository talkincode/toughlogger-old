#!/usr/bin/env python
# coding=utf-8
import sys
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from toughlogger.common.dbengine import get_engine
from sqlalchemy.sql import text as _sql

class WriteProc:

    def __init__(self, config):
        self.dbengine = get_engine(config)
        _task = task.LoopingCall(self.process)
        _task.start(0.002)

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


if __name__ == "__main__":
    run(None)