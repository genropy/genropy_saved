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
        left = bc.roundedGroupFrame(title='Source',region='left',width='50%')
        left.dataFormula('#FORM.currentTable','tbl',tbl='^#FORM.record.tbl')
        bc.dataRpc('#FORM.sourceTreeData', self.relationExplorer, 
                            table='^#FORM.currentTable', dosort=False)
        tree = left.treeGrid(storepath='#FORM.sourceTreeData', 
                    #onDrag=self.onDrag(),
                    draggable=True,
                    dragClass='draggedItem',headers=True)
        tree.column('fieldpath',header='Field') 
        tree.column('dtype',size=40,header='DT')
        tree.column('caption',header='Caption',size=200)
        right = bc.roundedGroupFrame(title='Current data',region='center')
        bar = right.top.bar.replaceSlots('#','#,del_element,add_group')
        bar.del_element.slotButton('Delete')
        bar.add_group.slotButton('Add folder',action="""
            data =data || new gnr.GnrBag();
            caption = caption || 'Untitled Group';
            var label = currentDestSelectedPath && data.getItem(currentDestSelectedPath)?'g_'+data.getItem(currentDestSelectedPath).len():'g_0';
            var dp = currentDestSelectedPath?currentDestSelectedPath+'.'+label:label;
            data.setItem(dp,new gnr.GnrBag(),{caption:caption});
            """,data='=#FORM.record.data',currentDestSelectedPath='=#FORM.currentDestSelectedPath',
                ask=dict(title='Nuovo gruppo',fields=[dict(name='caption',lbl='Caption')]))
        tree = right.treeGrid(storepath='#FORM.record.data', 
                    #onDrag=self.onDrag(),
                    selectedPath='#FORM.currentDestSelectedPath',
                    draggable=True,
                    dragClass='draggedItem',headers=True)


        tree.column('fieldpath',header='Field') 
        tree.column('dtype',size=40,header='DT')
        tree.column('caption',header='Caption',size=200)

    def th_options(self):
        return dict(dialog_parentRatio=0.95)
