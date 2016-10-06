#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('item_type')
        r.fieldcell('data')
        r.fieldcell('user_group')
        r.fieldcell('tbl')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')


class AuthItemView(View):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')

class QTREEItemView(View):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('user_group')
        r.fieldcell('section')



class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('item_type')
        fb.field('data')
        fb.field('user_group')
        fb.field('tbl')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')


class AuthItemForm(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.column_config(bc.contentPane(region='center',datapath='.record'))

    def _columnsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname', width='14em', name='Field')
        r.cell('datatype', width='8em', name='Datatype')
        r.cell('name_long', width='15em', name='Name long')
        r.cell('auth_tags', width='15em', name='Auth tags',edit=True)


    def column_config(self,pane):
        pane.css('.virtualCol','color:green')
        frame = pane.bagGrid(frameCode='columnsGrid',title='Columns',struct=self._columnsgrid_struct,
                        storepath='#FORM.record.data',
                        datapath='#FORM.column_config_grid',
                        pbl_classes=True,
                        margin='2px',_class='pbl_roundedGroup',
                        addrow=False,delrow=False)


    def getColumnConfig(self,table=None):
        tblobj = self.db.table(table)
        result = Bag()
        for field,colobj in tblobj.model.columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T')),auth_tags=None))

        for field,colobj in tblobj.model.virtual_columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T'),auth_tags=None)),_customClasses='virtualCol')

        return result


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        currdata = record['data']
        record['data'] = self.getColumnConfig(record['tbl'])
        record['data'].update(currdata)

    def th_options(self):
        return dict(dialog_parentRatio=0.8)

class QTREEItemForm(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.field('name')
        fb.field('section')
        fb.field('user_group')
        center = bc.borderContainer(region='center',design='sidebar')
        center.contentPane(region='center').tree(storepath='#FORM.record.data',hideValues=True,nodeId='QTREEEditor_tree',
                                                selectedPath='#FORM.selectedTreePath',
                                                selectedLabelClass='selectedTreeNode',
                                                dropTarget=True,
                                                labelAttribute='name',
                                                draggable=True,
                                                editable='Shift',
                                                selfsubscribe_onSelected="genro.publish('QTREENodeEditor_currentPath',$1.item.getFullpath(null,genro._data))",
                                                onDrag='dragValues["layoutnode_path"]= dragValues["treenode"]["relpath"];',
                                                onDrop_fieldvars="""console.log('zzz',data);
                                                                        var dropPath = dropInfo.treeItem.getFullpath(null,this.getRelativeData(this.attr.storepath));
                                                                        genro.publish('insert_layout_element',{insertPath:dropPath || 'root'});
                                                                        """)
        center.contentPane(region='bottom',height='50%',splitter=True,overflow='hidden').bagNodeEditor(bagpath='curr_field_node',
            labelAttribute='label',addrow=True,delrow=True,addcol=True,nodeId='QTREENodeEditor',
            datapath='.bagNodeEditor')
        center.contentPane(region='left',border_right='1px solid silver',width='200px').fieldsTree(table='^#FORM.record.tbl')

    def th_options(self):
        return dict(dialog_parentRatio=0.8)


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if not record['data']:
            record['data'] = Bag(dict(root=Bag()))
