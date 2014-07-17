
#!/usr/bin/env python
# encoding: utf-8
def config(root):
    system = root.branch("!!System", tags="sysadmin")
    system.webpage("Onering", file="/sys/onering")
    system.webpage("Db Structure", file="/sys/dbstruct")

