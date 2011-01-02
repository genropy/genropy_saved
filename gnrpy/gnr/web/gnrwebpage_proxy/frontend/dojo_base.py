#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------

from gnr.web.gnrwebpage_proxy.frontend.gnrbasefrontend import GnrBaseFrontend
from gnr.core.gnrlang import boolean
import os.path

class GnrBaseDojoFrontend(GnrBaseFrontend):
    def importer(self):
        return '<script type="text/javascript" src="%s" djConfig="%s"> </script>' % (self.dojolib, self.djConfig)

    def init(self, **kwargs):
        self.dojo_static_handler = self.page.site.getStatic('dojo')
        dojo_theme = getattr(self.page, 'dojo_theme', None) or self.page.site.config['dojo?theme'] or 'tundra'
        self._theme = dojo_theme
        self.dojo_version = self.page.dojo_version
        if boolean(self.page.dojo_source):
            dojofolder = 'dojo_src'
            if not os.path.exists(self.dojo_static_handler.path(self.dojo_version, dojofolder)):
                dojofolder = 'dojo'
        else:
            dojofolder = 'dojo'
        dojolib = self.dojo_static_handler.url(self.dojo_version, dojofolder, 'dojo', 'dojo.js')
        self.dojolib = dojolib
        self.djConfig = "parseOnLoad: false, isDebug: %s, locale: '%s' ,noFirebugLite:true" % (
        self.page.isDeveloper() and 'true' or 'false', self.page.locale)


    def _get_theme(self):
        return self._theme

    theme = property(_get_theme)

    def event_onBegin(self):
        self._theme = self._call_kwargs.pop('dojo_theme', None) or self._theme

    def frontend_arg_dict(self, arg_dict):
        arg_dict['dojolib'] = self.dojolib
        arg_dict['djConfig'] = self.djConfig
        css_dojo = self.css_frontend()
        arg_dict['css_dojo'] = [self.dojo_static_handler.url(self. dojo_version, 'dojo', f) for f in css_dojo]
        
    
