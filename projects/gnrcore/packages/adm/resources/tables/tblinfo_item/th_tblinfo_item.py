#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('item_type')
        r.fieldcell('data')
        r.fieldcell('tblid')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')

class AuthItemView(View):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')

class QTREEItemView(View):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')

class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('item_type')
        fb.field('data')
        fb.field('tblid')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class ConfTreeItemForm(BaseComponent):
    js_requires = 'adm_configurator'
    def th_form(self, form):
        bc = form.center.borderContainer()
        left = bc.roundedGroupFrame(title='Source',region='left',width='250px',splitter=True)
        left.dataFormula('#FORM.currentTable','tblid',tblid='^#FORM.record.tblid')
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
        bar.del_element.slotButton('Delete',action="""
            if(currentDestSelectedPath&&data){
                data.popNode(currentDestSelectedPath);
            }
            """,data='=#FORM.record.data',currentDestSelectedPath="=#FORM.currentDestSelectedPath")
        bar.add_group.slotButton('Add folder',action="""
            data =data || new gnr.GnrBag();
            caption = caption || 'Untitled Group';
            var selnode = data.getNode(currentDestSelectedPath || '#0');
            if(!selnode){
                selnode = data.getNode('root');
            }
            if(selnode.attr.dtype){
                selnode = selnode.getParentNode();
            }
            var v =  selnode.getValue();
            var label ='n_'+timeStamp();
            v.setItem(label,new gnr.GnrBag(),{caption:caption});
            """,data='=#FORM.record.data',bc=bc.js_widget,currentDestSelectedPath='=#FORM.currentDestSelectedPath',
                ask=dict(title='Folder name',fields=[dict(name='caption',lbl='Caption')]))
        tree = right.treeGrid(storepath='#FORM.record.data', 
                    headers=True,
                    autoCollapse=False,
                    _class='fieldsTree',
                    hideValues=True,
                    nodeId='infoItemTree_%(formId)s' %form.attributes,
                    onDrop_selfdrag_path="""ConfTreeEditor.selfDragDropTree(this,data,dropInfo);""",
                    onDrag='dragValues["selfdrag_path"]= dragValues["treenode"]["relpath"];',
                    dropTargetCb="""
                        if(!dropInfo.selfdrop&&dropInfo.treeItem.attr.dtype){
                            return false;
                        }
                        return true;
                    """,
                    onDrop_fsource="""
                        if(dropInfo.treeItem.attr.dtype){
                            return false;
                        }else{
                            var v = dropInfo.treeItem._value;
                            data.forEach(function(attr){
                                    v.setItem('n_'+timeStamp(),null,objectUpdate({},attr));
                                })
                        }
                    """,
                    dropTarget=True,
                    selectedPath='#FORM.currentDestSelectedPath',
                    draggable=True,dragClass='draggedItem',
                    selectedLabelClass='selectedTreeRow',
                    connect_ondblclick="""
                                    var item =  dijit.getEnclosingWidget($1.target).item
                                    var row = item.attr; 
                                    genro.dlg.prompt("Edit item",
                                    {dflt:new gnr.GnrBag(row),
                                    widget:[{value:'^.caption',lbl:'Caption'},
                                            {value:'^.fullcaption',lbl:'Full caption'}],
                                    action:function(res){
                                        objectUpdate(row,res.asDict(),true);
                                        item.updAttributes(row,true);
                                    }});
                                                """)
        tree.column('caption',header='Caption')
        tree.column('fullcaption',size=160,header='Full caption')
        tree.column('dtype',size=40,header='DT')
        tree.column('fieldpath',header='Field',size=320)

    def fsource_onDrag(self):
        return """var children=treeItem.getValue('static')
                  if(!children){
                      var fieldpath=treeItem.attr.fieldpath;
                      dragValues['fsource']=[treeItem.attr];
                      return
                  }
                   result=[];
                   children.forEach(function(n){
                        if (n.attr.checked && !n._value){result.push(n.attr);
                    }},'static');
                   dragValues['fsource']= result; 
               """

    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if not record['data']:
            record['data'] = Bag()
            record['data'].setItem('root',Bag(),caption='Root')

    def th_options(self):
        return dict(dialog_parentRatio=0.95,showtoolbar=False)
