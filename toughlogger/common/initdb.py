#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.split(__file__)[0])
sys.path.insert(0,os.path.abspath(os.path.pardir))
from toughlogger.console import models
from sqlalchemy.orm import scoped_session, sessionmaker
from hashlib import md5
from sqlalchemy.sql import text as _sql
import datetime
import logging

def init_db(db):

    params = [
        ('system_name',u'系统名称',u'ToughLogger管理控制台'),
        ('is_debug',u'DEBUG模式',u'0'),
    ]


    for p in params:
        param = models.TlParam()
        param.param_name = p[0]
        param.param_desc = p[1]
        param.param_value = p[2]
        db.add(param)

    opr = models.TlOperator()
    opr.id = 1
    opr.node_id = 1
    opr.operator_name = u'admin'
    opr.operator_type = 0
    opr.operator_pass = md5('root').hexdigest()
    opr.operator_desc = 'admin'
    opr.operator_status = 0
    db.add(opr)


    db.commit()
    db.close()

def create_logtable(db_engine):
    create_sql_tpl = """
    CREATE TABLE {0} (
    	id INTEGER NOT NULL PRIMARY KEY autoincrement,
    	host VARCHAR(32) NOT NULL,
    	time VARCHAR(19) NOT NULL,
    	facility VARCHAR(16) NOT NULL,
    	priority VARCHAR(16) NOT NULL,
    	username VARCHAR(16) NULL,
    	message VARCHAR(512) NOT NULL
    );
    """
    mysql_create_sql_tpl = """
    CREATE TABLE {0} (
        id INT(11) NOT NULL PRIMARY KEY  AUTO_INCREMENT ,
        host VARCHAR(32) NOT NULL,
        time VARCHAR(19) NOT NULL,
        facility VARCHAR(16) NOT NULL,
        priority VARCHAR(16) NOT NULL,
        username VARCHAR(16) NULL,
        message VARCHAR(512) NOT NULL
    )
    COMMENT='syslog table'
    COLLATE='utf8_general_ci'
    ENGINE=InnoDB
    AUTO_INCREMENT=1;
    """
    sql_tpl = 'mysql' in db_engine.driver and mysql_create_sql_tpl or create_sql_tpl
    table_name = "log_{0}".format(datetime.datetime.now().strftime("%Y%m%d%H"))
    sqlstr = sql_tpl.format(table_name)
    with db_engine.begin() as conn:
        try:
            conn.execute(_sql(sqlstr))
        except:
            logging.exception("create logtable error")


def update(db_engine):
    print 'starting update database...'
    metadata = models.get_metadata(db_engine)
    metadata.drop_all(db_engine)
    metadata.create_all(db_engine)
    print 'update database done'
    db = scoped_session(sessionmaker(bind=db_engine, autocommit=False, autoflush=True))()
    init_db(db)
    create_logtable(db_engine)
