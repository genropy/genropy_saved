
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    system = root.branch(u"!!System", tags="sysadmin")
    system.webpage(u"Onering", filepath="/sys/onering")
    system.webpage(u"Db Structure", filepath="/sys/dbstruct")

