#!/usr/bin/env python
# coding=utf-8

import re
from datetime import datetime


class SyslogParser:

    date_ignore_pattern = None
    date_format = "%Y %b %d %H:%M:%S"
    pattern = ' '.join([
        r'<?(?P<pri>\d+)>?(?P<time>\S+ \d\d \d\d\:\d\d\:\d\d)?',
        r'(?P<host>\S+)?',
        r'(?P<process>\S+):?',
        r'(?P<message>.*)',
    ])

    user_pattern = r"\[username:([^\]]*)\]"

    def __init__(self):
        self.all_regex = re.compile(self.pattern)
        self.user_regex = re.compile(self.user_pattern)

    def parse_line(self, line):
        """Parse one line of the log file.
        """
        m = self.all_regex.search(line)
        if m:
            data = m.groupdict()
            data = self.post_process(data)
            if self.date_format:
                try:
                    data['time'] = self.convert_time(data['time'])
                except:
                    data['time'] = datetime.now()
            else:
                data['time'] = datetime.now()
            data['time'] = data['time'].strftime("%Y-%m-%d %H:%M:%S")
            return data
        else:
            return {}

    def convert_time(self, time_str):
        """Convert date string to datetime object
        """
        if self.date_ignore_pattern:
            time_str = re.sub(self.date_ignore_pattern, '', time_str)
        return datetime.strptime(time_str, self.date_format)


    def post_process(self, data):
        data['time'] = '%d %s' % (datetime.now().year, data['time'])
        m = self.user_regex.search(data['message'])
        if m:
            data['username'] = m.group(1)
        else:
            data['username'] = ''
        return data


slog_parser = SyslogParser()


class SyslogProtocol:

    PRIORITY = {
        0: "emerg", 1: "alert", 2: "crit", 3: "err",
        4: "warning", 5: "notice", 6: "info", 7: "debug"
    }

    PRIORITY_REVERSE = {
        "emerg"  : 0, "alert": 1, "crit": 2, "err": 3,
        "warning": 4, "notice": 5, "info": 6, "debug": 7
    }

    FACILITY = {
        0 : "kern", 1: "user", 2: "mail", 3: "daemon",
        4 : "auth", 5: "syslog", 6: "lpr", 7: "news",
        8 : "uucp", 9: "cron", 10: "authpriv", 11: "ftp",
        12: "ntp", 13: "security", 14: "console", 15: "mark",
        16: "local0", 17: "local1", 18: "local2", 19: "local3",
        20: "local4", 21: "local5", 22: "local6", 23: "local7"
    }

    @classmethod
    def facility(cls, number):
        try:
            return cls.FACILITY[number >> 3]
        except:
            return "unknown"

    @classmethod
    def priority(cls, number):
        try:
            return cls.PRIORITY[number & 0x07]
        except:
            return "unknown"

    @classmethod
    def decode(cls, data):
        res = []
        for chunk in data.split("\n"):
            if not chunk or len(chunk) < 5:
                continue

            msg = slog_parser.parse_line(chunk)
            if msg:
                msg['facility'] = SyslogProtocol.facility(int(msg['pri']))
                msg['priority'] = SyslogProtocol.priority(int(msg['pri']))
                res.append(msg)
        return res

    @classmethod
    def encode(cls, facility, priority, message):
        return "<%d>%s" % ((facility << 3) + priority, message)


if __name__ == "__main__":

    msg = """
<14>Nov 11 11:41:01 qingyun dhclient[470]: DHCPACK [username:abc] from 192.168.100.1 (xid=0x3d25774e)
<14>Nov 11 14:22:29 wjt.local toughengine: INFO    [username:www]  radiusd [Radiusd] :::::::  Send radius response: AccessAccept host=192.168.31.79:61498,id=106,Reply-Message="""
    parser = SyslogParser()
    for line in msg.split("\n"):
        print parser.parse_line(line)
        print