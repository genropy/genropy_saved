
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    root.webpage("!!Categories", filepath="/flib/categories")
    root.webpage("!!Item uploader", filepath="/flib/item_uploader")
    root.thpage("!!Items", table="flib.item")
