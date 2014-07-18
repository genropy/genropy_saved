
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    administration = root.branch("!!Administration", tags="admin")
    administration.webpage("!!Users", filepath="/adm/user_page")
    administration.thpage("!!Auth tags", table="adm.htag")
    administration.thpage("!!Letterheads", table="adm.htmltemplate")
    administration.thpage("!!Notifications", table="adm.notification")
    administration.thpage("!!Menu Manager", table="adm.menu")
    administration.thpage("!!Menu Pages", table="adm.menu_page")
    administration.thpage("!!Datacatalog", table="adm.datacatalog")
    administration.lookups("!!Utility tables", lookup_manager="adm")
    administration.thpage("!!Counter", table="adm.counter")

