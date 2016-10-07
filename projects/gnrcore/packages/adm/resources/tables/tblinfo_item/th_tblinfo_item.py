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
        left = bc.roundedGroupFrame(title='Source',region='left',width='200px')
        left.dataFormula('#FORM.currentTable','tbl',tbl='^#FORM.record.tbl')
        bc.dataRpc('#FORM.sourceTreeData', self.relationExplorer, 
                            table='^#FORM.currentTable', dosort=False)
        left.tree(storepath='#FORM.sourceTreeData', 
                    persist=False,
                    inspect='shift', #labelAttribute='label',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
                    onDrag_fsource=self.fsource_onDrag(),
                    draggable=True,
                    dragClass='draggedItem',
                    onChecked=True,
                    selected_fieldpath='.selpath',
                    getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                    getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")
        right = bc.roundedGroupFrame(title='Current data',region='center')
        bar = right.top.bar.replaceSlots('#','#,del_element,add_group')
        bar.del_element.slotButton('Delete')
        bar.add_group.slotButton('Add folder',action="""
            data =data || new gnr.GnrBag();
            caption = caption || 'Untitled Group';
            var label = currentDestSelectedPath && data.getItem(currentDestSelectedPath)?'g_'+data.getItem(currentDestSelectedPath).len():'g_0';
            var dp = currentDestSelectedPath?currentDestSelectedPath+'.'+label:label;
            data.setItem(dp,new gnr.GnrBag(),{caption:caption});
            """,data='=#FORM.record.data',bc=bc.js_widget,currentDestSelectedPath='=#FORM.currentDestSelectedPath',
                ask=dict(title='Nuovo gruppo',fields=[dict(name='caption',lbl='Caption')]))
        right.tree(storepath='#FORM.record.data', 
                    #onDrag=self.onDrag(),
                    _class='fieldsTree',
                    hideValues=True,
                    getLabel="""function(node){
                          
                          return node.attr.fieldpath || node.attr.caption || node.label;
                      }""",
                    onDrop_fsource="""
                        if(!dropInfo.treeItem._value){
                            return false;
                        }else{
                            var v = dropInfo.treeItem._value;
                            data.forEach(function(attr){
                                    v.setItem('n_'+v.len(),null,objectUpdate({},attr));
                                })
                            
                        }
                    """,
                    dropTarget=True,
                    selectedPath='#FORM.currentDestSelectedPath',
                    draggable=True,dragClass='draggedItem',
                    selectedLabelClass='selectedTreeNode')

    def fsource_onDrag(self):
        return """var children=treeItem.getValue('static')
                    console.log('children',children)
                  if(!children){
                      var fieldpath=treeItem.attr.fieldpath;
                      dragValues['fsource']=[treeItem.attr];
                      console.log('singolo',dragValues['fsource'])
                      return
                  }
                   result=[];
                   children.forEach(function(n){
                        if (n.attr.checked){result.push(n.attr);
                    }},'static');
                   dragValues['fsource']= result; 
                   console.log('gruppo',dragValues['fsource'])
               """

    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if not record['data']:
            record['data'] = Bag()
            record['data'].setItem('root',Bag())

    def th_options(self):
        return dict(dialog_parentRatio=0.95)
