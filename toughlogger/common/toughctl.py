#!/usr/bin/env python
# coding=utf-8
from autobahn.twisted import choosereactor
choosereactor.install_optimal_reactor(False)
from toughlogger.common import config as iconfig
from toughlogger.common.dbengine import get_engine
from toughlogger.common import initdb as init_db

import argparse
import sys


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-serv', '--serv', action='store_true', default=False, dest='serv', help='run logger')
    parser.add_argument('-initdb', '--initdb', action='store_true', default=False, dest='initdb', help='run initdb')
    parser.add_argument('-port', '--port', type=int, default=0, dest='port', help='admin port')
    parser.add_argument('-debug', '--debug', action='store_true', default=False, dest='debug', help='debug option')
    parser.add_argument('-x', '--xdebug', action='store_true', default=False, dest='xdebug', help='xdebug option')
    parser.add_argument('-c', '--conf', type=str, default="/etc/toughlogger.conf", dest='conf', help='config file')
    args = parser.parse_args(sys.argv[1:])

    config = iconfig.Config(args.conf)

    if args.debug or args.xdebug:
        config.defaults.debug = True

    if args.port > 0:
        config.server.port = int(args.port)

    if args.serv:
        from toughlogger.console import logger_app
        logger_app.run(config)

    if args.initdb:
        init_db.update(get_engine(config))

