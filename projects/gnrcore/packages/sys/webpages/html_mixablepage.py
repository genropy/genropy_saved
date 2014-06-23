#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
 
from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory
 
class GnrCustomWebPage(object):
    dojo_version='18'
    dojo_theme='tundra'
    def onIniting(self, url_parts, request_kwargs):
        component_path = '%s:%s' %('/'.join(url_parts[0:-1]),url_parts[-1])
        url_parts[:] = []
        self.mixinComponent(component_path)

    def main(self, body, **kwargs):
        pass