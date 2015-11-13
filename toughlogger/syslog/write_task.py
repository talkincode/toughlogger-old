#!/usr/bin/env python
# coding=utf-8
import sys
from twisted.python import log
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
        self.msg_num = 0
        self.sum_time = time.time()

    def process(self):
        # log.msg("fetch queue  message")
        job = self.beanstalk.reserve()
        msg_dict = json.loads(job.body)

        _date = datetime.datetime.strptime(msg_dict['time'], self.date_format)
        table_name = "log_{0}".format(_date.strftime("%Y%m%d%H"))

        insert_sql = _sql("""insert into {0} (host,time,facility,priority,username,message)
        values (:host,:time,:facility,:priority,:username,:message)""".format(table_name))

        with self.dbengine.begin() as conn:
            # if self.config.defaults.debug:
            #     log.msg("start write message to db")
            try:
                conn.execute(insert_sql,
                             host=msg_dict.get("host"),
                             time=msg_dict.get("time"),
                             facility=msg_dict.get("facility"),
                             priority=msg_dict.get("priority"),
                             username=msg_dict.get("username"),
                             message=msg_dict.get("message"))
                job.delete()
                self.msg_num += 1
                # if self.config.defaults.debug:
                #     log.msg("write syslog success")
            except Exception as err:
                log.err(err, 'write syslog error')
                job.release()

        reactor.callLater(0.001, self.process, )

        ctime = time.time()
        total_time = (ctime - self.sum_time)
        if total_time >= 5:
            per_num = self.msg_num / total_time
            log.msg(
                "Total msg: %s; Time total: %s sec; Msg per second: %s;" % (self.msg_num, total_time, per_num))
            self.msg_num = 0
            self.sum_time = time.time()



def run(config):
    time.sleep(1.0)
    log.startLogging(sys.stdout)
    log.msg("start write task")
    app = WriteProc(config)
    app.process()
    reactor.run()


