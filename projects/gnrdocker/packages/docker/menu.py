#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    auto = root.branch(u"auto")
    auto.thpage(u"!!Container", table="docker.container")
    auto.thpage(u"!!Server", table="docker.server")
    auto.thpage(u"!!Server_container", table="docker.server_container")

