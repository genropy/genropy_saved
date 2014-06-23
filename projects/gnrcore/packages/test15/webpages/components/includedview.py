# -*- coding: UTF-8 -*-

# includedview.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""IncludedView test page"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    auto_polling = 0
    user_polling = 0
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull,foundation/includedview:IncludedView,gnrcomponents/selectionhandler'
    
    def common_data(self):
        result = Bag()
        for i in range(5):
            result['r_%i' % i] = Bag(dict(name='Mr. Man %i' % i, age=i + 36, work='Work useless %i' % i))
        return result
        
    def common_struct(self, struct):
        r = struct.view().rows()
        r.cell('name', name='Name', width='10em')
        r.cell('age', name='Age', width='5em', dtype='I')
        r.cell('work', name='Work', width='10em')
        
    def test_1_includedview_editable_bag(self, pane):
        """Includedview editable datamode bag"""
        bc = pane.borderContainer(height='300px')
        bc.data('.mygrid.rows', self.common_data())
        bc.data('nome', 'piero')
        iv = self.includedViewBox(bc, label='!!Products', datapath='.mygrid',
                                  storepath='.rows', struct=self.common_struct,
                                  autoWidth=True, datamode='bag',
                                  add_action=True, del_action=True, editorEnabled=True,
                                  newRowDefaults=dict(name='^nome')
                                  #newRowDefaults = "function(){return {name:'piero'}}"
                                  #newRowDefaults = "return {name:'piero'}"
                                  )
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.numbertextbox(gridcell='age')
        gridEditor.textbox(gridcell='work')
        
   # def prov_struct(self,struct):
   #     r = struct.view().rows()
   #     r.fieldcell('nome', width='50%')
   #     r.fieldcell('@regione.nome', width='50%')
   #     
   # def _test_2_remote_includedview_db(self, pane):
   #     bc = pane.borderContainer(height='300px')
   #     self.includedViewBox(bc, label='Test', datapath='.test_db', filterOn='auto:sigla+nome+codice+regione',
   #                          nodeId='test_db', table='glbl.provincia', autoWidth=True,
   #                          _onStart=True, selectionPars=dict(order_by='$nome'))
   #                          
   # def _test_5_selectiohandler(self, pane):
   #     bc = pane.borderContainer(height='300px')
   #     pane = bc.contentPane(region='center')
   #     iv = pane.selectionViewBox(frameCode='test_db',label='Test', datapath='.test_db', filterOn='auto:sigla+nome+codice+regione',
   #                          nodeId='test_db', table='glbl.provincia',
   #                          struct=self.prov_struct,_onStart=True, selectionPars=dict(order_by='$nome'))
   #                          
   #    #menu = bc.top.right.add_del.addButton.menu(id='mymenu',modifiers='*')
   #    #menu.menuline('Open...',action="FIRE .reload;")
   #    #menu.menuline('Close',action="alert('Closing...')")
   #     
   # def test_6_selectiohandler(self, pane):
   #     bc = pane.borderContainer(height='300px')   
   #     frame = bc.selectionHandler(label='Test', datapath='.test_db', filterOn='auto:sigla+nome+codice+regione',
   #                          nodeId='test_db', table='glbl.provincia', 
   #                          checkMainRecord=False,struct=self.prov_struct,
   #                          _onStart=True, selectionPars=dict(order_by='$nome'))
   #                          
   # #    #menu = bc.top.right.add_del.addButton.menu(id='mymenu',modifiers='*')
   # #    #menu.menuline('Open...',action="FIRE .reload;")
   # #    #menu.menuline('Close',action="alert('Closing...')")
   # #
   #     
   # def _test_3_remote_includedview_editable_bag(self, pane):
   #     """Includedview editable datamode bag"""
   #     bc = pane.borderContainer(height='300px')
   #     bc.data('.mygrid.rows', self.common_data())
   #     bc.contentPane(region='top').button('Build remote grid', fire='.build')
   #     bc.contentPane(region='center').remote('test_2', _fired='^.build')
   #     
   # def remote_test_2(self, pane):
   #     bc = pane.borderContainer(height='100%')
   #     iv = self.includedViewBox(bc, label='!!Products', datapath='.mygrid',
   #                               storepath='.rows', struct=self.common_struct,
   #                               autoWidth=True, datamode='bag',
   #                               add_action=True, del_action=True, editorEnabled=True)
   #     gridEditor = iv.gridEditor()
   #     gridEditor.textbox(gridcell='name')
   #     gridEditor.numbertextbox(gridcell='age')
   #     gridEditor.textbox(gridcell='work')