#!/usr/bin/python
# -*- coding: utf-8 -*-

def config(root,application=None):
    docu = root.branch('Documentation')
    docu.thpage('!!Documentation',table='docu.documentation')
    docu.lookups(u"!!Docu tables", lookup_manager="docu")
