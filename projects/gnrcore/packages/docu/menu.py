#!/usr/bin/python
# -*- coding: utf-8 -*-

def config(root,application=None):
    docu = root.branch('Documentation',tags='_DOC_')
    docu.thpage('!!Documentation',table='docu.documentation')
    docu.thpage('!!Handbooks',table='docu.handbook')
    docu.lookups(u"!!Docu tables", lookup_manager="docu")
