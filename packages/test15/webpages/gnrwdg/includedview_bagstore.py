# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

"includedview: bagstore"
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    dojo_source = True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,foundation/includedview"
    
    def test_0_firsttest(self,pane):
        """First test description"""
        frame = pane.framePane('gridtest',height='400px',_class='no_over',datapath='.test')
        tbar = frame.top.slotToolbar('*,addrow',addrow_delay=300)
        frame.data('.mybag',self.common_data())
        frame.dataController("console.log(data)",data="=#",fired='tt')
        iv = frame.includedView(storepath='.mybag',datapath=False,struct=self.common_struct,datamode='bag',
                                selectedIndex='.currIndex',
                                selfsubscribe_addrow="""for(var i=0; i<$1._counter;i++){
                                                            this.widget.addBagRow('#id', '*', this.widget.newBagRow());
                                                        }
                                                        this.widget.editBagRow(null);
                                                        """)
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.numbertextbox(gridcell='age')
        gridEditor.textbox(gridcell='work')
        
    def common_data(self):
        result = Bag()
        for i in range(5):
            result['r_%i' % i] = Bag(dict(name='Mr. Man %i' % i, age=i + 36, work='Work useless %i' % i))
        return result
        
    def common_struct(self, struct):
        r = struct.view().rows()
        r.cell('name',name='Name',width='10em')
        r.cell('age',name='Age',dtype='I',width='5em')
        r.cell('work',name='Work',width='10em')
        