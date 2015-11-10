#!/usr/bin/env python
# coding=utf-8
import os
import txmongo
import cyclone.web
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from mako.lookup import TemplateLookup
from twisted.python import log
from twisted.internet import reactor
from toughlogger.common.permit import permit
from sqlalchemy.orm import scoped_session, sessionmaker
from toughlogger.common.dbengine import get_engine
from toughlogger.console import models
from toughlogger.console.handlers import (
    dashboard,login,logout
)
import time
import sys


###############################################################################
# web application
###############################################################################
class Application(cyclone.web.Application):
    def __init__(self, config=None,  **kwargs):
        self.config = config

        try:
            if 'TZ' not in os.environ:
                os.environ["TZ"] = config.defaults.tz
            time.tzset()
        except:
            pass


        self.rdb = scoped_session(sessionmaker(bind=get_engine(self.config), autocommit=False, autoflush=False))

        settings = dict(
            cookie_secret=os.environ.get('cookie_secret', "12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="),
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "views"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            api_secret=config.defaults.secret,
            debug=config.defaults.debug,
            rdb=self.rdb,
            xheaders=True,
        )

        self.cache = CacheManager(**parse_cache_config_options({
            'cache.type': 'file',
            'cache.data_dir': '/tmp/cache/data',
            'cache.lock_dir': '/tmp/cache/lock'
        }))

        self.tp_lookup = TemplateLookup(directories=[settings['template_path']],
                                        default_filters=['decode.utf8'],
                                        input_encoding='utf-8',
                                        output_encoding='utf-8',
                                        encoding_errors='replace',
                                        module_directory="/tmp/toughengine")

        self.init_permit()
        cyclone.web.Application.__init__(self, permit.all_handlers, **settings)

    def init_permit(self):
        conn = self.rdb()
        oprs = conn.query(models.TlOperator)
        for opr in oprs:
            if opr.operator_type > 0:
                for rule in self.rdb.query(models.TlOperatorRule).filter_by(operator_name=opr.operator_name):
                    permit.bind_opr(rule.operator_name, rule.rule_path)
            elif opr.operator_type == 0:  # 超级管理员授权所有
                permit.bind_super(opr.operator_name)


def run(config):
    log.startLogging(sys.stdout)
    app = Application(config)
    reactor.listenTCP(int(config.server.port), app, interface=config.server.host)
    reactor.run()