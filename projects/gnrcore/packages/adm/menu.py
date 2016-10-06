#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    administration = root.branch(u"!!Administration", tags="admin")
    administration.webpage(u"!!Users", filepath="/adm/user_page")
    administration.thpage(u"!!Auth tags", table="adm.htag")
    administration.thpage(u"!!Group", table="adm.group")
    administration.thpage(u"!!Letterheads", table="adm.htmltemplate")
    administration.thpage(u"!!Notifications", table="adm.notification")
    administration.thpage(u"!!Connections", table="adm.connection",tags='_DEV_')
    administration.thpage(u"!!Served pages", table="adm.served_page",tags='_DEV_')
    administration.thpage(u"!!Menu Manager", table="adm.menu",tags='_DEV_')
    administration.thpage(u"!!Menu Pages", table="adm.menu_page",tags='_DEV_')
    administration.thpage(u"!!Datacatalog", table="adm.datacatalog",tags='_DEV_')
    administration.thpage(u"!!Pkginfo", table="adm.pkginfo",tags='_DEV_')
    administration.thpage(u"!!Tableinfo", table="adm.tblinfo",tags='_DEV_')
    administration.lookups(u"!!Utility tables", lookup_manager="adm")
    administration.thpage(u"!!Counter", table="adm.counter")

