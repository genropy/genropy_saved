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

class HTableResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False,
                 'table':None,
                 'rootpath':None,
                 'limit_rec_type':None,
                 '_page':None}
    classArgs=['table','rootpath']
            
    def load(self):
        db= self._page.db
        tblobj = db.table(self.table) 
        rows = tblobj.query(columns='*,$child_code,$child_count,$description',where="COALESCE($parent_code,'')=:rootpath" ,
                     rootpath=self.rootpath or '',order_by='$child_code').fetch()
        children = Bag()
        for row in rows:
            child_count= row['child_count']
            limit_condition = True
            if self.limit_rec_type:
                limit_condition = row['rec_type'] !=self.limit_rec_type
            if child_count and limit_condition:
                value = HTableResolver(table=self.table,rootpath=row['code'],
                                        limit_rec_type=self.limit_rec_type,
                                        child_count=child_count,_page=self._page)  
            else:
                value = None
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            children.setItem(row['child_code'], value,
                             caption=tblobj.recordCaption(row,rowcaption=get_tree_row_caption(tblobj)),
                             pkey=row['pkey'],code=row['code'],child_count=child_count,checked=False,
                             parent_code=row['parent_code'],description=row['description'])#_attributes=dict(row),
        return children
        
    def resolverSerialize(self):
        self._initKwargs.pop('_page')
        return BagResolver.resolverSerialize(self)
        
class HTableHandlerBase(BaseComponent):
    
    def ht_treeDataStore(self,table=None,rootpath=None,limit_rec_type=None,rootcaption=None):
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
        value =  HTableResolver(table=table,rootpath=rootpath,limit_rec_type=limit_rec_type,_page=self) if child_count else None
        result.setItem(rootlabel,value,child_count=child_count, caption=caption,pkey=pkey,code=code,checked=False)#,_attributes=_attributes)
        return result
                    
class HTableHandler(HTableHandlerBase):
    py_require='gnrcomponents/selectionhandler:SelectionHandler'
    css_requires='public'
    def htableHandler(self,parent,nodeId=None,datapath=None,table=None,rootpath=None,label=None,
                    editMode='bc',childTypes=None,dialogPars=None,loadKwargs=None,parentLock=None,
                    where=None,onChecked=None,plainView=False,noRecordClass='noRecordSelected'):
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
        
        if plainView:
            tc = parent.tabContainer(nodeId='%s_tc' %nodeId,region='center')
            parent = tc.contentPane(title='!!Hierarchical')
            self.ht_plainView(tc.borderContainer(title='!!Plain',datapath=datapath),table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,childTypes=childTypes,editMode=editMode,label=label)

        commontop = None
        if editMode=='bc':
            bc = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px')
            treepane = bc.borderContainer(region='left',width='40%',splitter=True,_class='pbl_roundedGroup')
            formPanePars['region'] = 'center'            
            formBC = bc.borderContainer(region='center')
            commonTop = bc.contentPane(region='top',overflow='hidden')
             
            
            
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
            
       #recordlabel = formBC.contentPane(region='top',_class='pbl_roundedGroupLabel')
       #recordlabel.div('^.edit.record?caption')
        if editMode=='dlg':
            footer = formBC.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
            footer.button('!!Close',fire='.close')
        formpane = formBC.stackContainer(pageName='edit',**formPanePars)
        
        self.ht_tree(treepane,table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,childTypes=childTypes,editMode=editMode,label=label,onChecked=onChecked)
        self.ht_edit(formpane,table=table,nodeId=nodeId,disabled=disabled,
                        rootpath=rootpath,editMode=editMode,loadKwargs=loadKwargs,
                        childTypes=childTypes,commonTop=commonTop,noRecordClass=noRecordClass)
                        
    def ht_edit_dlg_bottom(self,bc,**kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Close',fire='.close')
                
    def ht_edit(self,sc,table=None,nodeId=None,disabled=None,rootpath=None,editMode=None,loadKwargs=None,childTypes=None,commonTop=None,noRecordClass=''):
        formId='%s_form' %nodeId
        norecord = sc.contentPane(id='no_record_page',pageName='no_record').div('',_class=noRecordClass)
        bc = sc.borderContainer(pageName='record_selected')
        top = commonTop if editMode=='bc' else bc.contentPane(region='top',overflow='hidden')
        toolbar =top.toolbar(_class='standard_toolbar')
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
        
        
        
        self.ht_edit_toolbar(toolbar,nodeId=nodeId,disabled=disabled,editMode=editMode,childTypes=childTypes)
        bc.dataController("""
                            if(pkey){
                                SET .edit.selectedPage='record_selected';
                                SET .edit.no_record = false;
                            }else{
                                SET .edit.selectedPage='no_record';
                                SET .edit.no_record = true;
                            }
                            """,pkey="^.tree.pkey")
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){
                                genro.setData('#%s.tree.pkey',currPkey);
                                genro.setData('#%s.tree.path',rootpath?currPkey.slice(rootpath.length-1):currPkey);
                                };
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ %(nodeId,nodeId),rootpath='=.tree.store?rootpath',
                            selPkey='^.tree.pkey',currPkey='=.edit.pkey',_if='selPkey && (selPkey!=currPkey)',
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

    def ht_edit_toolbar(self,toolbar,nodeId=None,disabled=None,editMode=None,childTypes=None):
        
        nav = toolbar.div(float='left',nodeId='%s_nav' %nodeId,font_size='.9em')
        toolbar.dataController("""
        
                            var pathlist = currpath.split('.');
                            var rootName = this.getRelativeData('.tree.store.#0?caption');
                            var rootnode = genro.nodeById(labelNodeId).clearValue();
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
                                rootnode._('button',{'label':label,'action':action,'float':'left',
                                                    'iconClass':'breadcrumbIcn','showLabel':showLabel});
                                    
                            }
                            rootnode._('button',{label:record_label,'float':'left',iconClass:'breadcrumbIcn',color:'red'});
                            rootnode._('button',{label:add_label,'float':'left',disabled:'%s',
                                                iconClass:'icnBaseAdd',showLabel:false,
                                                fire:'.edit.save_button',
                                                tree_code:tree_code});

                            """ %disabled,
                             
                             labelNodeId='%s_nav' %nodeId,
                             currpath='=.tree.path',
                             record_label='^.tree.caption',
                             tree_code='=.tree.code',
                             add_label='!!Add')
        toolbar.dataController("""
                                  if(modifier=="Shift"){
                                        SET .edit.defaults.parent_code = GET .edit.record.parent_code;
                                        SET .tree.pkey = '*newrecord*';
                                  }else{
                                        SET .edit.defaults.parent_code = tree_code;
                                        SET .tree.pkey ='*newrecord*';       
                                  }                                  
                                  
                                """,tree_code='=.tree.code',
                                modifier="^.edit.save_button")
        
        
        buttons = toolbar.div(float='right')
            
        spacer = buttons.div(float='right',_class='button_placeholder')
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
        spacer.div(nodeId='%s_semaphore' %nodeId,_class='semaphore',margin_top='3px',hidden='^.edit.no_record')  
        toolbar.button('!!Save',fire=".edit.save", float='right',
                        iconClass="tb_button db_save",showLabel=False,
                        hidden='^.edit.no_record',
                        disabled=disabled)
        toolbar.button('!!Revert',fire=".edit.load", iconClass="tb_button db_revert",
                        hidden='^.edit.no_record',
                        float='right',
                        showLabel=False,disabled=disabled)      
       # toolbar.button('!!Add',action="""   SET .edit.defaults.parent_code = GET .edit.record.parent_code;
       #                                     SET .tree.pkey = '*newrecord*';
       #                                     """,iconClass='db_add tb_button',
       #                                     showLabel=False,hidden=disabled,float='right')
        toolbar.button('!!Delete',fire=".edit.delete",iconClass='db_del tb_button',
                                            showLabel=False,disabled=disabled,
                                            hidden='^.edit.no_record',
                                            visible='^.edit.enableDelete',
                                            float='right')
        toolbar.dataFormula('.edit.enableDelete','child_count==0',child_count='^.tree.child_count')
        
        
        if editMode=='sc':
            toolbar.button('!!Tree',action="SET .selectedPage = 'tree';")
                                            
                 
    def ht_plainView(self,bc,table=None,nodeId=None,disabled=None,
                    rootpath=None,editMode=None,label=None):
        gridId='%s_grid' %nodeId
        default_selectionPars = dict(order_by='$code')
        dialogParsCb =getattr(self,'%s_dialogPars' %gridId,None)
        dialogPars=None
        if dialogParsCb:
            dialogPars = dialogParsCb()
        if rootpath:
            default_selectionPars = dict(where='$code LIKE %%:rootpath',rootpath=rootpath,order_by='$code')
        self.selectionHandler(bc,label=label,datapath=".plainview",
                                nodeId=gridId,table=table,add_enable=False,del_enable=False,
                                struct=getattr(self,'%s_struct' %gridId,None),
                                parentLock=disabled,_onStart=True,
                                selectionPars=getattr(self,'%s_selectionPars' %gridId,default_selectionPars),
                                dialogPars=dialogPars,
                                filterOn=getattr(self,'%s_filterOn' %gridId,'$code,$description'))
                                            
    def ht_labeltree(self,pane,label=None,nodeId=None,childTypes=None,editMode=None):
        pane.div(label,float='left')
        add_action="""SET .edit.defaults.parent_code = GET .tree.code;
                      SET .tree.pkey = '*newrecord*';"""
        if editMode=='dlg':
            add_action = '%s FIRE #%s_dlg.open;' %(add_action,nodeId)
        
        btn_addChild = pane.div(float='left' if editMode=='bc' else 'right', 
                                _class='buttonIcon icnBaseAdd',connect_onclick=add_action,
                                margin_right='2px',visible='^.tree.path',default_visible=False)
        
        if childTypes:
            childTypesMenu = Bag()
            for k,v in childTypes.items():
                childTypesMenu.setItem(k,None,caption=v,action="SET .edit.childType = $1.fullpath; %s" %add_action)
            pane.data('.childTypesMenu',childTypesMenu)
            btn_addChild.menu(storepath='.childTypesMenu',modifiers='*',_class='smallmenu') 
                                    
    def ht_tree(self,bc,table=None,nodeId=None,rootpath=None,disabled=None,
                childTypes=None,editMode=None,label=None,onChecked=None):
        if editMode!='bc':
            self.ht_labeltree(bc.contentPane(region='top',_class='pbl_roundedGroupLabel'),label=label,
                                            nodeId=nodeId,childTypes=childTypes,editMode=editMode)
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
                    margin='10px',isTree =False,hideValues=True,
                    inspect ='shift',labelAttribute ='caption',
                    selected_pkey='.tree.pkey',selectedPath='.tree.path',  
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_caption='.tree.caption',
                    selected_child_count='.tree.child_count',
                    connect_ondblclick=connect_ondblclick,
                    onChecked=onChecked)
                    

                    
        
class HTablePicker(HTableHandlerBase):
    py_requires='foundation/dialogs,foundation/includedview:IncludedView'
    
    def htablePicker(self,parent,table=None,rootpath=None,limit_rec_type=None,
                    input_codes=None,
                    output_codes=None,
                    output_pkeys=None,
                    nodeId=None,datapath=None,dialogPars=None,
                    caption=None,grid_struct=None,grid_columns=None,
                    grid_show=False,
                    condition=None,condition_pars=None,
                    editMode='dlg',**kwargs):
        
        self._htablePicker_main(parent,table=table,rootpath=rootpath,limit_rec_type=limit_rec_type,
                                input_codes=input_codes,output_codes=output_codes,
                                output_pkeys=output_pkeys,
                                nodeId=nodeId,grid_show=grid_show,
                                datapath=datapath,dialogPars=dialogPars,grid_struct=grid_struct,
                                grid_columns=grid_columns,editMode=editMode,
                                condition=condition,condition_pars=condition_pars)
    
    
    def htablePickerOnRelated(self,parent,table=None,rootpath=None,limit_rec_type=None,
                            input_pkeys=None,output_pkeys=None,
                            related_table=None,relation_path=None,
                            nodeId=None,datapath=None,dialogPars=None,
                            caption=None,grid_struct=None,grid_columns=None,
                            grid_applymethod=None,

                            grid_filter=None,default_checked_row=None,
                            condition=None,condition_pars=None,editMode=None,**kwargs):
            
            
        self._htablePicker_main(parent,table=table,rootpath=rootpath,
                        limit_rec_type=limit_rec_type,
                        related_table=related_table,
                        relation_path=relation_path,
                        input_pkeys=input_pkeys or '',output_related_pkeys=output_pkeys,nodeId=nodeId,grid_filter=grid_filter,
                        datapath=datapath,dialogPars=dialogPars,grid_struct=grid_struct,grid_columns=grid_columns,
                        grid_applymethod=grid_applymethod,
                        condition=condition,condition_pars=condition_pars,editMode=editMode,default_checked_row=default_checked_row)
    
    
    def _htablePicker_main(self,parent,table=None,rootpath=None,limit_rec_type=None,
                    input_pkeys=None,
                    input_codes=None,
                    output_pkeys=None,
                    output_related_pkeys=None,
                    grid_show=True,
                    output_codes=None,
                    nodeId=None,datapath=None,dialogPars=None,
                    caption=None,grid_struct=None,grid_columns=None,
                    condition=None,
                    condition_pars=None,
                    related_table=None,
                    relation_path=None,
                    grid_filter=None,
                    editMode=None,
                    grid_applymethod=None,
                    default_checked_row=None,
                    **kwargs):
        """params htable:
            parent
            column??
            resultpath
            """
        default_checked_row = False if default_checked_row is False else True
            
        editMode = editMode or 'dlg'
        grid_where = '$code IN :codes'
        if related_table:
            grid_where = '%s IN :codes' %relation_path 
        if condition:
            grid_where = '%s AND %s' %(grid_where,condition)
        condition_pars = condition_pars or dict()
        
        tblobj = self.db.table(table)
        default_width = '300px'
        if grid_show:
            default_width = '600px'
        params = dict(caption=caption,table=table,
                        grid_struct=grid_struct,grid_columns=grid_columns,
                        grid_where=grid_where,condition_pars=condition_pars,
                        output_codes=output_codes,output_pkeys=output_pkeys,
                        related_table=related_table,grid_show=grid_show,grid_filter=grid_filter,grid_applymethod=grid_applymethod,
                        default_checked_row=default_checked_row,
                        output_related_pkeys=output_related_pkeys)
        
        if editMode=='dlg':
            dialogPars = dialogPars or dict()
            dialogPars['title'] = dialogPars.get('title','%s picker' %tblobj.name_long)
            dialogPars['height'] = dialogPars.get('height','400px')
            dialogPars['width'] =  dialogPars.get('width', default_width)
            params.update(dialogPars)
            bc = self.formDialog(parent,datapath=datapath,formId=nodeId,
                                    cb_center=self.ht_pk_center,**params)
            bc.dataController("FIRE .open;",**{"subscribe_%s_open" %nodeId:True})
        elif editMode=='bc':
            bcId = '%s_bc' %nodeId
            bc = parent.borderContainer(datapath=datapath,nodeId=bcId)
            #bc.contentPane(region='top',_class='pbl_roundedGroupLabel').div('%s picker' %tblobj.name_long)
            #bottom = bc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
            bc.dataController("genro.formById(fid).load()",_onStart=True,fid=nodeId,**{"subscribe_%s_open" %nodeId:True})
           # bc.dataController("genro.formById(fid).load()",_onStart=True,fid=nodeId,**{"subscribe_%s_open" %nodeId:True)

           #bottom.button('!!Confirm', action='genro.formById(fid).save(true})',
           #                fid=nodeId,float='right')
            bc.dataController('genro.formById(fid).loaded();',fid=nodeId,_fired="^.loaded")
            bc.dataController('genro.formById(fid).saved();',fid=nodeId,_fired="^.saved")

            self.ht_pk_center(bc,region='center',
                        formId=nodeId,#form parameter
                        datapath='.data',#form parameter
                        controllerPath='#%s.form' %bcId,#form parameter
                        **params)
            
        
        bc.dataRpc('.data.tree','ht_pk_getTreeData',table=table,
                        rootpath=rootpath,rootcaption=tblobj.name_plural,
                        input_pkeys=input_pkeys,input_codes=input_codes,
                        relation_path=relation_path,related_table=related_table,
                        limit_rec_type=limit_rec_type,
                        nodeId='%s_loader' %nodeId,
                        _onResult="""FIRE .reload_tree;
                                     FIRE .prepare_check_status;
                                     if(kwargs._grid_show){
                                        if ($2.input_pkeys){
                                            SET .preview_grid.initial_checked_pkeys = $2.input_pkeys.split(',');
                                        }
                                        FIRE .preview_grid.load;
                                     }
                                     FIRE .loaded;""",_grid_show=grid_show)
                                     
        bc.dataController("""   PUBLISH %s_confirmed; 
                                FIRE .saved;""" %nodeId,
                            nodeId="%s_saver" %nodeId)
        
        bc.dataController("""
                            FIRE .prepare_check_status;
                            FIRE .preview_grid.load;
                            """ ,
                            **{'subscribe_%s_tree_checked' %nodeId:True})
                            
        bc.dataController("""
                            var result_codes = [];
                            var result_pkeys = [];
                            treedata.walk(function(n){
                                if (n.attr['checked']==true && !n.getValue()){
                                    result_codes.push(n.attr['code']);
                                    result_pkeys.push(n.attr['pkey']);
                                }
                            },'static');
                            SET .data.checked_codes = result_codes;
                            SET .data.checked_pkeys = result_pkeys;
                            if(output_codes){
                                this.setRelativeData(output_codes,result_codes.join(','));
                            }
                            if(output_pkeys){
                                this.setRelativeData(output_pkeys,result_pkeys.join(','));
                            }
                        """,
                        _fired="^.prepare_check_status",output_codes = output_codes or False,
                        output_pkeys= output_pkeys or False,
                        treedata='=.data.tree')
        
  
    def rpc_ht_pk_getTreeData(self,table=None,rootpath=None,limit_rec_type=None,rootcaption=None,
                             input_codes=None,input_pkeys=None,related_table=None,
                             relation_path=None):
        result = self.ht_treeDataStore(table=table,rootpath=rootpath,limit_rec_type=limit_rec_type,rootcaption=rootcaption)
        htableobj = self.db.table(table)
        if related_table:
            if input_pkeys:
                input_pkeys = input_pkeys.split(',')
                reltableobj = self.db.table(related_table)
                where='$%s IN :pkeys' %reltableobj.pkey
                q = reltableobj.query(columns='%s AS hcode' %relation_path,where=where,
                                                pkeys=input_pkeys,distinct=True,addPkeyColumn=False)
                input_codes = q.fetch()
                input_codes = [r['hcode'] for r in input_codes]
                
        if input_codes:
            if isinstance(input_codes,basestring):
                input_codes = input_codes.split(',')
            for code in input_codes:
                node = result.getNode('#0.%s' %code)
                if node and not node.attr['child_count']>0:
                    node.setAttr(checked=True)
            self._ht_pk_setParentStatus(result)
        return result
        
    def _ht_pk_setParentStatus(self,bag):
        for node in bag.nodes:        
            value = node.getValue('static')
            if isinstance(value,Bag):
                self._ht_pk_setParentStatus(value)
                checked_elements = value.digest('#a.checked')
                n_checked = checked_elements.count(True)
                n_fuzzy = checked_elements.count(-1)
                if n_checked == len(value):
                    checked = True
                elif n_checked==0 and n_fuzzy==0:
                    checked = False
                else:
                    checked = -1
                node.attr['checked'] = checked
        
    
    def ht_pk_center(self,parentBC,table=None,formId=None,datapath=None,
                    controllerPath=None,region=None,caption=None,grid_struct=None,grid_columns=None,grid_applymethod=None,
                    related_table=None,grid_where=None,condition_pars=None,output_codes=None,
                    output_related_pkeys=None,grid_show=None,
                    output_pkeys=None,grid_filter=None,default_checked_row=None,**kwargs):
        if grid_show:
            bc = parentBC.borderContainer(_class='pbl_roundedGroup',region=region)
            treepane = bc.contentPane(region='left',width='150px',splitter=True,
                                        datapath=datapath,formId=formId,controllerPath=controllerPath)
            self._ht_pk_view(bc.borderContainer(region='center'),
                        caption=caption, gridId='%s_grid' %formId,
                        table=table,related_table=related_table,
                        grid_where=grid_where,condition_pars=condition_pars,
                        output_related_pkeys=output_related_pkeys,
                        output_pkeys=output_pkeys,grid_struct=grid_struct,grid_applymethod=grid_applymethod,
                        grid_columns=grid_columns,grid_filter=grid_filter,default_checked_row=default_checked_row)
        else:
            treepane = parentBC.contentPane(region=region,datapath=datapath,formId=formId,
                                                controllerPath=controllerPath)
        self._ht_pk_tree(treepane,caption=caption,formId=formId)
    
        

    def _ht_pk_tree(self,pane,caption=None,formId=None,*kwargs):
        pane.tree(storepath ='.tree._root_',
                    isTree =False,hideValues=True,
                    _fired='^.#parent.reload_tree',
                    nodeId='%s_tree' %formId,eagerCheck=True,
                    inspect ='shift',labelAttribute ='caption',onChecked=True)
                            
                            
                    
    def _ht_pk_view(self,bc,caption=None,gridId=None,table=None,grid_columns=None,
                    grid_applymethod=None,
                    grid_struct=None,grid_where=None,condition_pars=None,related_table=None,
                    output_related_pkeys=None,grid_filter=None,default_checked_row=None,**kwargs):
                  
        label = False
        hasToolbar = None
        if grid_filter:
            label = ' '  
            hasToolbar = True
        self.includedViewBox(bc,label=label,datapath='.preview_grid',
                             nodeId=gridId,columns=grid_columns,
                             table=related_table or table,filterOn=grid_filter,
                             struct=grid_struct,hasToolbar=hasToolbar,
                             reloader='^.load', addCheckBoxColumn=bool(related_table),
                             selectionPars=dict(where=grid_where,
                                                codes='=.#parent.data.checked_codes',
                                                _delay=1000,
                                                _onResult="""
                                                    var bag =result.getValue();
                                                    var initial_pkeys = GET .initial_checked_pkeys;
                                                    var default_check = kwargs.checked_row_default;
                                                    var cb_initial = function(n){
                                                        n.attr._checked = dojo.indexOf(initial_pkeys,n.attr._pkey)>=0?default_check:false;
                                                    };
                                                    var cb = function(n){
                                                        var old_n = old.getNodeByAttr('_pkey',n.attr._pkey);
                                                        n.attr._checked=(old_n && old_n.attr._checked==false)?false:default_check;
                                                    }
                                                    bag.forEach(initial_pkeys?cb_initial:cb,'static');   
                                                    SET .initial_checked_pkeys = null;
                                                    FIRE .#parent.set_output_pkeys;
                                                """,checked_row_default=default_checked_row,
                                                    applymethod=grid_applymethod,**condition_pars),
                                                )
        
        bc.dataController("""
                            var l = [];
                            selection.forEach(function(n){
                                if(n.attr._checked){
                                    l.push(n.attr._pkey);
                                }
                            },'static');
                            this.setRelativeData(output_related_pkeys,l.join(','));
                            """,_fired="^.set_output_pkeys",selection='=.preview_grid.selection',
                            output_related_pkeys=output_related_pkeys,_if='output_related_pkeys',
                            **{'subscribe_%s_row_checked' %gridId:True})
        
                         
        
        
        

