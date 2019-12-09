#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')

    def th_order(self):
        return '_row_count'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):
    js_requires = 'adm_configurator'

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=3, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        fb.field('rootpage')

        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='!!Users').plainTableHandler(relation='@users',picker=True,
                            picker_viewResource='ViewPicker',
                            pbl_classes=True,margin='2px')
        tc.contentPane(title='!!Tag').inlineTableHandler(relation='@tags',
                            viewResource='ViewFromGroup',
                            pbl_classes=True,margin='2px',addrow=False,picker='tag_id',
                            picker_condition='$child_count=0',
                            picker_viewResource=True)

        tc.contentPane(title='!!Config').dialogTableHandler(table='adm.user_config',
                                margin='2px',
                                viewResource='ViewFromGroup',
                                formResource='FormFromGroup')
        self.groupCustomMenu(tc.borderContainer(title='Custom menu'))

    def groupCustomMenu(self,bc):
        left = bc.roundedGroupFrame(title='Source',region='left',width='400px',splitter=True)
        bar = left.top.bar.replaceSlots('#','v,pickerpackages,2')   
        fb = bar.pickerpackages.formbuilder(cols=1,border_spacing='0px')   
        fb.checkBoxText(value='^#FORM.menuPickerPackages',lbl='Packages',popup=True,
                            values=','.join(self.db.packages.keys()),width='25em',cols=1)
        bc.dataRpc('#FORM.sourceTreeData', self.groupMenuSource, packages='^#FORM.menuPickerPackages')
        right = bc.roundedGroupFrame(title='Menu',region='center')
        left.tree(storepath='#FORM.sourceTreeData', 
                    persist=False,
                    inspect='shift', labelAttribute='label',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
                    onDrag_msource=self.msource_onDrag(),
                    draggable=True,
                    dragClass='draggedItem')

        right = bc.roundedGroupFrame(title='Current data',region='center')
        bar = right.top.bar.replaceSlots('#','#,del_element,add_group')
        bar.del_element.slotButton('Delete',action="""
            if(currentDestSelectedPath&&data){
                data.popNode(currentDestSelectedPath);
            }
            """,data='=#FORM.record.custom_menu',currentDestSelectedPath="=#FORM.currentDestSelectedPath")
        bar.add_group.slotButton('Add folder',action="""
            data = data || new gnr.GnrBag();
            label = label || 'Untitled Folder';
            var selnode = data.getNode(currentDestSelectedPath || '#0');
            if(!selnode){
                selnode = data.getNode('root');
                if(!selnode){
                    selnode = data.setItem('root',new gnr.GnrBag(),{label:label,tag:'branch'});
                }
            }
            if(selnode.attr.dtype){
                selnode = selnode.getParentNode();
            }
            var v =  selnode.getValue();
            v.setItem('#id',new gnr.GnrBag(),{label:label,tag:'branch',tags:tags});
            """,data='=#FORM.record.custom_menu',bc=bc.js_widget,currentDestSelectedPath='=#FORM.currentDestSelectedPath',
                ask=dict(title='Folder name',fields=[dict(name='label',lbl='Label'),dict(name='tags',lbl='Tags')]))
        tree = right.treeGrid(storepath='#FORM.record.custom_menu', 
                    headers=True,
                    autoCollapse=False,
                    _class='fieldsTree',
                    hideValues=True,
                    nodeId='groupMenuTree',
                    onDrop_selfdrag_path="""ConfTreeEditor.selfDragDropTree(this,data,dropInfo);""",
                    onDrag='dragValues["selfdrag_path"]= dragValues["treenode"]["relpath"];',
                    dropTargetCb="""
                        console.log(dropInfo.treeItem.attr.tag);
                        if(!dropInfo.selfdrop && dropInfo.treeItem.attr.tag!='branch'){
                            return false;
                        }
                        return true;
                    """,
                    onDrop_msource="""
                        if(dropInfo.treeItem.attr.tag!='branch'){
                            return false;
                        }else{
                            var v = dropInfo.treeItem._value;
                            data.forEach(function(attr){
                                    v.setItem('#id',null,objectUpdate({},attr));
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
                                    widget:[{value:'^.label',lbl:'Caption'},
                                            {value:'^.tags',lbl:'Tags'}],
                                    action:function(res){
                                        objectUpdate(row,res.asDict(),true);
                                        item.updAttributes(row,true);
                                    }});
                                                """)
        tree.column('label',header='Caption')
        tree.column('tags',size=160,header='Tags')
    
    @public_method
    def groupMenuSource(self,packages=None):
        if not packages:
            return
        result = Bag()
        packages = packages.split(',')
        for pkgid,pkgobj in self.db.application.packages.items():
            if pkgid in packages and pkgobj.pkgMenu:
                result[pkgid] = Bag(pkgobj.pkgMenu)
        return result

    def msource_onDrag(self):
        return """var children=treeItem.getValue('static')
                  if(!children){
                      var fieldpath=treeItem.attr.fieldpath;
                      dragValues['msource']=[treeItem.attr];
                      return
                  }
                   var result=[];
                   children.forEach(function(n){
                        if (!n._value){result.push(n.attr);
                    }},'static');
                   dragValues['fsource']= result; 

               """
    
    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if not record['custom_menu']:
            record['custom_menu'] = Bag()
            record['custom_menu'].setItem('root',Bag(),label='Root',tag='branch')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
