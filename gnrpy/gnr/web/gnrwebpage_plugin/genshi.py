#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  genshi.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage_plugin.gnrbaseplugin import GnrBasePlugin
from genshi.template import TemplateLoader
import itertools
import os
from gnr.web.gnrwsgisite import WSGIHTTPException

AUTH_OK = 0
AUTH_NOT_LOGGED = 1
AUTH_FORBIDDEN = -1

class Plugin(GnrBasePlugin):
    def __call__(self, *args, **kwargs):
        dojo_theme=kwargs.pop('dojo_theme',None)
        striped=kwargs.pop('striped','odd_row,even_row')
        pdf=kwargs.pop('pdf',False)
        genshi_path=kwargs.get('genshi_path')
        page = self.page
        dojo_theme = dojo_theme or getattr(self.page, 'dojo_theme', None) or 'tundra'
        auth = page._checkAuth()
        if auth != AUTH_OK:
            return self.page.site.forbidden_exception
        if striped:
            kwargs['striped'] = itertools.cycle(striped.split(','))
        gnr_static_handler = page.site.getStatic('gnr')
        tpldirectories = [os.path.dirname(genshi_path), page.parentdirpath] + page.resourceDirs + [
                gnr_static_handler.path(page.gnrjsversion, 'tpl')]
        loader = TemplateLoader(tpldirectories)
        template = loader.load(os.path.basename(genshi_path))
        page.charset = 'utf-8'
        _resources = page.site.resources.keys()
        _resources.reverse()

        arg_dict = page.build_arg_dict()
        arg_dict['mainpage'] = page
        arg_dict.update(kwargs)
        try:
            output = template.generate(**arg_dict).render()
        except WSGIHTTPException, exc:
            return exc
        if not pdf:
            page.response.content_type = 'text/html'
            return output
        else:
            pass