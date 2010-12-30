# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
    
from gnr.core.gnrbag import Bag

"Protovis"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    js_requires='protovis'

    def windowTitle(self):
        return 'Palette manager'
        
    def test_1_basic(self,pane):
        """Basic button"""
        pane=pane.div(height='300px')
        
        protovis="""var vis = new pv.Panel()
                        .width(150)
                        .height(150);
                    
                    vis.add(pv.Rule)
                        .data(pv.range(0, 2, .5))
                        .bottom(function(d) d * 80 + .5)
                      .add(pv.Label);
                    
                    vis.add(pv.Bar)
                        .data([1, 1.2, 1.7, 1.5, .7])
                        .width(20)
                        .height(function(d) d * 80)
                        .bottom(0)
                        .left(function() this.index * 25 + 25)
                      .anchor("bottom").add(pv.Label);
                      return vis"""
        pane.protovis(id='here',height='200px',width='200px',background_color='silver',margin='10px',protovis=protovis)

             