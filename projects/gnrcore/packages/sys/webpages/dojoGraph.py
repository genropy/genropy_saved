#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory

class GnrCustomWebPage(object):
    dojo_version='18'
    dojo_theme='tundra'

    #py_requires="""gnrcomponents/dynamicform/componentDojoGraph:componentsGrafico"""
    #py_requires = 'gnrcomponents/graphiframe:GraphIframe'
    #css_requires="gnrcomponents/dynamicform/dojo_18/dijit/themes/tundra/tundra"
    js_requires='gnrcomponents/graphiframe/graphiframe'
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


