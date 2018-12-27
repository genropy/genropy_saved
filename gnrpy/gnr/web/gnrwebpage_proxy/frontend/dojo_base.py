#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  dojo_base.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

# --------------------------- GnrWebPage subclass ---------------------------

from gnr.web.gnrwebpage_proxy.frontend.gnrbasefrontend import GnrBaseFrontend
from gnr.core.gnrlang import boolean
import os.path

class GnrBaseDojoFrontend(GnrBaseFrontend):
    def importer(self):
        return '<script type="text/javascript" src="%s" djConfig="%s"> </script>' % (self.dojolib, self.djConfig)
        
    def init(self, **kwargs):
        self.dojo_storage_handler = self.page.site.storage('dojo')
        dojo_theme = getattr(self.page, 'dojo_theme', None) or self.page.site.config['dojo?theme'] or 'tundra'
        self._theme = dojo_theme
        self.dojo_version = self.page.dojo_version
        self.dojo_release= None
        if boolean(self.page.dojo_source):
            dojofolder = 'dojo_src'
            if not self.dojo_storage_handler.exists(self.dojo_version, dojofolder):
                dojofolder = 'dojo'
        else:
            dojofolder = 'dojo'
        localroot = None
        if self.page.connection.electron_static:
            localroot ='file://%s/app/lib/static/' %self.page.connection.electron_static
        dojolib = self.dojo_storage_handler.url(self.dojo_version, dojofolder, 'dojo', 'dojo.js',_localroot=localroot)
        self.dojofolder = dojofolder
        self.dojolib = dojolib
        self.djConfig = "parseOnLoad: false, isDebug: %s, locale: '%s' ,noFirebugLite:true" % (
                   self.page.isDeveloper() and 'true' or 'false', self.page.locale.lower())
        
    def _get_theme(self):
        return self._theme
        
    theme = property(_get_theme)
        
    def event_onBegin(self):
        self._theme = self._call_kwargs.pop('dojo_theme', None) or self._theme
        
    def frontend_arg_dict(self, arg_dict):
        arg_dict['dojolib'] = self.dojolib
        arg_dict['djConfig'] = self.djConfig
        css_dojo = self.css_frontend()
        arg_dict['css_dojo'] = [self.dojo_storage_handler.url(self.dojo_version, 'dojo', f) for f in css_dojo]
        if self.dojo_release:
            releaseImports = self.dojo_release_imports()
            arg_dict['dijitImport'] = [self.dojo_storage_handler.url(self.dojo_version, self.dojofolder, 'dojo', f) for f in releaseImports]
            
        
    def dojo_release_imports(self):
        return []