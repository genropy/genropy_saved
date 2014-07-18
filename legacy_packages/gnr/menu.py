
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    gnrpkg = root.branch("gnrpkg", tags="_DEV_")
    gnrpkg.thpage("!!Error", table="gnr.error")
    gnrpkg.thpage("!!Sync_out", table="gnr.sync_out")
    gnrpkg.thpage("!!Transaction", table="gnr.transaction")

