# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Test batch handler"""
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/batch_handler/batch_handler:TableScriptRunner,gnrcomponents/batch_handler/batch_handler:BatchMonitor"

    maintable='glbl.localita'
    defaultscript='localita_script'
    
    def windowTitle(self):
        return 'Test Batch Handler'
    
    def loc_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.fieldcell('nome', name='Nome', width='10em')
        r.fieldcell('provincia', name='Provincia', width='10em')
        r.fieldcell('@provincia.@regione.nome', name='Regione', width='10em')
        return struct
        
    def test_0_root(self,pane):
        """Not real test: common stuff"""
        bc = pane.borderContainer(height='300px',datapath='test0')
        self.bm_monitor_pane(bc.contentPane(region='right',width='200px',splitter=True))
        fb = bc.contentPane(region='top').formbuilder(cols=1)
        fb.textbox(value='^.start',lbl='Starts with:')
        fb.button('addcol',action="""genro._data.setItem('grids.mygrid.struct.view_0.rows_0.cell_3',null,{width:'12em',name:'Nome Provincia',field:'@provincia.nome',tag:'cell'})""")
        viewpane=bc.contentPane(region='center',datapath='.mygrid')
        viewpane.dataSelection('.selection',self.maintable,where="$nome ILIKE :seed || '%%'",seed='^.#parent.start',
                            columnsFromView='mygrid',
                            selectionName='*currsel',selectionId='mainselection')
        viewpane.includedView(storepath='.selection',struct=self.loc_struct(),nodeId='mygrid')
        
    def test_1_launch_button(self,pane):
        """Launch test from button"""
        parameters="""{res_type:"action",table:"%s",resource:"%s",selectionName:"currsel"}""" % (self.maintable,self.defaultscript)
        pane.button('Launch action',
                    action="PUBLISH table_script_run=%s;" % parameters)
    
    def test_2_launch_tree(self,pane):
        """Launch test from tree"""
        box = pane.div(datapath='test2',height='200px')
        self.table_script_resource_tree(box,res_type='action',table=self.maintable,gridId='mygrid',selectionName='currsel')
        
    def onMain_grid_configurator(self):
        page = self.pageSource()
        root=page.div(nodeId='grid_configurator_root',datapath='gnr.plugin.grid_configurator')
        root.dataController("""var e=grid_configurator[1];
                               var grid=e.grid;
                               var cell=e.cell;
                               var attr=grid.sourceNode.attr;
                               console.log(e);
                               SET .dialog.title='Grid configuration: '+attr.nodeId;
                               FIRE .dialog.open;""",
                               subscribe_grid_configurator=True)
        dlg = self.simpleDialog(root,title='^.title',datapath='.dialog',height='300px',width='400px',
                         cb_center=self.grid_configurator_dialog_center,dlgId='grid_configurator_dialog')
                         
                         
    def grid_configurator_dialog_center(self,parentBc,**kwargs):
        center=parentBc.contentPane(datapath='.pars',**kwargs)
        center.div('my configurator')
        center_attr = center.getNode('#0').attr
        dlg_attr = center.parentNode.parentbag.parentNode.attr
        dlg_attr['height'] = center_attr.get('height') or dlg_attr['height']
        dlg_attr['width'] = center_attr.get('width') or dlg_attr['width']