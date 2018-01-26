#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    administration = root.branch(u"!!Email Config", tags="admin")
    administration.thpage(u"!!Accounts", table="email.account")
    administration.thpage(u"!!Messages", table="email.message")
    administration.lookups(u"!!Utility tables", lookup_manager="email")


