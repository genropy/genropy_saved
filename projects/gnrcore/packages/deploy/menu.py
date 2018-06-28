#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    deploy = root.branch(u"!!Deploy", tags="admin")
    deploy.thpage(u"!!Provider", table="deploy.provider")
    deploy.thpage(u"!!Hosts", table="deploy.host")
    deploy.webpage(u"!!Instances", table="deploy.instance")
    deploy.lookups('Lookup tables',lookup_manager='deploy')
