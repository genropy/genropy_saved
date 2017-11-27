#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    system = root.branch(u"!!System", tags="sysadmin,_DEV_")
    system.webpage("Onering", filepath="/sys/onering")
    system.webpage("Db Structure", filepath="/sys/dbstruct")
    system.webpage("Package editor", filepath="/sys/package_editor",tags='_DEV_')
    system.webpage("Startup data manager", filepath="/sys/startupdata_manager",tags='_DEV_')
    system.thpage("Tasks", table='sys.task',tags='_DEV_')

    system.webpage("Localization editor", filepath="/sys/localizationeditor",
                    tags='_DEV_,_TRD_,superadmin')
    system.webpage("GnrIDE", filepath="/sys/gnride",tags='_DEV_')

