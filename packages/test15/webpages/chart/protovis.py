# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
    
from gnr.core.gnrbag import Bag
import random

"Protovis"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    js_requires='protovis'

    def windowTitle(self):
        return 'Palette manager'
        
    def test_1_basic(self,pane):
        """Basic button"""

        bc = pane.borderContainer(width="100%", height="100%")

        top = bc.contentPane(region="top")
        top.button("Update", fire="update_data")

        self.dataRpc('random_data', 'random_data', _fired="update_data", _onResult="FIRE update_graph")

        self.testProtovis(bc.contentPane(region="left", width="50%", splitter=True))
        self.testProtovis(bc.contentPane(region="center"))

    def testProtovis(self, pane):

        pane.protovis("""

            var x = pv.Scale.linear(0, data.length).range(0,width),
                y = pv.Scale.linear(data).range(0,height),
                c = pv.Scale.linear(data).range("#1f77b4", "#ff7f0e");

            vis.margin(20).strokeStyle('#ccc');

            vis.add(pv.Rule)
                .data(x.ticks())
                .strokeStyle('#ccc')
                .left(x)
            .anchor("bottom").add(pv.Label)
                .text(x.tickFormat);


            vis.add(pv.Rule).
                .data(y.ticks())
                .strokeStyle('#ccc')
                .bottom(y)
            .anchor("left").add(pv.Label)
                .text(y.tickFormat);

            vis.add(pv.Dot)
                .data(data)
                .left(function() x(this.index))
                .bottom(function(d) y(d))
                .strokeStyle(c)
                .fillStyle(function(d) c(d).alpha(0.2));

        """,
        autoWidth=True, autoHeight=True, # These could be defaults
        data="=random_data",
        _fired="^update_graph")

    def rpc_random_data(self):
        numbers = range(20)
        random.shuffle(numbers)
        return numbers