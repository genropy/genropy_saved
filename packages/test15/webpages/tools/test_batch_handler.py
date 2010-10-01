# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Test batch handler"""
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/batch_handler/batch_handler:TableScriptRunner,gnrcomponents/batch_handler/batch_handler:BatchMonitor"

    def windowTitle(self):
        return 'Test Batch Handler'
    
    def loc_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('nome', name='Nome', width='10em')
        r.cell('provincia', name='Provincia', width='10em')
        return struct
        
    def test_0_root(self,pane):
        """Not real test: common stuff"""
        bc = pane.borderContainer(height='300px',datapath='test0')
        fb = bc.contentPane(region='top').formbuilder(cols=1).textbox(value='^.localita',lbl='Localita')
        bc.dataSelection('.selection','glbl.localita',where="$nome ILIKE :v||'%%'",v='^.localita',
                            selectionName='myselection')
        self.bm_monitor_pane(bc.contentPane(region='right',width='200px',splitter=True))
        bc.contentPane(region='center').includedView(storepath='.selection',struct=self.loc_struct(),nodeId='mygrid')
        
    def test_1_launch_button(self,pane):
        """Launch test from button"""
        pane.button('Launch action',
                    action='PUBLISH table_script_run={res_type:"action",table:"glbl.localita:localita_script",selectionName:"myselection"};')
    
    def test_2_launch_tree(self,pane):
        """Launch test from tree"""
        box = pane.div(datapath='test2',height='200px')
        self.table_script_resource_tree(box,res_type='action',table='glbl.localita',gridId='mygrid',selectionName='myselection')
        