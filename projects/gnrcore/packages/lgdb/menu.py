#!/usr/bin/python3
# -*- coding: utf-8 -*-

def config(root,application=None):
    lgdb = root.branch('DB Descriptor')
    lgdb.thpage('Legacy tables',table='lgdb.lg_table')
    lgdb.thpage('Legacy package',table='lgdb.lg_pkg')
    lgdb.thpage('Legacy column',table='lgdb.lg_column')