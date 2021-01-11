# -*- coding: utf-8 -*-
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
from gnr.web.gnrbaseclasses import BaseComponent,page_proxy
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
DEFAULT_MD_MODE = 'STD'

    
@page_proxy
class MasterDetail(BaseComponent):
    py_requires = 'gnrcomponents/framegrid:FrameGrid'
    master_md_mode = None
    detail_grid_customizer = None
    detail_tbl = None
    detail_viewResource =None

    @extract_kwargs(default=True)
    def detailsGrid(self,pane,storepath=None,nodeId=None,title=None,
                    datapath='#FORM.details',pbl_classes=True,table=None,
                    md_mode=None,struct_customizer=None,
                    viewResource=None,canSort=False,
                    default_kwargs=None,**kwargs):
        tbl = table or self.detail_tbl
        default_kwargs.setdefault('main_column','=.md_customizer.main_column')
        frame = pane.bagGrid(storepath=storepath,
                        table=tbl,title=title,
                        datapath=datapath,
                        pbl_classes=pbl_classes,
                        nodeId=nodeId or 'detailsGrid',
                        grid_canSort=canSort,
                        grid_remoteRowController= self.rowController,
                        grid_remoteRowController_default = default_kwargs,
                        grid_selfDragRows=True,
                        **kwargs)
        pkg,tblname = tbl.split('.')
        viewResource = viewResource or 'th_{tbl}:{viewResourceClass}'.format(tbl=tblname,
                                                                            viewResourceClass=self.detail_viewResource)
        self.customizeGrid(frame.grid,resource=viewResource,
                                md_mode=md_mode or '^#FORM.record.{md_mode}'.format(md_mode=self.master_md_mode),
                                struct_customizer=struct_customizer or '=#FORM.record.{}'.format(self.detail_grid_customizer))
        self.detailsCustomization(frame)

        return frame
    
    def detailsCustomization(self,frame):
        return

    def inputCustomizer_struct(self, struct):
        r=struct.view().rows()
        r.checkboxcolumn('enabled', name=' ')
        r.cell('field', name='!!Field',width='12em')
        r.cell('name', name='!!Header',width='25em', edit=True)
        r.cell('width', name='!!Width',edit=True)
        r.cell('format', name='!!Format',edit=True)
        r.cell('caption_field', name='!!Caption field',edit=True,width='15em')
        r.cell('style', name='!!Style',edit=True,width='100%')

    def printCustomizer_struct(self, struct):
        r=struct.view().rows()
        r.checkboxcolumn('enabled', name=' ')
        r.cell('field', name='!!Field',width='12em')
        r.cell('name', name='!!Header',width='25em', edit=True)
        r.cell('mm_width', name='!!mm width',edit=True,dtype='L')
        r.cell('format', name='!!Format',edit=True)
        r.cell('style', name='!!Style',edit=True,width='100%')


    def inputCustomizer(self, parent,field=None,datapath=None,**kwargs):
        pane = parent.contentPane(**kwargs)
        pane.bagGrid(storepath='#FORM.record.%s' %field,pbl_classes=True,title='!!Grid input configurator',
                   datapath='.gridInputCostomizer',
                    grid_selfDragRows=True,
                   struct=self.inputCustomizer_struct,addrow=False,delrow=False)

    def printCustomizer(self, parent,field=None,table=None,datapath=None,**kwargs):
        pane = parent.contentPane(**kwargs)
        pane.bagGrid(storepath='#FORM.record.%s' %field,pbl_classes=True,
                   datapath='#FORM.conf_print',title='!!Print grid configurator',
                   grid_selfDragRows=True,
                   struct=self.printCustomizer_struct,addrow=False,delrow=False)

    def configurator(self,parent,gridField=None,printField=None,
                gridResource=None,gridTable=None,md_mode=None,datapath=None,**kwargs):
        tc = parent.tabContainer(datapath=datapath or '.gridCustomizer',**kwargs)
        structures = self.getStructures(table=gridTable,resource=gridResource)
        tc.data('.base_structures',structures)
        tc.dataController("""
        if(this.form.isNewRecord()){
            return;
        }        
        var that = this;
        var cb = function(root,field){
            var default_rows = new gnr.GnrBag();
            var v;
            base_structures.getItem(root).getItem(md_mode+'.view_0.rows_0').forEach(function(n){
                if(n.attr.hidden && !n.attr.hiddenIsDefault){
                    return;
                }
                v = objectExtract(n.attr,'caption_field,field,name,width,format,style,mm_width',true);
                v.enabled = !n.attr.hiddenIsDefault;
                default_rows.setItem(n.attr.field.replace(/\W/g, '_'),new gnr.GnrBag(v))
            });
            var curr_rows = that.getRelativeData('#FORM.record.'+field);
            if(!curr_rows){
                that.setRelativeData('#FORM.record.'+field,default_rows)
            }else{
                default_rows.forEach(function(n){
                    if(!curr_rows.getNode(n.label)){
                        curr_rows.setItem(n.label,n.getValue())
                    }
                });
            }
        }
        if(gridField){
            cb('struct_grid',gridField);
        }
        if(printField){
            cb('struct_print',printField);
        }

        """,
            _fired='^#FORM.controller.loaded',base_structures='=.base_structures',
            gridField=gridField,printField=printField,md_mode=md_mode or DEFAULT_MD_MODE)
        if gridField:
            self.inputCustomizer(tc,field=gridField,
                                        margin='2px',
                                        title='!!Grid input')
        if printField:
            bc = tc.borderContainer(title='!!Print output')
            self.printCustomizer(bc,field=printField,table=gridTable,region='center',margin='2px')

    def customizeGrid(self,grid,resource=None,md_mode=None,struct_customizer=None):
        table = grid.attributes['table']
        tblobj = self.db.table(table)
        controller = grid.dataController(datapath='.md_customizer')
        default_md_mode = tblobj.attributes.get('default_md_mode') or  DEFAULT_MD_MODE
        md_mode = md_mode or default_md_mode
        md_structures = self.getStructures(table=table,resource=resource)['struct_grid']
        md_fkeys = tblobj.md_fkeys()
        controller.data('.md_fkeys',Bag(md_fkeys))
        controller.data('.md_structures',md_structures)
        controller.data('.main_column',md_fkeys[default_md_mode])
        grid.data(grid.attributes.get('structpath','.struct'),md_structures[default_md_mode])
        controller.dataFormula('.main_column',"md_fkeys.getItem(md_mode)",
                                md_mode=md_mode or default_md_mode,
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
                                    default_md_mode=default_md_mode,_delay=1)

    def getStructures(self,table=None,resource=None):
        tblobj = self.db.table(table)
        view = self.site.virtualPage(table=table,table_resources=resource)
        fullstruct = self.newGridStruct(maintable=table)
        view.th_struct(fullstruct)
        struct_grid = Bag()
        struct_print = Bag()
        modes = dictExtract(tblobj.attributes,'md_mode_') or {DEFAULT_MD_MODE:'STANDARD'}
        for mode in modes.keys():
            mode_struct = fullstruct.deepcopy()
            cells = mode_struct['view_0.rows_0']
            for cell_label,cell_attr in cells.digest('#k,#a'):
                colobj = tblobj.column(cell_attr['field'])
                if colobj is not None and colobj.attributes.get('md_mode') and colobj.attributes.get('md_mode')!=mode:
                    cells.popNode(cell_label)
            struct_grid[mode] = self.gridstruct_default(mode_struct.deepcopy())
            struct_print[mode] = self.printstruct_default(mode_struct.deepcopy())
        return Bag(dict(struct_grid=struct_grid,struct_print=struct_print))

    def gridstruct_default(self,mode_struct):
        cells = mode_struct['view_0.rows_0']
        for cell_label,cell_attr in cells.digest('#k,#a'):
            if cell_attr.get('print') =='*':
                cells.pop(cell_label)
        return mode_struct

    def printstruct_default(self,mode_struct):
        cells = mode_struct['view_0.rows_0']
        for cell_label,cell_attr in cells.digest('#k,#a'):
            printattr = dictExtract(cell_attr,'print_',pop=True)
            if not printattr:
                cells.popNode(cell_label)
            else:
                cell_attr.update(printattr)
                cell_attr.pop('width',None)
                cell_attr.pop('edit',None)
                cell_attr.pop('tag',None)

        return mode_struct

    def customizePrint(self,printInstance,viewResource=None,md_mode=None,customizerBag=None,table=None):
        table = table or printInstance.rows_table or printInstance.tblobj.fullname
        default_struct = self.getStructures(table=table,resource=viewResource)['struct_print'][md_mode]
        printInstance.grid_columns = printInstance.gridColumnsFromStruct(struct=default_struct)
        if customizerBag:
            filtered_grid_columns = []
            colsdict = {d['field']:dict(d) for d in printInstance.grid_columns}
            for v in customizerBag.values():
                d = colsdict.get(v['field']) or {}
                custattr = dict(field=v['field'],name=v['name'],
                                mm_width=v['mm_width'],
                                format=v['format'],
                                style=v['style'],
                                totalize=v['totalize'])
                d.update(custattr)
                if v['enabled']:
                    d['hidden'] = False
                else:
                    d['hidden'] = True
                filtered_grid_columns.append(d)
            printInstance.grid_columns = filtered_grid_columns
            printInstance.grid_columnsets = dict()
        return printInstance.grid_columns
