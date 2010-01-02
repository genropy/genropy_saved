#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os, datetime

from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self, root, **kwargs):
        root, top, bottom = self.pbl_rootContentPane(root)
        #root.data('grid.struct', self._gridStruct())
        root.dataRpc('grid.data', 'gridData', _fired='^gnr.onStart')
        box = root.div(width='100%', height='300px')
        grid = box.IncludedView(nodeId='inputgrid',struct=self._gridStruct(),storepath='grid.data',
                                datamode='bag',editorEnabled=True)
        gridEditor = grid.gridEditor(datapath='dummy') #editOn='onCellClick')
        gridEditor.numbertextbox(gridcell='c')
        gridEditor.textbox(gridcell='name',validate_len=':4',validate_len_max='!!Too long',
                            validate_len_min='!!Too short')
        gridEditor.numbertextbox(gridcell='qt')
        gridEditor.checkbox(gridcell='new')
        gridEditor.datetextbox(gridcell='date')
        gridEditor.dbSelect(dbtable='showcase.person', gridcell='person', 
                            value='^.person_id', 
                            editorEnabled=True,
                            validate_notnull=True,validate_notnull_error='!!Required')
       #gridEditor.textbox(gridcell='size')
       #paneOpt = gridEditor.contentPane(gridcell='options')
       #paneOpt.checkbox('alpha',value='^.alpha')
       #paneOpt.checkbox('beta',value='^.beta')
       #paneOpt.checkbox('gamma',value='^.gamma')
        root.button('Edit', action='genro.wdgById("inputgrid").editBagRow(3);')
        
        
        root.button('Copy', fire='docopy')
        #root.div(datapath='test').dbSelect(dbtable='glbl.provincia', auxColumns='nome,regione', value='^.prov', selected_nome='.prov_dsc')
        
        root.textbox(connect_onBlur="console.log('onBlur')")
                    
        root.dataFormula('grid.copy', 'b.deepCopy()', b='=grid.data', _fired='^docopy')
        
    def _gridStruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('c', name='Range',width='3em', dtype='L')
        r.cell('name', name='Name',width='10em', dtype='T')
        r.cell('qt', name='Qty',width='10em', dtype='R')
        r.cell('new', name='New',width='10em', dtype='B')
        r.cell('size', name='Size',width='10em', dtype='T')
        r.cell('date', name='Date',width='10em', dtype='D')
        r.cell('person', name='Person',width='10em', dtype='T')
       # r.cell('options', name='Options',width='10em', dtype='T')

        return struct

    def rpc_gridData(self):
        result = Bag()
        date = datetime.date.today()
        for i in range(100):
            result['r_%i' % i] = Bag({'c':i, 'name':'Dsc %i' % i, 'qt':None, 'new':bool(i%2), 'size':'big', 'date':date + datetime.timedelta(i)})
        return result
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
