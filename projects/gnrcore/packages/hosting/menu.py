#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    hosting = root.branch(u"!!Hosting", basepath="/hosting", tags="owner")
    hosting.webpage(u"!!Clients", filepath="client")
    hosting.webpage(u"!!Instances", filepath="instance")
    hosting.webpage(u"!!Slot Types", filepath="slot_type")

