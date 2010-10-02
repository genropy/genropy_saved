# -*- coding: UTF-8 -*-

# grid_configurator.py
# Created by Francesco Porcari on 2010-10-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class GridConfigurator(BaseComponent):
    js_requires='gnrcomponents/grid_configurator/grid_configurator'
    css_requires='gnrcomponents/grid_configurator/grid_configurator'

    def onMain_grid_configurator(self):
        page = self.pageSource()
        root=page.div(nodeId='grid_configurator_root',datapath='gnr.plugin.grid_configurator')
        root.dataController(""" 
                                var grid = grid_configurator[1].grid;
                                
                                var attr=grid.sourceNode.attr;
                                SET .dialog.gridId = attr.nodeId;
                                SET .dialog.table = attr.table;
                                SET .dialog.title = 'Grid configuration: '+attr.nodeId;
                                SET .dialog.data.struct_to_edit = grid_conf.get_struct_to_edit(grid.sourceNode);
                                FIRE .dialog.open;
                             """,
                               subscribe_grid_configurator=True)
        dlg = self.simpleDialog(root,title='^.title',datapath='.dialog',height='300px',width='600px',
                         cb_center=self.grid_configurator_dialog_center,dlgId='grid_configurator_dialog')
        dlg.dataController("""
                            grid_conf.from_struct_to_edit(genro.nodeById(gridId),currGridStruct);
                            FIRE .close;
                            """,_fired="^.save",currGridStruct='=.data.struct_to_edit',gridId='=.gridId')
                         
                         
    def grid_configurator_dialog_center(self,parentBc,**kwargs):
        bc=parentBc.borderContainer(**kwargs)
        top = bc.contentPane(region='top').toolbar()
        top.button('!!Add row',action='SET .data.struct_to_edit.#id = new gnr.GnrBag();')
        top.button('!!Del row')
        left = bc.contentPane(region='left',width='150px')
        left.dataRpc('.fieldstree','relationExplorer',table='^.table', omit='_',_onResult='FIRE .maketree')
        left.tree(storepath='.fieldstree',persist=False,
                    inspect='shift', labelAttribute='caption',
                    _class='fieldsTree',_fired='^.maketree',
                    hideValues=True,
                    getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}',
                    dndController="dijit._tree.dndSource",
                    onDndDrop="function(){this.onDndCancel();}::JS",
                    checkAcceptance='function(){return false;}::JS',
                    checkItemAcceptance='function(){return false;}::JS')

        iv = bc.contentPane(region='center',datapath='.data').includedView(storepath='.struct_to_edit',struct=self.grid_configurator_struct(),datamode='bag',
                                        nodeId='grid_configurator_grid',editorEnabled=True)

        gridEditor = iv.gridEditor()
        gridEditor.numberTextBox(gridcell='order')
        gridEditor.textBox(gridcell='field')
        gridEditor.textBox(gridcell='name')
        gridEditor.textBox(gridcell='width')


    
    def grid_configurator_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('order',dtype='L',name='Order', width='5em')
        r.cell('field', name='Field', width='15em')
        r.cell('name', name='Name', width='15em')
        r.cell('dtype', name='Dtype', width='5em')
        r.cell('width', name='Width', width='5em')
        r.cell('classes', name='Classes', width='10em')
        r.cell('cell_classes', name='cellClasses', width='10em')
        r.cell('header_classes', name='headerClasses', width='10em')
        r.cell('view',name='View',width='10em')
        r.cell('subrow',name='Subrow',width='10em')
        return struct
    