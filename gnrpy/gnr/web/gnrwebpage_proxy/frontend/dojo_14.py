#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  dojo_14.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage_proxy.frontend.dojo_base import GnrBaseDojoFrontend
from gnr.web.gnrwebstruct import  GnrDomSrc_dojo_14

class GnrWebFrontend(GnrBaseDojoFrontend):
    version = 'd14'
    domSrcFactory = GnrDomSrc_dojo_14

    def css_frontend(self, theme=None):
        theme = theme or self.theme
        return ['dojo/resources/dojo.css',
                'dijit/themes/dijit.css',
                'dijit/themes/%s/%s.css' % (theme, theme),
                'dojox/grid/_grid/Grid.css',
                'dojox/grid/_grid/%sGrid.css' % theme
        ]

    def gnrjs_frontend(self):
        return ['gnrbag', 'genro', 'genro_widgets', 'genro_rpc', 'genro_patch',
                'genro_dev', 'genro_dlg', 'genro_frm', 'genro_dom', 'gnrdomsource',
                'genro_wdg', 'genro_src', 'gnrlang', 'gnrstores']

    def css_genro_frontend(self):
        return {'all': ['gnrbase'], 'print': ['gnrprint']}


