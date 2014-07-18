
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    system = root.branch("!!System", tags="sysadmin")
    system.webpage("Onering", filepath="/sys/onering")
    system.webpage("Db Structure", filepath="/sys/dbstruct")

