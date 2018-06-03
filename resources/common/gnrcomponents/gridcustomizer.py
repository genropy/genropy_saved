# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for GridCustomizer:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
DEFAULT_MD_MODE = 'STD'


class GridCustomizer(BaseComponent):
    py_requires = 'gnrcomponents/framegrid:FrameGrid'

    def gc_gridInputCostomizerConfig_struct(self, struct):
        r=struct.view().rows()
        r.checkboxcolumn('enabled', name=' ')
        r.cell('field', name='!!Field',width='12em')
        r.cell('name', name='!!Header',width='25em', edit=True)
        r.cell('width', name='!!Width',edit=True)
        r.cell('format', name='!!Format',edit=True)
        r.cell('style', name='!!Style',edit=True,width='100%')

    def gc_gridPrintCostomizerConfig_struct(self, struct):
        r=struct.view().rows()
        r.checkboxcolumn('enabled', name=' ')
        r.cell('field', name='!!Field',width='12em')
        r.cell('name', name='!!Header',width='25em', edit=True)
        r.cell('mm_width', name='!!mm width',edit=True,dtype='L')
        r.cell('format', name='!!Format',edit=True)
        r.cell('style', name='!!Style',edit=True,width='100%')


    def gc_gridInputCostomizerConfig(self, parent,field=None,datapath=None,**kwargs):
        pane = parent.contentPane(**kwargs)
        pane.bagGrid(storepath='#FORM.record.%s' %field,pbl_classes=True,title='!!Grid input configurator',
                   datapath='.gridInputCostomizer',
                   struct=self.gc_gridInputCostomizerConfig_struct,addrow=False,delrow=False)

    def gc_gridPrintCostomizerConfig(self, parent,field=None,datapath=None,**kwargs):
        pane = parent.contentPane(**kwargs)
        pane.bagGrid(storepath='#FORM.record.%s' %field,pbl_classes=True,
                   datapath='#FORM.conf_print',title='!!Print grid configurator',
                   grid_selfDragRows=True,
                   struct=self.gc_gridPrintCostomizerConfig_struct,addrow=False,delrow=False)

    @struct_method
    def gc_gridCustomizerEditor(self,parent,gridField=None,printField=None,
                            gridResource=None,gridTable=None,md_mode=None,datapath=None,**kwargs):
        tc = parent.tabContainer(datapath=datapath or '.gridCustomizer',**kwargs)
        structures = self._gc_gridCustomizerStructures(table=gridTable,resource=gridResource)
        tc.data('.base_structures',structures)
        tc.dataController("""
        var current_cells = base_structures.getItem(md_mode+'.view_0.rows_0');
        var default_rows = new gnr.GnrBag();
        var v;
        current_cells.forEach(function(n){
            if(n.attr.hidden){
                return;
            }
            v = objectExtract(n.attr,'field,name,width,format,style,mm_width',true);
            v.enabled = true;
            default_rows.setItem(n.attr.field.replace(/\W/g, '_'),new gnr.GnrBag(v))
        });
        var that = this;
        var cb = function(field){
            var dflt_val = default_rows.deepCopy();
            var curr_rows = that.getRelativeData('#FORM.record.'+field);
            if(!curr_rows){
                that.setRelativeData('#FORM.record.'+field,dflt_val)
            }else{
                dflt_val.forEach(function(n){
                    if(!curr_rows.getNode(n.label)){
                        curr_rows.setItem(n.label,n.getValue())
                    }
                });
            }
        }
        if(gridField){
            cb(gridField);
        }
        if(printField){
            cb(printField);
        }

        """,
            _fired='^#FORM.controller.loaded',base_structures='=.base_structures',
            gridField=gridField,printField=printField,md_mode=md_mode or DEFAULT_MD_MODE)
        if gridField:
            self.gc_gridInputCostomizerConfig(tc,field=gridField,
                                        margin='2px',
                                        title='!!Grid input')
        if printField:
            self.gc_gridPrintCostomizerConfig(tc,field=printField,
                                        margin='2px',
                                        title='!!Print output')

    def _gc_gridCustomizerStructures(self,table=None,resource=None):
        tblobj = self.db.table(table)
        view = self.site.getDummyPage(resources=resource,table=table)
        fullstruct = self.newGridStruct(maintable=table)
        view.struct(fullstruct)
        result = Bag()
        modes = dictExtract(tblobj.attributes,'md_mode_') or {DEFAULT_MD_MODE:'STANDARD'}
        for mode in modes.keys():
            mode_struct = fullstruct.deepcopy()
            result[mode] = mode_struct
            cells = mode_struct['view_0.rows_0']
            for c in cells.nodes:
                colobj = tblobj.column(c.attr['field'])
                if colobj is not None and colobj.attributes.get('md_mode') and colobj.attributes.get('md_mode')!=mode:
                    cells.popNode(c.label)
        return result
    
    @struct_method
    def gc_gridCustomizer(self,grid,resource=None,md_mode=None,struct_customizer=None):
        table = grid.attributes['table']
        tblobj = self.db.table(table)
        controller = grid.dataController(datapath='.md_customizer')
        md_mode = md_mode or DEFAULT_MD_MODE
        md_structures = self._gc_gridCustomizerStructures(table=table,resource=resource)
        md_fkeys = tblobj.md_fkeys()
        controller.data('.md_fkeys',Bag(md_fkeys))
        controller.data('.md_structures',md_structures)
        controller.data('.main_column',md_fkeys[DEFAULT_MD_MODE])

        grid.data(grid.attributes.get('structpath','.struct'),md_structures[DEFAULT_MD_MODE])
        controller.dataFormula('.main_column',"md_fkeys.getItem(md_mode)",
                                md_mode=md_mode or DEFAULT_MD_MODE,
                                md_fkeys='=.md_fkeys')
        controller.dataController("""var md_struct = md_structures.getItem(md_mode).deepCopy();
                                    if(struct_customizer){
                                        var struct_cells = md_struct.getItem('view_0.rows_0');
                                        var cellNode;
                                        struct_customizer.values().forEach(function(v){
                                            v = v.asDict()
                                            cellNode = struct_cells.getNodeByAttr('field',objectPop(v,'field'))
                                            if(!cellNode){
                                                return;
                                            }
                                            if(!objectPop(v,'enabled')){
                                                cellNode.attr.hidden = true;
                                                return;
                                            }
                                            objectUpdate(cellNode.attr,v);
                                        });
                                    }
                                    grid.setRelativeData(grid.attr.structpath,md_struct);
                                  """,md_structures='=.md_structures',grid=grid,md_mode=md_mode,
                                  struct_customizer=struct_customizer,
                                    default_md_mode=DEFAULT_MD_MODE,_delay=1)


