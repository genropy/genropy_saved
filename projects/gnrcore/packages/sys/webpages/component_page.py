#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
 
from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory
 
class GnrCustomWebPage(object):
    dojo_version='18'
    dojo_theme='tundra'

    def onIniting(self, url_parts, request_kwargs):
        print request_kwargs
        #for pkgname in self.db.packages.keys():
        #    try:
        #        cl = self.site.loadResource(pkgname, 'preference:AppPref')
        #        self.mixin(cl)
        #    except GnrMixinError:
        #        pass
    
 
    #py_requires="""gnrcomponents/dynamicform/componentDojoGraph:componentsGrafico"""
    #py_requires = 'gnrcomponents/graphiframe:GraphIframe'
    #css_requires="gnrcomponents/dynamicform/dojo_18/dijit/themes/tundra/tundra"
    #js_requires='gnrcomponents/graphiframe/graphiframe'
    def main(self, body, **kwargs):
        bc = body.borderContainer(position='absolute',top=0,bottom=0,left=0,right=0)
        bc.contentPane(region='left',background='green',width='200px')
        bc.contentPane(region='center',background='pink')
       #bc.Chart2D('mainchart')
       #bc.script("""dojo.ready(function(){
       #        gnrgraph.start('mainchart');
       #    })
       #            
       #    """)
 
        #self.plotGrafico(body, **kwargs)