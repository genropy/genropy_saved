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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver

def _getTreeRowCaption(tblobj):
    if hasattr(tblobj,'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code,$description:%s - %s'

def _getTreeRowCaption2(tblobj):
    if hasattr(tblobj,'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code'

class HTableHandlerBase(BaseComponent):
    def ht_treeDataStore(self,table=None,rootpath=None,rootcaption=None):
        tblobj= self.db.table(table)
        result = Bag()
        if rootpath:
            row=tblobj.query(columns='*',where='$code=:code',code=rootpath).fetch()[0]
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            caption=tblobj.recordCaption(row,rowcaption=get_tree_row_caption(tblobj))
            rootlabel = row['child_code']
            pkey=row['pkey']
            _attributes=dict(row)
            rootpath=row['code']
            code=row['code']
            child_count = row['child_count']

        else:
            caption=rootcaption
            rootlabel ='_root_'
            _attributes=dict()
            pkey=None
            code=None
            rootpath=None
            child_count = tblobj.query().count()
        value =  HTableResolver(table=table,rootpath=rootpath) if child_count else None
        result.setItem(rootlabel,value,child_count=child_count, caption=caption,pkey=pkey,code=code)#,_attributes=_attributes)
        return result
                    
class HTableHandler(HTableHandlerBase):
    css_requires='public'
    def htableHandler(self,parent,nodeId=None,datapath=None,table=None,rootpath=None,label=None,
                    editMode='bc',childTypes=None,dialogPars=None,loadKwargs=None,parentLock=None,where=None,onChecked=None):
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
        disabled ='^#%s.edit.status.locked'%nodeId
        if parentLock:
            parent.dataController("SET .edit.status.locked=parentLock;",parentLock=parentLock,datapath=datapath)
            parent.dataController("""SET %s=isLocked;""" %parentLock[1:],
                                    parentLock=parentLock,isLocked='^.edit.status.locked',
                                    _if='parentLock!=isLocked',datapath=datapath)
                                        
        formPanePars = dict(selectedPage='^.edit.selectedPage',_class='pbl_roundedGroup')
        if editMode=='bc':
            bc = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px')
            treepane = bc.borderContainer(region='left',width='40%',splitter=True,_class='pbl_roundedGroup')
            formPanePars['region'] = 'center'            
            formBC = bc.borderContainer(region='center')
            
        elif editMode=='sc':
            sc = parent.stackContainer(region='center',datapath=datapath,nodeId=nodeId,
                                        selectedPage='^.selectedPage',margin='2px')
            treepane = sc.borderContainer(pageName='tree',_class='pbl_roundedGroup')
            formPanePars['pageName'] = 'edit'
            formBC = sc.borderContainer(region='center')
            
        elif editMode=='dlg':
            assert dialogPars,'for editMode == "dlg" dialogPars are mandatory'
            treepane = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px',_class='pbl_roundedGroup')
            formBC = self.simpleDialog(treepane,dlgId='%s_dlg' %nodeId,**dialogPars)
            formPanePars['region'] = 'center'
            
        recordlabel = formBC.contentPane(region='top',_class='pbl_roundedGroupLabel')
        recordlabel.div('^.edit.record?caption')
        footer = formBC.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        if editMode=='dlg':
            footer.button('!!Close',fire='.close')

        formpane = formBC.stackContainer(pageName='edit',**formPanePars)
        footer.dataController("""
                            var pathlist = currpath.split('.');
                            var rootnode = genro.nodeById(labelNodeId).clearValue().freeze();
                            var label,path2set;
                            for(var i=0;i<pathlist.length-1;i++){
                                label = pathlist[i];
                                path2set = path2set?path2set+'.'+label:label;
                                var action = "this.setRelativeData('.tree.path','"+path2set+"');";
                                var showLabel = true;
                                if(label=='_root_'){
                                    label = rootName;
                                }else{
                                    label = label;
                                }
                                rootnode._('button',{label:label,action:action,'float':'left',font_size:'.9em',
                                                    iconClass:'breadcrumbIcn',showLabel:showLabel});
                                    
                            }
                            rootnode.unfreeze();

                            """,
                             currpath='=.tree.path',_fired='^.edit.record.code',
                             labelNodeId='%s_nav' %nodeId,rootName='!!Root:')
        
        self.ht_tree(treepane,table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,childTypes=childTypes,editMode=editMode,label=label,onChecked=onChecked)
        self.ht_edit(formpane,table=table,nodeId=nodeId,disabled=disabled,
                        rootpath=rootpath,editMode=editMode,loadKwargs=loadKwargs)
                        
    def ht_edit_dlg_bottom(self,bc,**kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Close',fire='.close')
                
    def ht_edit(self,sc,table=None,nodeId=None,disabled=None,rootpath=None,editMode=None,loadKwargs=None):
        formId='%s_form' %nodeId
        norecord = sc.contentPane(pageName='no_record').div('No record selected')
        bc = sc.borderContainer(pageName='record_selected')
        toolbar = bc.contentPane(region='top',overflow='hidden').toolbar(_class='standard_toolbar')
        toolbar.dataFormula('.edit.status.locked',True,_onStart=True)
        toolbar.dataController("""
                            if(isLocked){
                            //if not unlockable return
                                isLocked = isLocked //if unlocable 
                            }
                            SET .edit.status.locked=!isLocked
                            """,
                            _fired='^.edit.status.changelock',
                            isLocked='=.edit.status.locked')
        toolbar.dataController("""
                             SET .edit.status.statusClass = isLocked?'tb_button icnBaseLocked':'tb_button icnBaseUnlocked';
                             SET .edit.status.lockLabel = isLocked?unlockLabel:lockLabel;
                               """,isLocked="^.edit.status.locked",lockLabel='!!Lock',
                                unlockLabel='!!Unlock')
        
        
        
        self.ht_edit_toolbar(toolbar,nodeId=nodeId,disabled=disabled,editMode=None)
        bc.dataController("SET .edit.selectedPage=pkey?'record_selected':'no_record'",pkey="^.tree.pkey")
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){
                                genro.setData('#%s.tree.pkey',currPkey);
                                genro.setData('#%s.tree.path',rootpath?currPkey.slice(rootpath.length-1):currPkey);
                                };
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ %(nodeId,nodeId),rootpath='=.tree.store?rootpath',
                            selPkey='^.tree.pkey',currPkey='=.edit.pkey',_if='selPkey!=currPkey',
                            formId=formId)

        bc.dataController("""
                             var rootpath = rootpath || null;
                             
                             if (destPkey!='*newrecord*'){
                                 var editNode = treestore.getNode(treepath);
                                 var attr= editNode.attr;
                                 attr.caption = treeCaption;
                                 editNode.setAttr(attr);
                                 FIRE .edit.load;
                             }else{
                                SET .edit.pkey = savedPkey;
                                FIRE .edit.load;
                                var parentPath = rootpath?parent_code.slice(rootpath.length):parent_code?'_root_.'+parent_code:'_root_'
                                var refreshFromNode = treestore.getNode(parentPath);
                                
                                if(!refreshFromNode.getValue()){
                                    refreshFromNode = refreshFromNode.getParentNode();
                                }
                                refreshFromNode.refresh(true);
                             }
                         """,
                        _fired="^.edit.onSaved",destPkey='=.tree.pkey',parent_code='=.edit.record.parent_code',
                        savedPkey='=.edit.savedPkey',rootpath='=.tree.store?rootpath',
                        treepath='=.tree.path',treestore='=.tree.store',
                        treeCaption='=.edit.savedPkey?caption')
        bc.dataController("""
                            if (rootpath){
                                path=code.slice(rootpath.length);
                            }else{
                                path = code?'_root_.'+code:'_root_';
                            }
                            SET .tree.path=path;""",code="^.edit.record.code",
                            rootpath='=.tree.store?rootpath',_if='code')
        
        
        bc.dataRpc('.edit.del_result','deleteDbRow',pkey='=.edit.pkey',
                    _POST=True,table=table,_delStatus='^.edit.delete',
                    _if='_delStatus=="confirm"',_else='genro.dlg.ask(title,msg,null,"#%s.edit.delete")' %nodeId,
                    title='!!Deleting record',msg='!!You cannot undo this operation. Do you want to proceed?',
                    _onResult="""var path = $2.currpath.split('.');
                                 path.pop();
                                 var path = path.join('.');
                                 $2.treestore.getNode(path).refresh(true)
                                 SET .tree.path = path;""",currpath='=.tree.path',treestore='=.tree.store')
                    
        getattr(self,formId)(bc,region='center',table=table,
                              datapath='.edit.record',controllerPath='#%s.edit.form' %nodeId,
                              formId=formId,
                              disabled= disabled,
                              pkeyPath='#%s.edit.pkey' %nodeId)
        tblobj = self.db.table(table)
        loadKwargs =  loadKwargs or dict()
       
        loadKwargs['default_parent_code'] = '=.defaults.parent_code'                                
        self.formLoader(formId,datapath='#%s.edit' %nodeId,resultPath='.record',_fired='^.load',
                        table=table, pkey='=.pkey',**loadKwargs)
        self.formSaver(formId,datapath='#%s.edit' %nodeId,resultPath='.savedPkey',_fired='^.save',
                        table=table,onSaved='FIRE .onSaved;',#onSaving='if($1.getItem("child_code").indexOf(".")>=0){}',
                        rowcaption=_getTreeRowCaption(self.db.table(table)))

    def ht_edit_toolbar(self,toolbar,nodeId=None,disabled=None,editMode=None):
        nav = toolbar.div(float='left',nodeId='%s_nav' %nodeId)
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.button(label='^.edit.status.lockLabel', fire='.edit.status.changelock',
                      iconClass="^.edit.status.statusClass",showLabel=False)
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
        toolbar.button('!!Save',fire=".edit.save", float='right',
                        iconClass="tb_button db_save",showLabel=False,
                        hidden=disabled)
        toolbar.button('!!Revert',fire=".edit.load", iconClass="tb_button db_revert",float='right',
                        showLabel=False,hidden=disabled)      
        toolbar.button('!!Add',action="""   SET .edit.defaults.parent_code = GET .edit.record.parent_code;
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
                                            
                                                                 
    def ht_tree(self,bc,table=None,nodeId=None,rootpath=None,disabled=None,childTypes=None,editMode=None,label=None,onChecked=None):
        
        labelbox = bc.contentPane(region='top',_class='pbl_roundedGroupLabel')
        labelbox.div(label,float='left')
        add_action="""SET .edit.defaults.parent_code = GET .tree.code;
                      SET .tree.pkey = '*newrecord*';"""
        if editMode=='dlg':
            add_action = '%s FIRE #%s_dlg.open;' %(add_action,nodeId)
        btn_addChild = labelbox.div(float='right', _class='buttonIcon icnBaseAdd',connect_onclick=add_action,
                        margin_right='2px',visible='^.tree.path',default_visible=False)
        if childTypes:
            childTypesMenu = Bag()
            for k,v in childTypes.items():
                childTypesMenu.setItem(k,None,caption=v,action="SET .edit.childType = $1.fullpath; %s" %add_action)
            labelbox.data('.childTypesMenu',childTypesMenu)
            btn_addChild.menu(storepath='.childTypesMenu',modifiers='*',_class='smallmenu')            
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
                    connect_ondblclick=connect_ondblclick,
                    onChecked=onChecked)

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
        rows = tblobj.query(columns='*,$child_count,$hdescription',where="COALESCE($parent_code,'')=:rootpath" ,
                     rootpath=self.rootpath or '',order_by='$child_code').fetch()
        children = Bag()
        for row in rows:
            child_count= row['child_count']
            value=HTableResolver(table=self.table,rootpath=row['code'],child_count=child_count) if child_count else None
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            children.setItem(row['child_code'], value,caption=tblobj.recordCaption(row,rowcaption=get_tree_row_caption(tblobj)),
                             pkey=row['pkey'],code=row['code'],child_count=child_count,
                             parent_code=row['parent_code'],hdescription=row['hdescription'])#_attributes=dict(row),
        return children
        
class HTablePicker(HTableHandlerBase):
    py_requires='foundation/dialogs,foundation/includedview:IncludedView'
    def htablePicker(self,parent,table=None,column=None,rootpath=None,
                    resultpath=None,nodeId=None,datapath=None,dialogPars=None,
                    caption=None,grid_struct=None,grid_columns=None,grid_table=None,grid_where=None,**kwargs):
        """params htable:
            parent
            column??
            resultpath
            """
        dialogPars = dialogPars or dict()
        tblobj = self.db.table(table)
        dialogPars['title'] = dialogPars.get('title','%s picker' %tblobj.name_long)
        dialogPars['height'] = dialogPars.get('height','300px')
        dialogPars['width'] =  dialogPars.get('width', '400px')
        dlgbc = self.formDialog(parent,datapath=datapath,formId=nodeId,
                                cb_center=self.ht_pk_center,caption=caption,table=table,
                                grid_struct=grid_struct,grid_columns=grid_columns,
                                grid_where=grid_where,
                                grid_table=grid_table,**dialogPars)
                                
        dlgbc.dataRpc('.data.tree','ht_pk_getTreeData',table=table,
                        rootpath=rootpath,rootcaption=tblobj.name_plural,
                        nodeId='%s_loader' %nodeId,_onResult='FIRE .check_curr_elements;')
        dlgbc.dataController("FIRE .reload_tree; FIRE .loaded",
                            _fired="^.check_curr_elements",checked_elements='=%s' %resultpath)
        dlgbc.dataController("""
                                var result = [];
                                selection.forEach(function(n){
                                    if(n.attr._checked){
                                        result.push(n.attr._pkey);
                                    }
                                },'static');
                                SET %s = result;
                                FIRE .saved;
                                
                            """ %resultpath,nodeId='%s_saver' %nodeId,selection='=#%s_grid.selection' %nodeId)        
        
        
    def rpc_ht_pk_getTreeData(self,table=None,rootpath=None,rootcaption=None):
        #result = self.db.table(table).query().fetchAsBag(key='code')
        result = self.ht_treeDataStore(table=table,rootpath=rootpath,rootcaption=rootcaption)
        return result
    
    def ht_pk_center(self,parentBC,table=None,formId=None,datapath=None,
                    controllerPath=None,region=None,caption=None,grid_struct=None,grid_columns=None,
                    grid_table=None,grid_where=None,**kwargs):
        sc = parentBC.stackContainer(_class='pbl_roundedGroup',selectedPage='^.selectedPage',region=region)
        
        self._ht_pk_tree(sc.borderContainer(pageName='tree'),
                         caption=caption,datapath=datapath,
                        controllerPath=controllerPath,
                        formDatapath='.data.tree',formId=formId)
        self._ht_pk_view(sc.borderContainer(pageName='view'),
                        caption=caption, gridId='%s_grid' %formId,
                        table=table,grid_table=grid_table,grid_where=grid_where,
                        grid_struct=grid_struct,grid_columns=grid_columns)

    def _ht_pk_tree(self,bc,caption=None,datapath=None,formId=None,controllerPath=None,**kwargs):
        top = bc.contentPane(region='top').toolbar().div(value=caption,height='20px')
        bc.contentPane(region='bottom').button('Show selected',action='FIRE .calculate_checked; SET .selectedPage = "view";')
        
        center = bc.contentPane(region='center',datapath=datapath,formId=formId,controllerPath=controllerPath)
        center.tree(storepath ='.tree._root_',
                    isTree =False,hideValues=True,
                    _fired='^.#parent.reload_tree',
                    inspect ='shift',labelAttribute ='caption',
                    onChecked=True)
        #center.data('.tree.store',Bag())
                    
                    
        bc.dataController("""
                            var result = [];
                            treedata.walk(function(n){
                                if (n.attr['checked']==true && !n.getValue()){
                                    result.push(n.attr['code']);
                                }
                            },'static');
                            SET .data.checked_codes = result;
                            FIRE .preview_grid.load;
                            """,_fired="^.calculate_checked",treedata='=.data.tree')
                    
    def _ht_pk_view(self,bc,caption=None,gridId=None,table=None,grid_columns=None,
                    grid_struct=None,grid_where=None,grid_table=None,**kwargs):
        def footer(pane,**kwargs):
            pane.button('Tree',action='SET .#parent.selectedPage = "tree";')
        struct=grid_struct #or self._ht_pk_view_struct
       #struct = struct(self.newGridStruct(grid_table))
       #struct.getItem('#0.#0').checkboxcell()
        self.includedViewBox(bc,label=caption,footer=footer,datapath='.preview_grid',
                             nodeId=gridId,columns=grid_columns,
                             table=grid_table or table,autoWidth=True,
                             struct=struct,
                             reloader='^.load', 
                             selectionPars=dict(where=grid_where or '$code IN :codes',
                                                codes='=.#parent.data.checked_codes',
                                                _onResult="""
                                                             var bag =result.getValue();
                                                             bag.forEach(function(n){n.attr._checked=true;},'static');
                                                             """))
                                                
        
        
        

