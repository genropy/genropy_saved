#!/usr/bin/python
# -*- coding: UTF-8 -*-

def config(root,application=None):
    orgn = root.branch('To Do')
    orgn.thpage('Action',table='orgn.action')
    orgn.thpage('!!Action types',table='orgn.action_type')
