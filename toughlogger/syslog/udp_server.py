#!/usr/bin/env python
# coding=utf-8

import time
import sys
import json
import os
import beanstalkc
from twisted.internet import protocol
from syslog_protocol import SyslogProtocol
from twisted.python import log
from twisted.internet import reactor

class SyslogUDP(protocol.DatagramProtocol):

    config = None
    beanstalk = None
    msg_num = 0
    sum_time = time.time()

    def datagramReceived(self, data, (host, port)):

        for log_item in SyslogProtocol.decode(data):
            log_item["host"] = host
            self.beanstalk.put(json.dumps(log_item, ensure_ascii=False))
            self.msg_num += 1

        if self.config.defaults.debug:
            ctime = time.time()
            total_time = (ctime - self.sum_time)
            if total_time >= 5:
                per_num = self.msg_num / total_time
                log.msg("Total msg: %s; Time total: %s sec; Msg per second: %s;" % (self.msg_num, total_time, per_num))
                self.msg_num = 0
                self.sum_time = time.time()


def run(config):
    time.sleep(1.0)
    log.startLogging(sys.stdout)
    app = SyslogUDP()
    app.config = config
    app.beanstalk_host = os.environ.get("BEANSTALK_HOST", config.defaults.get('beanstalk_host', 'localhost'))
    app.beanstalk_port = int(os.environ.get("BEANSTALK_PORT", config.defaults.get('beanstalk_port', 11300)))
    app.beanstalk = beanstalkc.Connection(
        host=app.beanstalk_host,
        port=app.beanstalk_port
    )
    reactor.listenUDP(int(config.syslogd.udp_port), app, interface=config.syslogd.host)
    reactor.run()
