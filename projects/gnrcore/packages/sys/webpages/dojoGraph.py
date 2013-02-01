#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlPage as page_factory

class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/dynamicform/componentDojoGraph:componentsGrafico"""
    css_requires="gnrcomponents/dynamicform/dojo_18/dijit/themes/tundra/tundra"
    js_requires='gnrcomponents/dynamicform/dojo_18/dojo/dojo, gnrcomponents/dynamicform/dynamicform'
    def main(self, body, **kwargs):
        self.plotGrafico(body, **kwargs)