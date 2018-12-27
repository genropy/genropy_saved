#!/usr/bin/python
# -*- coding: utf-8 -*-

def config(root,application=None):
    geo_italia = root.branch(u"!![it]Geo Italia", tags="admin")
    geo_italia.thpage(u"!![it]Nazione", table="glbl.nazione")
    geo_italia.thpage(u"!![it]Regione", table="glbl.regione")
    geo_italia.thpage(u"!![it]Provincia", table="glbl.provincia")
    geo_italia.thpage(u"!![it]Comune", table="glbl.comune")
    geo_italia.thpage(u"!![it]Nuts", table="glbl.nuts")

