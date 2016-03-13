#!/usr/bin/python
# -*- coding: UTF-8 -*-

def config(root,application=None):
    todo = root.branch('To Do')
    todo.thpage('Action',table='todo.action')
    todo.thpage('!!Action types',table='todo.action_type')
