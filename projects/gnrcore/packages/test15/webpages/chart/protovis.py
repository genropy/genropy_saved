# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Protovis"""

from gnr.core.gnrbag import Bag
import random
from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    js_requires = 'protovis'

    def windowTitle(self):
        return 'Palette manager'

    def test_1_from_script(self, pane):
        """From Script"""
        pane = pane.div(height='300px')
        bc = pane.borderContainer(width="100%", height="100%")
        top = bc.contentPane(region="top", background_color='pink', height='30px')
        top.button("Update", fire=".update_data")
        top.dataRpc('.data', 'random_data', _fired="^.update_data", _onResult="FIRE .update_graph")
        self.createProtovis(bc.contentPane(region="left", width="50%", splitter=True, background_color='lime'),
                            'left_vis1', js=self.scriptTest())
        self.createProtovis(bc.contentPane(region="center"), 'right_vis1', js=self.scriptTest())

    def test_2_fromBag(self, pane):
        """FromBag"""
        pane = pane.div(height='300px')
        pane.data('.myprotovis.source', self.bagTest())
        pane.data('.myprotovis.width', 300)
        pane.data('.myprotovis.height', 200)
        pane.dataRpc('.myprotovis.data', 'random_data', _fired="^.update_data", _onResult="FIRE .update_graph")

        bc = pane.borderContainer(width="100%", height="100%")
        fb = bc.contentPane(region="top", background_color='pink', height='30px').formbuilder(cols=4,
                                                                                              border_spacing='3px')
        fb.button("Update", fire=".update_data")
        fb.horizontalslider(value="^.myprotovis.width", minimum=200, maximum=500, intermediateChanges=False,
                            width='150px', lbl='Width')
        fb.horizontalslider(value="^.myprotovis.height", minimum=100, maximum=300, intermediateChanges=False,
                            width='150px', lbl='Height')
        self.createProtovis(bc.contentPane(region="left", width="50%",
                                           splitter=True, background_color='lime'), 'left_vis2',
                            storepath='.myprotovis')
        self.createProtovis(bc.contentPane(region="center"), 'right_vis2', storepath='.myprotovis')


    def test_3_fromFile(self, pane):
        pane = pane.div(height="300px")
        b = Bag()
        for n in xrange(10):
            b['r_%d' % n] = n % 5
        pane.data('.myprotovis.width', 300)
        pane.data('.myprotovis.height', 200)
        pane.dataRpc('.myprotovis.data', 'random_data', _fired="^.update_data", _onResult="FIRE .update_graph")

        bc = pane.borderContainer(width="100%", height="100%")
        fb = bc.contentPane(region="top", background_color='pink', height='30px').formbuilder(cols=4,
                                                                                              border_spacing='3px')
        fb.button("Update", fire=".update_data")
        fb.horizontalslider(value="^.myprotovis.width", minimum=200, maximum=500, intermediateChanges=False,
                            width='150px', lbl='Width')
        fb.horizontalslider(value="^.myprotovis.height", minimum=100, maximum=300, intermediateChanges=False,
                            width='150px', lbl='Height')

        bc.contentPane(region="left", splitter=True).protovisJS(nodeId="left_vis3", height="200", width="300",
                                                              data="=.data", src="protovis-sample3.js")


    @struct_method
    def protovisJS(self, parent, js=None, src=None, **kwargs):
        if js and src:
            raise ValueError("protovisJS: please specify only 'js' or 'src', but not both parameters.")
        if src:
            js = open(self.getResource(src),'rT').read()
        parent.protovis(js=js, **kwargs)

    def scriptTest(self):
        return """if(!data){return}
                  vis.width(width)
                     .height(height);
                  vis.add(pv.Rule)
                     .data(pv.range(0, 1, .5))
                     .bottom(function(d) d * 80+ .5)
                     .add(pv.Label);
                  
                  vis.add(pv.Bar)
                     .data(data)
                     .width(20)
                     .height(function(d) d * 80)
                     .bottom(0)
                     .left(function() this.index * 25 + 25)
                     .anchor("bottom").add(pv.Label);"""

    def createProtovis(self, pane, nodeId, _fired=None, **kwargs):
        pane.protovis(nodeId=nodeId,
                      width=200,
                      height=200,
                      data="=.data", **kwargs)
        pane.dataController("genro.publish('%s_render')" % nodeId, _fired="^.update_graph")


    def bagTest(self):
        result = Bag()
        visbag = result.child('Panel', width='=.width', height='=.height')
        visbag.child('Rule', data='pv.range(0, 2, .5)::JS',
                     bottom='function(d){return d * 80 + .5}::JS').child('Label')
        visbag.child('Bar', data='=.data',
                     width='20', height='function(d){return d * 80}::JS',
                     bottom=0,
                     left='function() {return this.index * 25 + 25}::JS',
                     anchor='bottom').child(tag='Label')
        return result

    #def testProtovis_(self, pane,nodeId):
    #   pane.protovis(protovis="""
    #       if(!data){return}
    #       var x = pv.Scale.linear(0, data.length).range(0,width),
    #           y = pv.Scale.linear(data).range(0,height),
    #           c = pv.Scale.linear(data).range("#1f77b4", "#ff7f0e");
    #       vis.margin(20).strokeStyle('#ccc');
    #
    #       vis.add(pv.Rule)
    #           .data(x.ticks())
    #           .strokeStyle('#ccc')
    #           .left(x)
    #       .anchor("bottom").add(pv.Label)
    #           .text(x.tickFormat);
    #
    #
    #       vis.add(pv.Rule)
    #           .data(y.ticks())
    #           .strokeStyle('#ccc')
    #           .bottom(y)
    #       .anchor("left").add(pv.Label)
    #           .text(y.tickFormat);
    #
    #       vis.add(pv.Dot)
    #           .data(data)
    #           .left(function() x(this.index))
    #           .bottom(function(d) y(d))
    #           .strokeStyle(c)
    #           .fillStyle(function(d) c(d).alpha(0.2));
    #
    #   """,
    #   autoWidth=True, autoHeight=True, # These could be defaults
    #   width=400,
    #   height=300,
    #   nodeId=nodeId,
    #   data="=random_data",
    #   _fired="^update_graph")

    def rpc_random_data(self):
        numbers = [int(random.random() * 200) / 100. for i in range(10)]
        return '%s::JS' % str(numbers)