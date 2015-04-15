#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    dev = root.branch("Developer")
    dev.thpage('Widgets',table='dev.widget',tags='_DEV_')
