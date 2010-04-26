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

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver

def _getTreeRowCaption(tblobj):
    if hasattr(tblobj,'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code,$caption'

class HTableHandler(BaseComponent):
    css_requires='public'
    def htableHandler(self,parent,nodeId=None,datapath=None,table=None,rootpath=None,label=None,
                    editMode='bc',dialogPars=None,disabled=None):
        """
        .tree: tree data:
                        store
                        **selected elements
        .edit (sym #nodeId_edit): pane data: **controllers
                                       form
                                       record
        formId:nodeId_form 
        controllerNodeId:nodeId_edit
        treeId:nodeId_tree
        editMode:'bc','sc','dlg'
        """
        
        formPanePars = dict(selectedPage='^.edit.selectedPage')
        if editMode=='bc':
            bc = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px')
            treepane = bc.borderContainer(region='left',width='40%',splitter=True)
            formPanePars['region'] = 'center'            
            formBC = bc.borderContainer(region='center')
            
        elif editMode=='sc':
            sc = parent.stackContainer(region='center',datapath=datapath,nodeId=nodeId,
                                        selectedPage='^.selectedPage',margin='2px')
            treepane = sc.borderContainer(pageName='tree')
            formPanePars['pageName'] = 'edit'
            formBC = sc.borderContainer(region='center')
            
        elif editMode=='dlg':
            assert dialogPars,'for editMode == "dlg" dialogPars are mandatory'
            treepane = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px')
            formBC = self.simpleDialog(treepane,dlgId='%s_dlg' %nodeId,
                                    cb_bottom=self.ht_edit_dlg_bottom,**dialogPars)
            formPanePars['region'] = 'center'
            
        recordlabel = formBC.contentPane(region='top',_class='pbl_roundedGroupLabel')
        recordlabel.div(nodeId='%s_nav' %nodeId)
        formpane = formBC.stackContainer(pageName='edit',**formPanePars)
        recordlabel.dataController("""
                            var pathlist = currpath.split('.');
                            var rootnode = genro.nodeById(labelNodeId).clearValue().freeze();
                            var label,path2set;
                            for(var i=0;i<pathlist.length-1;i++){
                                label = pathlist[i];
                                path2set = path2set?path2set+'.'+label:label;
                                var action = "this.setRelativeData('.tree.path','"+path2set+"');";
                                rootnode._('a',{content:label,connect_onclick:action,href:'#','float':'left'});
                                rootnode._('div',{content:'-',float:'left'})
                            }
                            rootnode._('div',{content:title,'float':'left'});
                            rootnode.unfreeze();

                            """,title="^.edit.title",
                             currpath='=.tree.path',
                             labelNodeId='%s_nav' %nodeId)
        
        self.ht_tree(treepane,table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,editMode=editMode,label=label)
        self.ht_edit(formpane,table=table,nodeId=nodeId,disabled=disabled,
                        rootpath=rootpath,editMode=editMode)
                        
    def ht_edit_dlg_bottom(self,bc,**kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Back',baseClass='bottom_btn',float='right',margin='1px',fire='.close')
        return bottom
                
    def ht_edit(self,sc,table=None,nodeId=None,disabled=None,rootpath=None,editMode=None):
        formId='%s_form' %nodeId
        norecord = sc.contentPane(pageName='no_record').div('No record selected')
        bc = sc.borderContainer(pageName='record_selected')
        toolbar = bc.contentPane(region='top',overflow='hidden').toolbar(_class='standard_toolbar')
        self.ht_edit_toolbar(toolbar,nodeId=nodeId,disabled=disabled,editMode=None)
        bc.dataController("SET .edit.selectedPage=pkey?'record_selected':'no_record'",pkey="^.tree.pkey")
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){
                                genro.setData('#%s.tree.pkey',currPkey);
                                genro.setData('#%s.tree.path',currPkey.slice(rootpath.length-1));
                                };
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ %(nodeId,nodeId),rootpath=rootpath,
                            selPkey='^.tree.pkey',currPkey='=.edit.pkey',_if='selPkey!=currPkey',
                            formId=formId)
        bc.dataController("""     
                              var editNode = treestore.getNode(treepath);
                             if (destPkey!='*newrecord*'){
                                 var attr= editNode.attr;
                                 attr.caption = treeCaption;
                                 editNode.setAttr(attr);
                                 FIRE .edit.load;
                             }else{
                                SET .edit.pkey = savedPkey;
                                FIRE .edit.load;
                                editNode.refresh(true);
                             }
                             SET .tree.path = savedPkey.slice(rootpath.length-1);
                            
                         """,
                        _fired="^.edit.onSaved",destPkey='=.tree.pkey',
                        savedPkey='=.edit.savedPkey',rootpath=rootpath,
                        treepath='=.tree.path',treestore='=.tree.store',
                        treeCaption='=.edit.savedPkey?caption')
        
       #bc.dataRpc('dummy','deleteRecordCluster',data='.edit.record',)
       #bc.dataRpc('form.delete_result','deleteRecordCluster', data='=form.record?=genro.getFormChanges("formPane");', _POST=True,
       #                table=self.maintable,toDelete='^form.doDeleteRecord')
                        
        getattr(self,formId)(bc,region='center',table=table,
                              datapath='.edit.record',controllerPath='#%s.edit.form' %nodeId,
                              formId=formId,
                              disabled= disabled or '^#%s.edit.status.locked'%nodeId,
                              pkeyPath='#%s.edit.pkey' %nodeId)
        selected = dict()
        dfltConf = dict(code='code',parent_code='parent_code',child_code='child_code')
        tblobj = self.db.table(table)
        defaults = dict()
        if hasattr(tblobj,'htable_conf'):
            dfltConf = tblobj.htable_conf()        
        defaults['default_%s' %dfltConf['parent_code']] = '=.defaults.parent_code'
        
        self.formLoader(formId,datapath='#%s.edit' %nodeId,resultPath='.record',_fired='^.load',
                        table=table, pkey='=.pkey',**defaults)
        self.formSaver(formId,datapath='#%s.edit' %nodeId,resultPath='.savedPkey',_fired='^.save',
                        table=table,onSaved='FIRE .onSaved;',
                        rowcaption=_getTreeRowCaption(self.db.table(table)))

    def ht_edit_toolbar(self,toolbar,nodeId=None,disabled=None,editMode=None):
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.data('.edit.status.locked',True)
        if not disabled:
            disabled = '^.edit.status.locked'
            spacer.button('!!Unlock',fire='.edit.status.unlock',iconClass="tb_button icnBaseLocked",
                        showLabel=False,hidden='^.edit.status.unlocked')
            spacer.button('!!Lock',fire='.edit.status.lock',iconClass="tb_button icnBaseUnlocked", 
                        showLabel=False,hidden='^.edit.status.locked')
            toolbar.dataController("SET .edit.status.locked=true;",fired='^.edit.status.lock')
            toolbar.dataController("SET .edit.status.locked=false;",fired='^.edit.status.unlock') 
            toolbar.dataFormula(".edit.status.unlocked", "!locked",locked="^.edit.status.locked")
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.dataController("""genro.dom.removeClass(semaphoreId,"greenLight redLight yellowLight");
              if(isValid){
                 if(isChanged){
                     genro.dom.addClass(semaphoreId,"yellowLight");
                 }else{
                     genro.dom.addClass(semaphoreId,"greenLight");
                 }
              }else{
                    genro.dom.addClass(semaphoreId,"redLight");
              }
              """,isChanged="^.edit.form.changed",semaphoreId='%s_semaphore' %nodeId,
            isValid='^.edit.form.valid')
        spacer.div(nodeId='%s_semaphore' %nodeId,_class='semaphore',margin_top='3px',
                  hidden=disabled)  
        toolbar.dataController("SET .edit.title =recordCaption",recordCaption="^.edit.record?caption")
        toolbar.button('!!Save',fire=".edit.save", float='right',
                        iconClass="tb_button db_save",showLabel=False,
                        hidden=disabled)
        toolbar.button('!!Revert',fire=".edit.load", iconClass="tb_button db_revert",float='right',
                        showLabel=False,hidden=disabled)      
        toolbar.button('!!Add',action="""SET .edit.defaults.parent_code = GET .tree.code;
                                               SET .tree.pkey = '*newrecord*';
                                            """,iconClass='db_add tb_button',
                                            showLabel=False,hidden=disabled,float='right')
        toolbar.button('!!Delete',fire=".edit.delete",iconClass='db_del tb_button',
                                            showLabel=False,hidden=disabled,
                                            visible='^.edit.enableDelete',
                                            float='right')
        toolbar.dataFormula('.edit.enableDelete','child_count==0',child_count='^.tree.child_count')
        if editMode=='sc':
            toolbar.button('!!Tree',action="SET .selectedPage = 'tree';")
                                            
                                                                 
    def ht_tree(self,bc,table=None,nodeId=None,rootpath=None,disabled=None,editMode=None,label=None):
        labelbox = bc.contentPane(region='top',_class='pbl_roundedGroupLabel')
        labelbox.div(label,float='left')
        tblobj = self.db.table(table)
        center = bc.contentPane(region='center')
        center.data('.tree.store',self.ht_treeDataStore(table=table,rootpath=rootpath,rootcaption=tblobj.name_plural),
                    rootpath=rootpath)
                    
        connect_ondblclick=None
        if editMode=='sc':
            connect_ondblclick = 'SET .selectedPage = "edit";'
        elif editMode=='dlg':
            connect_ondblclick = 'FIRE #%s_dlg.open;' %nodeId
        center.tree(storepath ='.tree.store',
                    isTree =False,hideValues=True,
                    inspect ='shift',labelAttribute ='caption',
                    selected_pkey='.tree.pkey',selectedPath='.tree.path',  
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_child_count='.tree.child_count',
                    connect_ondblclick=connect_ondblclick)
                    
    def ht_treeDataStore(self,table=None,rootpath=None,rootcaption=None):
        tblobj= self.db.table(table)
        dfltConf = dict(code='code',parent_code='parent_code',child_code='child_code')
        result = Bag()
        if rootpath:
            row=tblobj.query(columns='*',where='$code=:code',code=rootpath).fetch()[0]
            caption=tblobj.recordCaption(row,rowcaption=_getTreeRowCaption(tblobj))
            rootlabel = row['child_code']
            pkey=row['pkey']
            _attributes=dict(row)
            rootpath=row['code']
            code=row[dfltConf['code']]
        else:
            caption=rootcaption
            rootlabel ='_root_'
            _attributes=dict()
            pkey=None
            code=None
            rootpath=None
        result.setItem(rootlabel, HTableResolver(table=table,rootpath=rootpath), caption=caption,pkey=pkey,code=code)#,_attributes=_attributes)
        return result
                     
class HTableResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False,
                 'table':None,
                 'rootpath':None,
                 '_page':None}
    classArgs=['table','rootpath']
            
    def load(self):
        db= self._page.db
        tblobj = db.table(self.table)
        dfltConf = dict(code='code',parent_code='parent_code',child_code='child_code')
        if hasattr(tblobj,'htable_conf'):
            dfltConf = tblobj.htable_conf()  
        rows = tblobj.query(columns='*,$child_count',where="COALESCE($parent_code,'')=:rootpath" ,
                     rootpath=self.rootpath or '',order_by='$child_code').fetch()
        children = Bag()
        for row in rows:
            child_count= row['child_count']
            if row['child_count']:
                value=HTableResolver(table=self.table,rootpath=row['code'],child_count=child_count)
            else:
                value=None
            children.setItem(row['child_code'], value,caption=tblobj.recordCaption(row,rowcaption=_getTreeRowCaption(tblobj)),pkey=row['pkey'],
                                                                                    code=row[dfltConf['code']],child_count=child_count)#_attributes=dict(row),
        return children
        
            
        
        