#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    gnrpkg = root.branch(u"gnrpkg", tags="_DEV_")
    gnrpkg.thpage(u"!!Error", table="gnr.error")
    gnrpkg.thpage(u"!!Sync_out", table="gnr.sync_out")
    gnrpkg.thpage(u"!!Transaction", table="gnr.transaction")

