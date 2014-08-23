#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):
    geo_italia = root.branch(u"!!Geo Italia", tags="admin")
    geo_italia.thpage(u"!!Nazione", table="glbl.nazione")
    geo_italia.thpage(u"!!Regione", table="glbl.regione")
    geo_italia.thpage(u"!!Provincia", table="glbl.provincia")
    geo_italia.thpage(u"!!Comune", table="glbl.comune")
    geo_italia.thpage(u"!!Nuts", table="glbl.nuts")

