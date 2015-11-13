#!/usr/bin/env python
# coding=utf-8
import sys
import json
import beanstalkc
import os
import time
from twisted.internet import protocol
from syslog_protocol import SyslogProtocol
from twisted.python import log
from twisted.internet import reactor

class SyslogTCPFactory(protocol.Factory):
    noisy = 0
    numberConnections = 0
    maxNumberConnections = 1024


class SyslogTCP(protocol.Protocol):

    beanstalk = None

    msg_num = 0
    sum_time = time.time()

    def connectionMade(self):
        self.factory.numberConnections += 1
        if self.factory.numberConnections > self.factory.maxNumberConnections:
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numberConnections -= 1

    def dataReceived(self, data):
        for log_item in SyslogProtocol.decode(data):
            log_item["host"] = self.transport.getPeer().host
            self.beanstalk.put(json.dumps(log_item, ensure_ascii=False))
            self.msg_num += 1

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
    app = SyslogTCPFactory()
    app.protocol = SyslogTCP
    app.protocol.beanstalk_host = os.environ.get("BEANSTALK_HOST", config.defaults.get('beanstalk_host', 'localhost'))
    app.protocol.beanstalk_port = int(os.environ.get("BEANSTALK_PORT", config.defaults.get('beanstalk_port', 11300)))
    app.protocol.beanstalk = beanstalkc.Connection(
        host=app.protocol.beanstalk_host,
        port=app.protocol.beanstalk_port
    )
    reactor.listenTCP(int(config.syslogd.tcp_port), app, interface=config.syslogd.host)
    reactor.run()