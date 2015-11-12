#!/usr/bin/env python
# coding:utf-8
import os
import ConfigParser


class ConfigDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<ConfigDict ' + dict.__repr__(self) + '>'


class Config():
    """ Config Object """

    def __init__(self, conf_file=None, **kwargs):

        cfgs = [conf_file, '/etc/toughlogger.conf']
        self.config = ConfigParser.ConfigParser()
        flag = False
        for c in cfgs:
            if c and os.path.exists(c):
                self.config.read(c)
                self.filename = c
                flag = True
                break
        if not flag:
            raise Exception("no config")

        self.defaults = ConfigDict(**{k: v for k, v in self.config.items("DEFAULT")})
        self.server = ConfigDict(**{k: v for k, v in self.config.items("server") if k not in self.defaults})
        self.syslogd = ConfigDict(**{k: v for k, v in self.config.items("syslogd") if k not in self.defaults})
        self.database = ConfigDict(**{k: v for k, v in self.config.items("database") if k not in self.defaults})

        self.defaults.debug = self.defaults.debug in ("1","true")
        self.database.echo = self.database.echo in ("1", "true")

    def update(self):
        """ update config file"""
        for k,v in self.defaults.iteritems():
            self.config.set("DEFAULT", k, v)


        for k, v in self.server.iteritems():
            if k not in self.defaults:
                self.config.set("server", k, v)

        for k, v in self.syslogd.iteritems():
            if k not in self.defaults:
                self.config.set("syslogd", k, v)

        for k, v in self.database.iteritems():
            if k not in self.defaults:
                self.config.set("database", k, v)



        with open(self.filename, 'w') as cfs:
            self.config.write(cfs)



if __name__ == "__main__":
    print Config()