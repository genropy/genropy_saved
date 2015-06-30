#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    system = root.branch(u"!!System", tags="sysadmin,_DEV_")
    system.webpage("Onering", filepath="/sys/onering")
    system.webpage("Db Structure", filepath="/sys/dbstruct")
    system.webpage("Package editor", filepath="/sys/package_editor",tags='_DEV_')
    system.webpage("GnrIDE", filepath="/sys/gnride",tags='_DEV_')

