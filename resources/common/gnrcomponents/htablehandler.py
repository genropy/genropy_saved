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

class HTableHandler(BaseComponent):
    css_requires='public'
    def htableHandler(self,parentBC,nodeId=None,datapath=None,table=None,rootpath=None,
                    label=None,editMode='bc',disabled=None):
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
        parentBC.contentPane(region='top',_class='pbl_roundedGroupLabel').div(label)
        formPars = dict(selectedPage='^.edit.selectedPage')
        if editMode=='bc':
            bc = parentBC.borderContainer(region='center',datapath=datapath,nodeId=nodeId)
            treepane = bc.borderContainer(region='left',width='40%',splitter=True)
            formpane = bc.stackContainer(region='center',**formPars)
        elif editMode=='sc':
            sc = parentBC.stackContainer(region='center',datapath=datapath,nodeId=nodeId,
                                        selectedPage='^.selectedPage')
            treepane = sc.borderContainer(pageName='tree')
            formpane = sc.stackContainer(pageName='edit',**formPars)
        elif editMode=='dlg':
            raise
        self.ht_tree(treepane,table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,editMode=editMode)
        self.ht_edit(formpane,table=table,nodeId=nodeId,disabled=disabled)
        
    def ht_edit(self,sc,table=None,nodeId=None,disabled=None):
        formId='%s_form' %nodeId
        norecord = sc.contentPane(pageName='no_record').div('No record selected')
        bc = sc.contentPane(pageName='record_selected')
        bc.dataController("SET .edit.selectedPage=pkey?'record_selected':'no_record'",pkey="^.tree.pkey")
        toolbar = bc.contentPane(region='top',overflow='hidden',datapath='.edit').toolbar(height='20px')
        self.ht_form_toolbar(toolbar,nodeId=nodeId)
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){genro.setData('#%s.tree.pkey',currPkey);};
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ %nodeId,
                            selPkey='^.tree.pkey',currPkey='=.edit.pkey',_if='selPkey!=currPkey',
                            formId=formId)
        bc.dataController("""
                            console.log(treepath);
                            treestore.getNode(treepath).getParentNode().refresh(true);
                            FIRE .load;
                         """,
                        _fired="^.edit.onSaved",
                        treepath='=.tree.path',treestore='=.tree.store')

        getattr(self,formId)(bc,region='center',table=table,
                              datapath='.edit.record',controllerPath='#%s.edit.form' %nodeId,
                              formId=formId,
                              disabled='^#%s.edit.status.locked'%nodeId,
                              pkeyPath='#%s.edit.pkey' %nodeId)
        self.formLoader(formId,datapath='#%s.edit' %nodeId,resultPath='.record',_fired='^.load',
                        table=table, pkey='=.pkey')
        self.formSaver(formId,datapath='#%s.edit' %nodeId,resultPath='.savedPkey',_fired='^.save',
                        table=table,onSaved='FIRE .onSaved;')
                
    def ht_form_toolbar(self,toolbar,nodeId=None):
        toolbar.dataController("SET .title =recordCaption",recordCaption="^.record?caption")
        toolbar.div('^.title',float='left')
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.data('.status.locked',True)
        spacer.button('!!Unlock',fire='.status.unlock',iconClass="tb_button icnBaseLocked",
                    showLabel=False,hidden='^.status.unlocked')
        spacer.button('!!Lock',fire='.status.lock',iconClass="tb_button icnBaseUnlocked", 
                    showLabel=False,hidden='^.status.locked')
        toolbar.dataController("SET .status.locked=true;",fired='^.status.lock')
        toolbar.dataController("SET .status.locked=false;",fired='^.status.unlock') 
        toolbar.dataFormula(".status.unlocked", "!locked",locked="^.status.locked")
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
              """,isChanged="^.form.changed",semaphoreId='%s_semaphore' %nodeId,
            isValid='^.form.valid')
        spacer.div(nodeId='%s_semaphore' %nodeId,_class='semaphore',margin_top='3px',
                  hidden='^.status.locked')  
        toolbar.button('!!Save',fire=".save", float='right',
                        iconClass="tb_button db_save",showLabel=False,
                        hidden='^.status.locked')
        toolbar.button('!!Revert',fire=".load", iconClass="tb_button db_revert",float='right',
                        showLabel=False,hidden='^.status.locked')      
                                                                 
    def ht_tree(self,bc,table=None,nodeId=None,rootpath=None,disabled=None,editMode=None):
        toolbar = bc.contentPane(region='top').toolbar(height='20px')
        toolbar.button('!!Add child')
        toolbar.button('Set to varie',action='SET .tree.path="V";')
        tblobj = self.db.table(table)
        center = bc.contentPane(region='center')
        selected = dict()
        dfltConf = dict(code='code',parent_code='parent_code',child_code='child_code')
        if hasattr(tblobj,'htable_conf'):
            dfltConf = tblobj.htable_conf()        
        selected['selected_%s' %dfltConf['parent_code']] = '.tree.parent_code'
        selected['selected_%s' %dfltConf['child_code']] = '.tree.child_code'
        selected['selected_%s' %dfltConf['code']] = '.tree.code'

        center.data('.tree.store',HTableResolver(table=table,rootpath=rootpath,
                                                    rootlabel=tblobj.name_plural,_page=self)(),
                                                    rootpath=rootpath)
        center.tree(storepath ='.tree.store',
                     isTree =False,
                     hideValues=True,
                     inspect ='shift',
                     labelAttribute ='caption',
                     selected_pkey='.tree.pkey',
                     selectedPath='.tree.path',
                     getLabelClass='return node.attr.labelClass',
                     useRelPath=True,
                     **selected)
                     
class HTableResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False,
                 'table':None,
                 'rootpath':None,
                 'rootlabel':False,
                 '_page':None}
    classArgs=['table','rootpath','rootlabel']
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
            caption='%s-%s'% (row['code'].split('.')[-1],row['caption'])
            if row['child_count']:
                value=HTableResolver(table=self.table,rootpath=row['code'])
            else:
                value=None
            children.setItem(row['child_code'], value,_attributes=dict(row),caption=caption)
        if not self.rootlabel:
            return children
        result = Bag()
        if self.rootpath:
            row=tblobj.query(columns='*',where='$code=:code',code=self.rootpath).fetch()[0]
            caption='%s-%s'% (row['code'].split('.')[-1],row['caption'])
            rootlabel = row['child_code']
            _attributes=dict(row)
        else:
            caption=self.rootlabel
            rootlabel ='_root_'
            _attributes=dict()
        result.setItem(rootlabel, children, caption=caption,_attributes=_attributes)
        return result
        
        