#!/usr/bin/env python
#coding:utf-8
from toughlogger.console.handlers.base import BaseHandler
from toughlogger.common.permit import permit

class LogoutHandler(BaseHandler):

    def get(self):
        if not self.current_user:
            self.clear_all_cookies()
            self.redirect("/login")
            return
        self.clear_all_cookies()    
        self.redirect("/login",permanent=False)

permit.add_handler(LogoutHandler, r"/logout")
