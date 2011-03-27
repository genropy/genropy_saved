# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.


from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,foundation/includedview"
    def common_struct(self, struct):
        r = struct.view().rows()
        r.cell('name', name='Name', width='10em')
        r.cell('age', name='Age', width='5em', dtype='I')
        r.cell('work', name='Work', width='10em')
        
    def common_data(self):
        result = Bag()
        for i in range(5):
            result['r_%i' % i] = Bag(dict(name='Mr. Man %i' % i, age=i + 36, work='Work useless %i' % i))
        return result
    
    
    def test_0_firsttest(self,pane):
        """First test description"""
        frame = pane.framePane('gridtest',height='400px')
        tbar = frame.top.slotToolbar('*,iv_add')
        frame.data('.mybag', self.common_data())
        iv = frame.includedView(storepath='.mybag',datapath=False,struct=self.common_struct,datamode='bag',
                                selfsubscribe_add="""this.widget.addBagRow('#id', '*', this.widget.newBagRow());
                                                     this.widget.editBagRow(null,1000);
                                                     """,onCreated="console.log('widget',widget);widget.updateRowCount('*');")
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.numbertextbox(gridcell='age')
        gridEditor.textbox(gridcell='work')
        