
#!/usr/bin/env python
# encoding: utf-8
def config(root):
    root.webpage("!!Categories", file="/flib/categories")
    root.webpage("!!Item uploader", file="/flib/item_uploader")
    root.thpage("!!Items", table="flib.item")
