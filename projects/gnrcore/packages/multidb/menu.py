# encoding: utf-8
def config(root,application=None):
    multidb = root.branch(u"!!Multidb", tags="sysadmin,_DEV_,superadmin")
    multidb.webpage("Multidb dashboard", filepath="/multidb/multidb_dashboard",tags='_DEV_')
    multidb.webpage("Sync status", filepath="/multidb/sync_status",tags='_DEV_')
