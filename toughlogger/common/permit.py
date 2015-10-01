#!/usr/bin/env python
#coding=utf-8
import time

class Permit():
    """ 权限菜单管理
    """
    routes = {}
    all_handlers = []

    def add_route(self, handle_cls,path, name, category,handle_params={}, is_menu=False, order=time.time(), is_open=True):
        """ 注册权限
        """
        if not path: return
        self.routes[path] = dict(
            path=path,# 权限url路径
            name=name,# 权限名称
            category=category,# 权限目录
            is_menu=is_menu,# 是否在边栏显示为菜单
            oprs=[],# 关联的操作员
            order=order,# 排序
            is_open=is_open # 是否开放授权
        )
        self.add_handler(handle_cls,path,handle_params)

    def add_handler(self, handle_cls, path, handle_params={}):
        print ("add handler [%s:%s]"%(path,repr(handle_cls)))
        self.all_handlers.append((path, handle_cls, handle_params))

    def get_route(self, path):
        """ 获取一个权限资源
        """
        return self.routes.get(path)

    def bind_super(self, opr):
        """ 为超级管理员授权所有权限
        """
        for path in self.routes:
            route = self.routes.get(path)
            route['oprs'].append(opr)

    def bind_opr(self, opr, path):
        """ 为操作员授权
        """
        if not path or path not in self.routes:
            return
        oprs = self.routes[path]['oprs']
        if opr not in oprs:
            oprs.append(opr)

    def unbind_opr(self, opr, path=None):
        """ 接触操作员与权限关联
        """
        if path:
            self.routes[path]['oprs'].remove(opr)
        else:
            for path in self.routes:
                route = self.routes.get(path)
                if route and opr in route['oprs']:
                    route['oprs'].remove(opr)

    def check_open(self, path):
        """ 检查权限是否开放授权
        """
        route = self.routes[path]
        return 'is_open' in route and route['is_open']

    def check_opr_category(self, opr, category):
        """ 检查权限是否在指定目录下
        """
        for path in self.routes:
            route = self.routes[path]
            if opr in route['oprs'] and route['category'] == category:
                return True
        return False

    def build_menus(self, order_cats=[]):
        """ 生成全局内存菜单"""
        menus = [{'category': _cat, 'items': []} for _cat in order_cats]
        for path in self.routes:
            route = self.routes[path]
            for menu in menus:
                if route['category'] == menu['category']:
                    menu['items'].append(route)
        return menus

    def match(self, opr, path):
        """ 检查操作员是否匹配资源
        """
        if not path or not opr:
            return False
        return opr in self.routes[path]['oprs']

# 全局实例
permit = Permit()