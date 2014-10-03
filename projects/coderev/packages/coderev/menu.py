#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    auto = root.branch(u"auto")
    auto.thpage(u"!!Py_class", table="coderev.py_class")
    auto.thpage(u"!!Py_method", table="coderev.py_method")
    auto.thpage(u"!!Py_module", table="coderev.py_module")
    auto.thpage(u"!!Py_package", table="coderev.py_package")

