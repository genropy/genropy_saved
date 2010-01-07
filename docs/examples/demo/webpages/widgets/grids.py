#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Grid Test"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #root = self.rootLayoutContainer(root)
        sp=root.splitContainer(height='100%')
        sp.contentPane(sizeShare=30).tree(storepath='*D',label='data',inspect='shift')
        right=sp.splitContainer(sizeShare=70,orientation='vertical')
        top=right.contentPane(sizeShare=30)
        fb=top.formbuilder(cols=4,datapath='grid.selected.buffer')
        fb.textBox(lbl='Name',value='^.name')
        fb.textBox(lbl='Sex',value='^.sex',width='4em')
        fb.dateTextBox(lbl='Birthday',value='^.birthday')
        fb.numberTextBox(lbl='Height',value='^.height',width='4em')
        fb.button('Add', action="var newkey='T_'+genro.getCounter();genro.setData('grid.data.'+newkey,null,{_pkey:newkey,name:'aaaa'})")
        fb.button('Delete', action="alert('deleting')")
        bottom=right.contentPane(sizeShare=70)
        bottom.data('grid.struct',self.gridStruct())
        bottom.data('grid.data',self.gridData())
        bottom.staticGrid(storepath='grid.data',structpath='grid.struct',elasticView=0, identifier='_pkey',gnrId='mygrid',
                       autoWidth=True,autoHeight=False,selectedRow='grid.selected.row',selectedRowBuffer='grid.selected.buffer')

    def gridData(self):
        data=Bag()
        data.rowchild(name='Mark Smith',sex='M',birthday='1980-06-04::D',height=170, _pkey='KK5567')
        data.rowchild(name='Ann Brown',sex='F',birthday='1960-09-21::D',height=173)
        data.rowchild(name='Sam Dubs',sex='M',birthday='1981-03-14::D',height=182)
        data.rowchild(name='John Doe',sex='M',birthday='1977-12-05::D',height=191)
        return data
        
    def gridStruct(self):
        struct=Bag()
        r=struct.child('view',noscroll=False).child('rows')
        r.child('cell',field='name',width='20em',name='Name')
        r.child('cell',field='sex',width='2em',name='Sex')
        r.child('cell',field='height',width='3em',name='Height',text_align='right')
        r.child('cell',field='birthday',width='10em',name='Birthday',format_date='long')
        return struct
    
    def gridStruct_(self):
        struct=Bag()
        r=struct.child('view',noscroll=True,viewWidth='20em').child('rows')
        r.child('cell',field='name',width='20em',name='Name')
        r=struct.child('view').child('rows')
        r.child('cell',field='sex',width='2em',name='Sex')
        r.child('cell',field='height',width='3em',name='Height',text_align='right')
        r.child('cell',field='birthday',width='10em',name='Birthday',format_date='long')
        return struct
     
        
