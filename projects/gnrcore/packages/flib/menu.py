
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    root.webpage(u"!!Categories", filepath="/flib/categories")
    root.webpage(u"!!Item uploader", filepath="/flib/item_uploader")
    root.thpage(u"!!Items", table="flib.item")
