#!/usr/bin/env python
# coding=utf-8
import sys
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from toughlogger.common.dbengine import get_engine
from sqlalchemy.sql import text as _sql
import datetime
import beanstalkc
import os
import json
import time

class WriteProc:

    date_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, config):
        self.config = config
        self.dbengine = get_engine(config)
        self.beanstalk_host = os.environ.get("BEANSTALK_HOST", config.defaults.get('beanstalk_host', 'localhost'))
        self.beanstalk_port = int(os.environ.get("BEANSTALK_PORT", config.defaults.get('beanstalk_port', 11300)))
        self.beanstalk = beanstalkc.Connection(
            host=self.beanstalk_host,
            port=self.beanstalk_port
        )
        self.task = task.LoopingCall(self.process)
        self.task.start(0.002)

    def process(self):
        log.msg("fetch queue  message")
        job = self.beanstalk.reserve(timeout=0.1)
        msg_dict = json.loads(job.body)

        _date = datetime.datetime.strptime(msg_dict['time'], self.date_format)
        table_name = "log_{0}".format(_date.strftime("%Y%m%d%H"))

        insert_sql = _sql("""insert into {0} (host,time,facility,priority,username,message)
        values (:host,:time,:facility,:priority,:username,:message)""".format(table_name))

        with self.dbengine.begin() as conn:
            if self.config.defaults.debug:
                log.msg("start write message to db")
            try:
                conn.execute(insert_sql,
                             host=msg_dict.get("host"),
                             time=msg_dict.get("time"),
                             facility=msg_dict.get("facility"),
                             priority=msg_dict.get("priority"),
                             username=msg_dict.get("username"),
                             message=msg_dict.get("message"))
                job.delete()
                if self.config.defaults.debug:
                    log.msg("write syslog success")
            except Exception as err:
                log.err(err, 'write syslog error')
                job.release()


    def stop(self):
        log.msg("stop write task")


def run(config):
    time.sleep(1.0)
    log.startLogging(sys.stdout)
    app = WriteProc(config)
    reactor.addSystemEventTrigger('before', 'shutdown', app.stop)
    log.msg("start write task")
    reactor.run()


