#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    flib = root.branch(u"!!Flib", tags="admin")

    flib.thpage(u"!!Categories", table="flib.category")
    flib.webpage(u"!!Uploader", filepath="/flib/item_uploader")
    flib.thpage(u"!!Items", table="flib.item")
