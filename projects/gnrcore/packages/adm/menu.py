# encoding: utf-8
def config(root,application=None):
    administration = root.branch(u"!!Administration", tags="admin")
    
    user_setup = administration.branch('!!Users setup')
    user_setup.webpage(u"!!Users", filepath="/adm/user_page")
    user_setup.thpage(u"!!Auth tags", table="adm.htag")
    user_setup.thpage(u"!!Group", table="adm.group")
    user_setup.thpage(u"!!Access groups", table="adm.access_group",tags='_DEV_,superadmin')

    utility = administration.branch('!!App Utility',tags='admin')
    utility.thpage(u"!!Letterheads", table="adm.htmltemplate")
    utility.thpage(u"!!Notifications", table="adm.notification")
    utility.thpage(u"!!Authorizations", table="adm.authorization")
    utility.thpage(u"!!Days", table="adm.day")
    utility.thpage(u"!!Userobjects", table="adm.userobject")
    utility.thpage(u"!!Counters", table="adm.counter",tags='_DEV_,superadmin')
    utility.lookups(u"!!Utility tables", lookup_manager="adm")

    dev = administration.branch('!!Developers',tags='_DEV_')
    
    dev.webpage(u"!!Install Checklist", filepath="/adm/checklist_page")
    dev.thpage(u"!!Backups", table="adm.backup")


    access_history = administration.branch('Access history',tags='_DEV_',checkpref='adm.dev.connection_log_enabled')
    access_history.thpage(u"!!Connections", table="adm.connection")
    access_history.thpage(u"!!Served pages", table="adm.served_page")

    permissions = administration.branch('!!Access permissions',tags='superadmin,_DEV_')
    permissions.thpage(u"!!Pkginfo", table="adm.pkginfo")
    permissions.thpage(u"!!Tableinfo", table="adm.tblinfo")
    permissions.webpage(u"!!User configurator", filepath="/adm/user_configuration",tags='superadmin')


    unused = administration.branch('!!Unused',tags='_DEV_')
    unused.thpage(u"!!Menu Manager", table="adm.menu")
    unused.thpage(u"!!Menu Pages", table="adm.menu_page")
    unused.thpage(u"!!Sent email", table="adm.sent_email")
