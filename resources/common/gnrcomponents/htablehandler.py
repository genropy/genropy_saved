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
from gnr.core.gnrbag import Bag, BagResolver
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs

ROOTCODE = '__ROOT__'

def _getTreeRowCaption(tblobj):
    if hasattr(tblobj, 'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code,$description:%s - %s'
    
def _getTreeRowCaption2(tblobj):
    if hasattr(tblobj, 'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code'
    
class HTableResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'readOnly': False,
                   'table': None,
                   'rootpath': None,
                   'limit_rec_type': None,
                   'related_table': None,
                   'related_order_by': None,
                   'relation_path': None,
                   'rootpkey': None,
                   'extra_columns':None,
                   'related_extra_columns':None,
                   'related_fullrecord':None,
                   'condition':None,
                   'condition_kwargs':None,
                   '_condition_id':None,
                   'storename':None,
                   '_page': None}
    classArgs = ['table', 'rootpath']
    
    def loadRelated(self, pkey):
        db = self._page.db
        tblobj = db.table(self.related_table)
        columns = ['*']
        captioncolumns = tblobj.rowcaptionDecode()[0]
        if captioncolumns:
            columns.extend(captioncolumns)
        columns = ','.join(columns)
        if self.related_extra_columns:
            columns = '%s,%s' %(columns,self.related_extra_columns)
        rows = tblobj.query(where='%s=:pkey' % self.relation_path[1:], pkey=pkey,columns=columns,order_by=self.related_order_by).fetch()
        children = Bag()

        for row in rows:
            caption = tblobj.recordCaption(row)
            children.setItem(row['pkey'], None,
                             caption=caption,
                             pkey=row['pkey'], code=row.get('code'),
                             node_class='tree_related',_record=dict(row) if self.related_fullrecord else None)
        return children
    
    
    def load(self):
        if self.rootpath and self.rootpath.startswith('*related*'):
            return self.loadRelated(self.rootpath.split(':')[1])
        db = self._page.db
        if self.storename:
            db.use_store(self.storename)
        tblobj = db.table(self.table)
        columns = '*,$child_count'
        if self.extra_columns:
            columns = '%s,%s' %(columns,self.extra_columns) 
        where="COALESCE($parent_code,'')=:rootpath"
        condition_kwargs = self.condition_kwargs or dict()
        condition_codes = None
        if self.condition:
            condition_codes = self.getConditionCodes()
            where = ' ( %s ) AND ( ( ( %s ) AND ($child_count=0) ) OR ( $code IN :condition_codes ) ) ' %(where,self.condition)
        rows = tblobj.query(columns,where=where,
                            rootpath=self.rootpath or '', order_by='$child_code',
                            condition_codes=condition_codes,
                            **condition_kwargs).fetch()
        children = Bag()
        if self.related_table:
            self.setRelatedChildren(children)
        for row in rows:
            child_count = row['child_count']
            if self.limit_rec_type:
                child_count = child_count if row['rec_type'] != self.limit_rec_type else 0
            if child_count:
                value = HTableResolver(table=self.table, rootpath=row['code'], rootpkey=row['pkey'],
                                       relation_path=self.relation_path,
                                       related_table=self.related_table,
                                       limit_rec_type=self.limit_rec_type,
                                       extra_columns=self.extra_columns,
                                       child_count=child_count, _page=self._page,_condition_id=self._condition_id,
                                       condition=self.condition,condition_kwargs=self.condition_kwargs,
                                       storename=self.storename)
            elif self.related_table:
                value = HTableResolver(table=self.table, rootpath='*related*:%s' % row['pkey'],
                                       relation_path=self.relation_path,
                                       related_extra_columns=self.related_extra_columns,
                                       related_fullrecord=self.related_fullrecord,
                                       related_table=self.related_table,
                                       related_order_by=self.related_order_by,storename=self.storename,
                                       _page=self._page)
                child_count = 1
                
            else:
                value = None
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            caption = tblobj.recordCaption(row, rowcaption=get_tree_row_caption(tblobj))
            children.setItem(row['child_code'], value,
                             caption=caption,
                             rec_type=row['rec_type'], pkey=row['pkey'], code=row['code'], child_count=child_count,
                             checked=False,
                             parent_code=row['parent_code'], description=row['description'],
                             _record=dict(row))#_attributes=dict(row),
            #
            
        children.sort('#a.caption')
        return children
    
    def getConditionCodes(self):
        if self._condition_id:
            condition_codes = self._page.pageStore().getItem('hresolver.%s' %self._condition_id)
        else:
            self._condition_id = self._page.getUuid()
            db = self._page.db
            tblobj = db.table(self.table)
            condition_kwargs = self.condition_kwargs or dict()
            valid = tblobj.query(where='$child_count=0 AND ( %s ) AND $parent_code IS NOT NULL' %self.condition,columns='$id,$parent_code',**condition_kwargs).fetchAsBag('parent_code')
            condition_codes = valid.getIndexList()
            with self._page.pageStore() as store:
                store.setItem('hresolver.%s' %self._condition_id,condition_codes)
        return condition_codes

        
    def setRelatedChildren(self, children):
        db = self._page.db
        related_tblobj = db.table(self.related_table)
        related_rows = []
        if self.rootpkey:
            related_rows = related_tblobj.query(where='%s=:pkey' % self.relation_path[1:], pkey=self.rootpkey).fetch()
            for related_row in related_rows:
                caption = related_tblobj.recordCaption(related_row)
                children.setItem(related_row['pkey'], None,
                                 caption=caption,
                                 pkey=related_row['pkey'], code=related_row['code'],
                                 node_class='tree_related')
                                 
    def resolverSerialize(self):
        self._initKwargs.pop('_page')
        return BagResolver.resolverSerialize(self)
        
class HTableHandlerBase(BaseComponent):
    """TODO"""
    
    @struct_method
    def ht_hdbselect_old(self,pane,**kwargs):
        dbselect = pane.dbselect(**kwargs)
        attr = dbselect.attributes
        menupath = 'gnr.htablestores.%(dbtable)s' %attr
        attr['hasDownArrow'] = True
        dbselect_condition = attr.get('condition')
        dbselect_condition_kwargs = dictExtract(attr,'condition_')
        attr['condition'] = '$child_count=0' if not dbselect_condition else ' ( %s ) AND $child_count=0' %dbselect_condition
        pane.dataRemote(menupath,self.ht_remoteTreeData,table=attr['dbtable'],
                        condition=dbselect_condition,
                        condition_kwargs=dbselect_condition_kwargs,cacheTime=30)
        dbselect.menu(storepath='%s._root_' %menupath,_class='smallmenu',modifiers='*',selected_pkey=attr['value'].replace('^',''))
        
    @struct_method
    def ht_htableStore(self, pane, table=None, related_table=None, relation_path=None, storepath='.store',
                        storename=None,rootcaption=None,rootcode=None,rootpkey=None,rootpath=None,**kwargs):
        rootcode = rootcode or ROOTCODE
        rootpkey = rootpkey or ROOTCODE
        if '@' in table:
            pkg, related_table, relation_path = table.split('.')
            related_table = '%s.%s' % (pkg, related_table)
            related_table_obj = self.db.table(related_table)
            table = related_table_obj.column(relation_path).parent.fullname
        tblobj = self.db.table(table)            
        
        data = self.ht_treeDataStore(table=table,
                                     related_table=related_table,
                                     relation_path=relation_path,
                                     rootcaption=rootcaption or tblobj.name_plural, 
                                     storename=storename,rootpath=rootpath,
                                     rootcode=rootcode,rootpkey=rootpkey,
                                     **kwargs)
        pane.data(storepath, data,rootpath=rootpath)
    
    @public_method
    def ht_remoteTreeData(self, *args,**kwargs):
        if 'storename' in kwargs:
            self.db.use_store(kwargs['storename'])
        return self.ht_treeDataStore(*args,**kwargs)
    
    
    @extract_kwargs(condition=True)
    def ht_treeDataStore(self, table=None, rootpath=None,
                         related_table=None,
                         relation_path=None,
                         limit_rec_type=None,
                         rootcaption=None,
                         rootcode=None,
                         rootpkey=None,
                         extra_columns=None,
                         related_extra_columns=None,
                         related_order_by=None,
                         related_fullrecord=True,
                         storename=None,condition=None,condition_kwargs=None,**kwargs):
        columns = '$code,$parent_code,$description,$child_code,$child_count,$rec_type'
        if extra_columns:
            columns = '%s,%s' %(columns,extra_columns) 
        result = Bag()
        value = HTableResolver(table=table, rootpath=rootpath, limit_rec_type=limit_rec_type, _page=self,
                               related_table=related_table, relation_path=relation_path,extra_columns=extra_columns,
                               related_extra_columns=related_extra_columns,
                               related_order_by=related_order_by,related_fullrecord=related_fullrecord,storename=storename,
                               condition=condition,condition_kwargs=condition_kwargs) #if child_count else None
        rootlabel,attr = self._ht_rootNodeAttributes(table=table,rootpath=rootpath,columns=columns,
                                                            rootcaption=rootcaption,rootcode=rootcode,
                                                            rootpkey=None,storename=storename)
        result.setItem(rootlabel, value, checked=False,**attr)
        return result
    
    
        
    def _ht_rootNodeAttributes(self,table=None,rootpath=None,columns=None,rootcaption=None,rootcode=None,rootpkey=None,storename=None):
        tblobj = self.db.table(table)
        if rootpath:
            row = tblobj.query(columns=columns, where='$code=:code', code=rootpath).fetch()[0]
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            with self.db.tempEnv(storename=storename):
                caption = tblobj.recordCaption(row, rowcaption=get_tree_row_caption(tblobj))
            rootlabel = row['child_code']
            pkey = row['pkey']
            rootpath = row['code']
            code = row['code']
            child_count = row['child_count']
        else:
            caption = rootcaption or tblobj.name_plural
            rootlabel = '_root_'
            pkey = rootpkey
            code = rootcode
            rootpath = None
            row = dict()
            with self.db.tempEnv(storename=storename):
                child_count = tblobj.query().count()
        return rootlabel,dict(_record=dict(row),caption=caption,pkey=pkey,code=code,child_count=child_count)
        
        
class HTableHandler(HTableHandlerBase):
    """A class to handle the :ref:`h_th_component` component"""
    py_requires = 'gnrcomponents/selectionhandler:SelectionHandler'
    css_requires = 'public'
    
    def htableHandler(self, parent, nodeId=None, datapath=None, table=None, rootpath=None, label=None,
                      editMode='bc', childTypes=None, dialogPars=None, loadKwargs=None, parentLock=None,
                      where=None, onChecked=None, plainView=False, childsCodes=False, noRecordClass='noRecordSelected',
                      picker=None):
        """TODO
        
        :param parent: the parent path
        :param nodeId: MANDATORY. The :ref:`nodeid`
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param table: MANDATORY. The :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param rootpath: TODO
        :param label: TODO
        :param editMode: the GUI of the hTableHandler; set:
                         
                         * ``bc`` to use a :ref:`bordercontainer`
                         * ``sc`` to use a :ref:`stackcontainer`
                         * ``dlg`` to use a :ref:`simpledialog`
                                                  
        :param childTypes: TODO
        :param dialogPars: MANDATORY if you set the *editMode* attribute to ``dlg``. TODO
        :param loadKwargs: TODO
        :param parentLock: TODO
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param onChecked: TODO
        :param plainView: boolean. TODO
        :param childsCodes: tuple(path,field). Return a list of values of all the selected node childs at a given path.
                            Useful to list, via a selectionHandler or an includedView ... , both all the records related
                            to the selected node and those related to the children nodes
        :param noRecordClass: TODO
        
        CLIPBOARD::
        
            .tree: tree data:
                            store
                            **selected elements
            .edit (sym #nodeId_edit): pane data: **controllers
                                           form
                                           record
            controllerNodeId:nodeId_edit"""
        disabled = '^#%s.edit.status.locked' % nodeId
        parent.attributes.update(table=table)
        if childsCodes:
            childsCodesDiv = parent.div(datapath=datapath)
            if isinstance(childsCodes, tuple):
                childsCodesPath = childsCodes[0]
                field = childsCodes[1]
                childsCodesDiv.dataRpc(childsCodesPath, self.getChildsIds, field=field, code='^.edit.record.code',
                                       table=table)
            else:
                childsCodesDiv.dataRpc(childsCodes, self.getChildsIds, field=None, code='^.edit.record.code', table=table)
                
        if parentLock:
            parent.dataController("SET .edit.status.locked=parentLock;", parentLock=parentLock, datapath=datapath)
            parent.dataController("""SET %s=isLocked;""" % parentLock[1:],
                                  parentLock=parentLock, isLocked='^.edit.status.locked',
                                  _if='parentLock!=isLocked', datapath=datapath)
                                  
        formPanePars = dict(selectedPage='^.edit.selectedPage')
        commonTop=None
        if plainView:
            tc = parent.tabContainer(nodeId='%s_tc' % nodeId, region='center')
            parent = tc.contentPane(title='!!Hierarchical')
            self.ht_plainView(tc.borderContainer(title='!!Plain', datapath=datapath), table=table, nodeId=nodeId,
                              disabled=disabled,
                              rootpath=rootpath, editMode=editMode, label=label)
                              
        if editMode == 'bc':
            ht = bc = parent.borderContainer(region='center', datapath=datapath, nodeId=nodeId, design='sidebar',_class='hideSplitter')
            treepane = bc.framePane(region='left', width='220px', splitter=True,rounded=6,border='1px solid silver',margin='2px',childname='treepane')
            frame = bc.framePane(region='center',rounded=6,margin='2px',border='1px solid silver',childname='editpane')
            formBC = frame.center
            commonTop = frame.top
            
        elif editMode == 'sc':
            ht = sc = parent.stackContainer(region='center', datapath=datapath, nodeId=nodeId,
                                       selectedPage='^.selectedPage', margin='2px')
            treepane = sc.framePane(pageName='tree',rounded=6,border='1px solid silver')
            formPanePars['pageName'] = 'edit'
            formBC = sc.borderContainer(region='center')
            
        elif editMode == 'dlg':
            assert dialogPars, 'for editMode == "dlg" dialogPars are mandatory'
            ht = treepane = parent.framePane(region='center', datapath=datapath, nodeId=nodeId, margin='2px',
                                              _class='pbl_roundedGroup')
            formBC = self.simpleDialog(treepane, dlgId='%s_dlg' % nodeId, **dialogPars)
            formPanePars['region'] = 'center'
            
            
            #recordlabel = formBC.contentPane(region='top',_class='pbl_roundedGroupLabel')
            #recordlabel.div('^.edit.record?caption')
        if editMode == 'dlg':
            footer = formBC.contentPane(region='bottom', _class='pbl_roundedGroupBottom')
            footer.button('!!Close', fire='.close')
        formpane = formBC.stackContainer(pageName='edit', **formPanePars)
        
        self.ht_tree(treepane, table=table, nodeId=nodeId, disabled=disabled,
                     rootpath=rootpath, childTypes=childTypes, editMode=editMode, 
                     label=label, onChecked=onChecked,picker=picker)
        self.ht_edit(formpane, table=table, nodeId=nodeId, disabled=disabled,
                     rootpath=rootpath, editMode=editMode, loadKwargs=loadKwargs,
                     childTypes=childTypes, commonTop=commonTop, noRecordClass=noRecordClass)
        return ht
    @public_method          
    def getChildsIds(self, code=None, field=None, table=None):
        field = field or 'code'
        records = self.db.table(table).query(field, where='($code LIKE :code)', code='%s%%' % code,
                                             addPkeyColumn=False).fetch()
        return str([str(f[field]) for f in records]) + '::JS'
        
    def ht_edit_dlg_bottom(self, bc, **kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Close', fire='.close')
        
    def ht_edit(self, sc, table=None, nodeId=None, disabled=None, rootpath=None, editMode=None, loadKwargs=None,
                childTypes=None, commonTop=None, noRecordClass=''):
        formId = '%s_form' % nodeId
        norecord = sc.contentPane(id='no_record_page', pageName='no_record').div('', _class=noRecordClass)
        bc = sc.borderContainer(pageName='record_selected')
        top = commonTop if editMode == 'bc' else bc.contentPane(region='top', overflow='hidden')
        toolbar = top.slotToolbar('2,breadcrumb,*,hdelete,hadd,hsave,hrevert,hsemaphre,hlock',height='20px')
        toolbar.dataFormula('.edit.status.locked', True, _onStart=True)
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
                             SET .edit.status.statusClass = isLocked?'iconbox lock':'iconbox unlock';
                             SET .edit.status.lockLabel = isLocked?unlockLabel:lockLabel;
                             genro.dom.setClass(toolbar,'lockedToolbar',isLocked);
                               """, isLocked="^.edit.status.locked", lockLabel='!!Lock',
                               unlockLabel='!!Unlock',toolbar=toolbar)
                               
        self.ht_edit_toolbar(toolbar, nodeId=nodeId, disabled=disabled, editMode=editMode, childTypes=childTypes)
        bc.dataController("""
                            if(pkey){
                                SET .edit.selectedPage='record_selected';
                                SET .edit.no_record = false;
                            }else{
                                SET .edit.selectedPage='no_record';
                                SET .edit.no_record = true;                                
                            }
                            """, pkey="^.tree.pkey",_onStart=True)
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){
                                genro.setData('#%s.tree.pkey',currPkey);
                                genro.setData('#%s.tree.path',rootpath?currPkey.slice(rootpath.length-1):currPkey);
                                };
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ % (nodeId, nodeId), rootpath='=.tree.store?rootpath',
                          selPkey='^.tree.pkey', currPkey='=.edit.pkey', _if='selPkey && (selPkey!=currPkey)',
                          formId=formId)
                          
        bc.dataController("""
                             var rootpath = rootpath || null;
                             if (destPkey!='*newrecord*' && !oldChildCode){
                                 var editNode = treestore.getNode(treepath);
                                 var attr= editNode.attr;
                                 attr.caption = treeCaption;
                                 editNode.setAttr(attr);
                                 FIRE .edit.load;
                             }else{
                                SET .edit.pkey = savedPkey;
                                FIRE .edit.load;
                             }
                         """,
                          _fired="^.edit.onSaved", destPkey='=.tree.pkey', parent_code='=.edit.record.parent_code',
                          savedPkey='=.edit.savedPkey', rootpath='=.tree.store?rootpath',
                          treepath='=.tree.path', treestore='=.tree.store',oldChildCode='=.edit.record.child_code?_loadedValue',
                          treeCaption='=.edit.savedPkey?caption',_delay=1)
        bc.dataController("""
                            if (rootpath){
                                path=code.slice(rootpath.length);
                            }else{
                                path = code?'_root_.'+code:'_root_';
                            }
                            SET .tree.path=path;
                            """, 
                            code="^.edit.record.code",
                          rootpath='=.tree.store?rootpath', 
                          _if='code')
                          
        bc.dataRpc('.edit.del_result', 'deleteDbRow', pkey='=.edit.pkey',
                   _POST=True, table=table, _delStatus='^.edit.delete',
                   _if='_delStatus=="confirm"', _else='genro.dlg.ask(title,msg,null,"#%s.edit.delete")' % nodeId,
                   title='!!Deleting record', msg='!!You cannot undo this operation. Do you want to proceed?',
                   _onResult="""var path = $2.currpath.split('.');
                                path.pop();
                                var path = path.join('.');
                                $2.treestore.getNode(path).refresh(true)
                                SET .tree.path = path;""", currpath='=.tree.path', treestore='=.tree.store')
        
        center = bc.contentPane(region='center',formId=formId,datapath='.edit',
                                controllerPath='#%s.edit.form' % nodeId,formDatapath='.record',
                                pkeyPath='#%s.edit.pkey' % nodeId)
        getattr(self, formId)(center,table=table,
                              datapath='.record',
                              disabled=disabled)
        center.dataController("FIRE .edit.controller.loaded;",_fired="^.edit.form.loaded",datapath='#%s' %nodeId) #COMPATIBILITY FIX
        tblobj = self.db.table(table)
        loadKwargs = loadKwargs or dict()
        loadKwargs['default_parent_code'] = '=.defaults.parent_code'
        self.formLoader(formId, datapath='#%s.edit' % nodeId, resultPath='.record', _fired='^.load',
                        table=table, pkey='=.pkey', **loadKwargs)
        self.formSaver(formId, datapath='#%s.edit' % nodeId, resultPath='.savedPkey', _fired='^.save',
                       table=table, onSaved='FIRE .onSaved;',
                       #onSaving='console.log($1.getNode("child_code"))',
                       rowcaption=_getTreeRowCaption(self.db.table(table)))
                       
    def _ht_add_button(self, pane, childTypes=None, disabled=None):
        if childTypes:
            storepath = childTypes
            if isinstance(childTypes, dict):
                childTypesMenu = Bag()
                storepath = '.tree.childTypesMenu'
                for k, v in childTypes.items():
                    childTypesMenu.setItem(k, None, caption=v)
                    pane.data(storepath, childTypesMenu)
            ddb = pane.div(label='!!Add', hidden=disabled,
                           margin='2px', _class='iconbox add_record', showLabel=False,
                           visible='==_tree_caption!=null',
                           _tree_caption='^.tree.caption', _storepath=storepath)
                           
            ddb.menu(storepath=storepath, modifiers='*', _class='smallmenu',
                     action="SET .edit.childType = $1.fullpath; FIRE .edit.add_child;")
        else:
            pane.slotButton(label='!!Add Sibling',  disabled=disabled,
                        iconClass='iconbox add_record',
                        action='FIRE .edit.add_sibling;', visible='==tree_caption!=null',
                        tree_caption='^.edit.record.code')
                        
    def ht_edit_toolbar(self, toolbar, nodeId=None, disabled=None, editMode=None, childTypes=None):
        nav = toolbar.breadcrumb.div(nodeId='%s_nav' % nodeId)
        self._ht_add_button(toolbar.hadd, childTypes=childTypes, disabled=disabled)
        toolbar.dataController("""
                            var pathlist = currpath.split('.').slice(1);
                            var rootName = this.getRelativeData('.tree.store.#0?caption');
                            var rootnode = genro.nodeById(labelNodeId)
                            if(store){
                            }else{
                            }
                            //var nodeattr = store.getNode(currpath).attr;
                            rootnode.freeze().clearValue();
                            var label;
                            var path2set = '_root_';
                            var row = rootnode._('table',{'border_spacing':0})._('tbody')._('tr');
                            row._('td')._('div',{'connect_onclick':"this.setRelativeData('.tree.path','_root_');",
                                                 _class:'bread_root',tip:rootName});
                            for(var i=0;i<pathlist.length;i++){
                                
                                label = pathlist[i];
                                path2set = path2set+'.'+label;
                                row._('td')._('div',{'_class':'bread_middle'});
                                var action = "this.setRelativeData('.tree.path','"+path2set+"');";
                                row._('td',{'innerHTML':label,'connect_onclick':action,_class:'iconbox_text',tip:this.getRelativeData('.tree.store.'+path2set+'?description')});
                            }
                            row._('td')._('div',{'_class':'last_bread_middle bread_middle'});
                            var add_action = "FIRE .edit.add_child;";
                            row._('td')._('div',{'_class':'bread_add',connect_onclick:add_action});
                            rootnode.unfreeze();
                            """,
                               labelNodeId='%s_nav' % nodeId,
                               currpath='^.tree.path',store='=.tree.store',
                               add_label='!!Add')
                               
        toolbar.dataController("""
                                SET .edit.defaults.parent_code = parent_code==ROOTCODE?null:parent_code;
                                SET .tree.pkey ='*newrecord*';                                         
                                """, parent_code='=.tree.code',
                               modifier="^.edit.add_child",ROOTCODE=ROOTCODE)
                               
        toolbar.dataController("""
                                SET .edit.defaults.parent_code = GET .edit.record.parent_code;
                                SET .tree.pkey = '*newrecord*';                                  
                                """, tree_code='=.tree.code',
                               modifier="^.edit.add_sibling")
        
        toolbar.hlock.slotButton(label='^.edit.status.lockLabel', action='FIRE .edit.status.changelock;',
                                 iconClass="^.edit.status.statusClass")
        toolbar.dataController("""genro.dom.removeClass(semaphoreId,"greenLight redLight yellowLight");
              if(isValid){
                 if(isChanged){
                     genro.dom.addClass(semaphoreId,"yellowLight");
                 }else{
                     genro.dom.addClass(semaphoreId,"greenLight");
                 }
              }else{
                    genro.dom.addClass(semaphoreId,"redLight");
              }
              """, isChanged="^.edit.form.changed", semaphoreId='%s_semaphore' % nodeId,
                              isValid='^.edit.form.valid')
        toolbar.hsemaphre.div(nodeId='%s_semaphore' % nodeId, _class='semaphore', hidden='^.edit.no_record')
        toolbar.hsave.slotButton('!!Save', action="FIRE .edit.save", float='right',
                                  iconClass="iconbox save",
                                  hidden='^.edit.no_record',
                                  disabled=disabled)
        toolbar.hrevert.slotButton('!!Revert', action="FIRE .edit.load;", iconClass="iconbox revert",
                       hidden='^.edit.no_record',
                       disabled=disabled)
        toolbar.hdelete.slotButton('!!Delete', action="FIRE .edit.delete;", iconClass='iconbox delete_record',
                                    disabled=disabled,
                                    hidden='^.edit.no_record'
                                    #visible='^.edit.enableDelete'
                                    )
        toolbar.dataFormula('.edit.enableDelete', 'child_count==0', child_count='^.edit.record.child_count')
        
        if editMode == 'sc':
            toolbar.button('!!Tree', action="SET .selectedPage = 'tree';")
            
    def ht_plainView(self, bc, table=None, nodeId=None, disabled=None,
                     rootpath=None, editMode=None, label=None):
        gridId = '%s_grid' % nodeId
        default_selectionPars = dict(order_by='$code')
        dialogParsCb = getattr(self, '%s_dialogPars' % gridId, None)
        dialogPars = None
        if dialogParsCb:
            dialogPars = dialogParsCb()
        if rootpath:
            default_selectionPars = dict(where='$code LIKE %%:rootpath', rootpath=rootpath, order_by='$code')
        self.selectionHandler(bc, label=label, datapath=".plainview",
                              nodeId=gridId, table=table, add_enable=False, del_enable=False,
                              struct=getattr(self, '%s_struct' % gridId, None),
                              parentLock=disabled, _onStart=True,
                              selectionPars=getattr(self, '%s_selectionPars' % gridId, default_selectionPars),
                              dialogPars=dialogPars,
                              filterOn=getattr(self, '%s_filterOn' % gridId, '$code,$description'))
    @struct_method
    def ht_htableTypePicker(self,pane,field=None,paletteCode=None):
        table = pane.getInheritedAttributes()['table']
        nodeId = pane.getInheritedAttributes()['nodeId']
        treeNode = self.pageSource().nodeById('%s_tree' %nodeId)
        typetblobj = self.db.table(pane.getInheritedAttributes()['table']).column(field).relatedTable().dbtable
        typetbl = typetblobj.fullname
        paletteCode = paletteCode or '%s_picker' %typetbl.replace('.','_')
        title = typetblobj.name_long or '!!Picker'
        if hasattr(typetblobj,'htableFields'):
            pane.paletteTree(paletteCode=paletteCode,dockButton=True,title=title,tree_dragTags=paletteCode).htableStore(table=typetbl)
        else:
            struct = getattr(self,'%s_picker_struct' %nodeId,self._ht_picker_auto_struct)
            pane.paletteGrid(paletteCode=paletteCode,struct=struct,dockButton=True,title=title,grid_dragTags=paletteCode).selectionStore(table=typetbl)
        treeattr = treeNode.attr
        dropTags = treeattr.get('dropTags')
        dropTags = dropTags.split(',') if dropTags else []
        dropTags.append(paletteCode)
        treeattr['dropTags'] = ','.join(dropTags)
        treeattr['onDrop_%s' %paletteCode] = self.__ht_onDropInsert(field,table,typetbl)
    

    def __ht_onDropInsert(self,field=None,table=None,typetbl=None):
        return """var types = [];
                if(data instanceof Array){
                    dojo.forEach(data,function(n){types.push(n._pkey)})
                }else{
                    types[0] = data['pkey'];
                }
                var that = this;
                var onResult = function(result){
                    that.setRelativeData('.tree.path','_root_.'+result);
                }
                var cb= function(count){
                    genro.serverCall('ht_createChildren',{types:types,parent_code:dropInfo.treeItem.attr.code,
                                    type_field:'%s',maintable:'%s',typetable:'%s',how_many:count},onResult,null,'POST');
                }
            if(dropInfo.modifiers=='Shift' && types.length==1){
                var dlg = genro.dlg.quickDialog('Multiple insertion',{_showParent:true,width:'250px'});
                var msg = 'How many copies do you want to insert?';
   
                dlg.center._('div',{innerHTML:_T(msg), text_align:'center',height:'20px'});
                var that = this;
                genro.setData('gnr._dev.addrecord.count',null);
                var slotbar = dlg.bottom._('slotBar',{slots:'*,cancel,confirm',
                                                    action:function(){
                                                        dlg.close_action();
                                                        if(this.attr.command='confirm'){
                                                             cb(that.getRelativeData("gnr._dev.addrecord.count"));
                                                        }
                                                    }});
                slotbar._('button','cancel',{label:'Cancel',command:'cancel'});
                var fb = genro.dev.formbuilder(dlg.center._('div',{margin:'5px'}),1);
                fb.addField('numberTextBox',{value:'^gnr._dev.addrecord.count',width:'5em',lbl:'Count',parentForm:false});
                slotbar._('button','confirm',{label:'Confirm',command:'confirm'});
                dlg.show_action();
            }else{
                cb();
            }""" %(field,table,typetbl)
        
        
    @public_method
    def ht_createChildren(self,maintable=None,typetable=None,types=None,type_field=None,parent_code=None,how_many=None):
        if not types:
            return
        tblobj = self.db.table(maintable)
        typetable = self.db.table(typetable)
        htype = hasattr(typetable,'htableFields')
        if htype:
            caption_cols = ['$code','$description']
        else:
            caption_cols,format = typetable.rowcaptionDecode(typetable.rowcaption)
        defaultDescriptions = typetable.query(where='$pkey IN :types',types=types,columns=','.join(caption_cols)).fetchAsDict('pkey')
        last_child = tblobj.query(where='$parent_code=:pcode' if parent_code else '$parent_code IS NULL',pcode=parent_code,order_by='child_code desc',limit=1).fetch()
        start_t =0
        if how_many:
            start_t = tblobj.query(where='$parent_code=:pcode AND $%s=:t' %type_field if parent_code else '$parent_code IS NULL AND $%s=:t' %type_field,
                                    pcode=parent_code, t=types[0],order_by='child_code desc',limit=1).count() +1
        
        start_n = 1
        digits = 2
        if last_child:
            last_child = last_child[0]
            if last_child['child_code'].isdigit():
                start_n = int(last_child['child_code'])+1
                digits = len(last_child['child_code'])

        def defaultInsertRecord(parent_code=None,type_field=None,type_id=None,offset=None,last_child=None):
            r = dict()
            c = start_n+offset
            d = start_t+offset
            r['parent_code'] = parent_code
            r['child_code'] = str(c).zfill(digits)
            typerec = defaultDescriptions[type_id]
            desc = typerec['description'] or typerec['code'] if htype else typetable.recordCaption(typerec)
            r['description'] = '%s %i' %(desc,d) if how_many else desc
            r[type_field] = type_id
            tblobj.insert(r)
            return r['code']
            
        insertRecord = getattr(tblobj,'ht_insertFromType',defaultInsertRecord)            
        if how_many and len(types) == 1:

            
            for i in range(how_many):
                last_code = insertRecord(parent_code=parent_code,type_field=type_field,type_id=types[0],offset=i,last_child=last_child)
        else:
            for i,type_id in enumerate(types):
                last_code= insertRecord(parent_code=parent_code,type_field=type_field,type_id=type_id,offset=i,last_child=last_child)        
        self.db.commit()
        return last_code
            

    def _ht_picker_auto_struct(self,struct):
        maintable = struct.maintable
        if struct.maintable:
            t = self.db.table(maintable)
            cols,format = t.rowcaptionDecode(t.rowcaption)
            r = struct.view().rows()
            for col in cols:
                r.fieldcell(col.replace('$',''),width='100%')
        
    def ht_tree(self, frame, table=None, nodeId=None, rootpath=None, disabled=None,
                childTypes=None, editMode=None, label=None, onChecked=None,picker=None):
        rootcode=ROOTCODE
        rootpkey=ROOTCODE
        if editMode != 'bc':
            top = frame.top.div(_class='pbl_roundedGroupLabel')
            top.div(label, float='left')
            self._ht_add_button(top.div(float='left'), disabled=disabled, childTypes=childTypes)
            
        tblobj = self.db.table(table)
        center = frame.center.contentPane(region='center',gradient_from='white',gradient_to='#D5DDE5',gradient_deg='360')
        center.data('.tree.store', self.ht_treeDataStore(table=table, rootpath=rootpath, rootcaption=tblobj.name_plural,rootcode=rootcode,rootpkey=rootpkey)
                    ,rootpath=rootpath)
                    
        connect_ondblclick = None
        if editMode == 'sc':
            connect_ondblclick = 'SET .selectedPage = "edit";'
        elif editMode == 'dlg':
            connect_ondblclick = 'FIRE #%s_dlg.open;' % nodeId
        tree = center.hTableTreeLegacy(storepath='.tree.store',nodeId='%s_tree' %nodeId,table=table,onChecked=onChecked,
                                connect_ondblclick=connect_ondblclick)
        treeattr = tree.attributes
        moverCode = 'mover_%s' %table.replace('.','_')
        treeattr['onDrop_%s' %moverCode] = """genro.serverCall('developer.importMoverLines',{table:data.table,pkeys:data.pkeys,objtype:data.objtype});"""   
        bar = frame.top.slotToolbar('2,tblname,*',height='20px')
        bar.tblname.div(tblobj.name_long)
        if picker:
            bar.replaceSlots('#','#,picker')
            bar.picker.htableTypePicker(picker)
        
    @struct_method
    def ht_hTableTreeLegacy(self,pane,nodeId=None,storepath=None,table=None,dragCode=None,**kwargs):
        tablecode = table.replace('.','_')
        nodeId = nodeId or '%s_tree' %tablecode
        dragCode = dragCode or '%s_record' %tablecode
        tree = pane.tree(nodeId=nodeId,storepath=storepath,
                    margin='10px', isTree=False, hideValues=True,
                    inspect='shift', labelAttribute='caption',
                    selected_pkey='.tree.pkey', selectedPath='.tree.path',
                    selected_rec_type='.tree.rec_type',
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_caption='.tree.caption',
                    selected_child_count='.tree.child_count',
                    identifier='pkey',
                    dragTags=dragCode,
                    dropTags='%s,mover' %dragCode,
                    dropTypes='nodeattr',draggable=True,
                     onDrag="""dragValues['dbrecords'] = {table:'%s',code:treeItem.attr['code']||'*',objtype:'record'}; """ %table,
                     onDrop="""if(dropInfo.dragSourceInfo.nodeId!=dropInfo.sourceNode.attr.nodeId){
                                    return;
                                };
                                var into_pkey = dropInfo.treeItem.attr.pkey;
                                var pkey = data['nodeattr'].pkey;
                                genro.serverCall("_table.%s.reorderCodes",{pkey:pkey,into_pkey:into_pkey},
                                                 function(result){
                                                    if(!result){
                                                        genro.dlg.alert("Not allowed","Warning");
                                                    }
                                                 });""" %table,
                     dropTargetCb="""var dragged_record = genro.dom.getFromDataTransfer(dropInfo.event.dataTransfer,'nodeattr');
                                    if(dropInfo.dragSourceInfo.nodeId!=dropInfo.sourceNode.attr.nodeId){
                                        return true;
                                    }
                                    var ondrop_record = dropInfo.treeItem.attr;
                                    if(ondrop_record.code.indexOf(dragged_record.code+'.')==0){
                                        return  false;
                                    }
                                    if(dragged_record.parent_code==ondrop_record.code){
                                        return false;
                                    }
                                    if(dragged_record.pkey==ondrop_record.pkey){
                                        return false;
                                    }
                                    return true;
                                    """,**kwargs)     
        pane.onDbChanges(action="""var selectedNode = treeNode.widget.currentSelectedNode;
                                    var selectedPkey = selectedNode? selectedNode.item.attr.pkey:'';       
                                    var selectedCode =null;                             
                                    var refreshDict = {};
                                    var n,child_count,content;
                                    treeNode.widget.saveExpanded()
                                    dojo.forEach(dbChanges,function(c){
                                        refreshDict[c.parent_code || ROOTCODE] = true;
                                        if(c.pkey==selectedPkey){
                                            selectedCode = c.code;
                                        }
                                        if(c.old_parent_code != c.parent_code){
                                            refreshDict[c.old_parent_code || ROOTCODE] = true;
                                        }
                                     });
                                     var refreshed = {};
                                     for (var k in refreshDict){
                                        n = store.getNodeByAttr('code',k);
                                        if(n && !(n.attr.code in refreshed)){
                                            if(n.getResolver()){
                                                n.refresh(true)
                                                refreshed[n.attr.code] = true;
                                                content = n.getValue();
                                                child_count = (content instanceof gnr.GnrBag)?content.len():0;
                                                n.updAttributes({'child_count':child_count});
                                            }else{
                                                n = n.getParentNode();
                                                if(n && n.getResolver() && !(n.attr.code in refreshed)){
                                                    n.refresh(true);
                                                    refreshed[n.attr.code] = true;
                                                }
                                            }
                                        }                     
                                     }
                                     treeNode.widget.restoreExpanded()
                                     if(selectedPkey){
                                         n = store.getNodeByAttr('pkey',selectedPkey);
                                         if(n){
                                            var p = n.getFullpath(null, treeNode.widget.model.store.rootData());
                                            treeNode.widget.setSelectedPath(null,{value:p});
                                         }else{
                                            treeNode.widget.setSelectedPath(null,{value:'_root_.'+selectedCode});
                                         }
                                     }
                                     """,table=table,store='=%s' %storepath,treeNode=tree,ROOTCODE=ROOTCODE)
        return tree

                                    
class HTablePicker(HTableHandlerBase):
    py_requires = 'foundation/dialogs,foundation/includedview:IncludedView'
    
    def htablePicker(self, parent, table=None, rootpath=None, limit_rec_type=None,
                     input_codes=None,
                     output_codes=None,
                     output_pkeys=None,
                     nodeId=None, datapath=None, dialogPars=None,
                     caption=None, grid_struct=None, grid_columns=None,
                     grid_show=False,
                     condition=None, condition_pars=None,
                     editMode='dlg', **kwargs):
        self._htablePicker_main(parent, table=table, rootpath=rootpath, limit_rec_type=limit_rec_type,
                                input_codes=input_codes, output_codes=output_codes,
                                output_pkeys=output_pkeys,
                                nodeId=nodeId, grid_show=grid_show,
                                datapath=datapath, dialogPars=dialogPars, grid_struct=grid_struct,
                                grid_columns=grid_columns, editMode=editMode,
                                condition=condition, condition_pars=condition_pars)
                                
    def htablePickerOnRelated(self, parent, table=None, rootpath=None, limit_rec_type=None,
                              input_pkeys=None, output_pkeys=None,
                              related_table=None, relation_path=None,
                              nodeId=None, datapath=None, dialogPars=None,
                              caption=None, grid_struct=None, grid_columns=None,
                              grid_applymethod=None,
                              
                              grid_filter=None, default_checked_row=None,
                              condition=None, condition_pars=None, editMode=None, **kwargs):
        self._htablePicker_main(parent, table=table, rootpath=rootpath,
                                limit_rec_type=limit_rec_type,
                                related_table=related_table,
                                relation_path=relation_path,
                                input_pkeys=input_pkeys or '', output_related_pkeys=output_pkeys, nodeId=nodeId,
                                grid_filter=grid_filter,
                                datapath=datapath, dialogPars=dialogPars, grid_struct=grid_struct,
                                grid_columns=grid_columns,
                                grid_applymethod=grid_applymethod,
                                condition=condition, condition_pars=condition_pars, editMode=editMode,
                                default_checked_row=default_checked_row)
                                    
    def _htablePicker_main(self, parent, table=None, rootpath=None, limit_rec_type=None,
                           input_pkeys=None,
                           input_codes=None,
                           output_pkeys=None,
                           output_related_pkeys=None,
                           grid_show=True,
                           output_codes=None,
                           nodeId=None, datapath=None, dialogPars=None,
                           caption=None, grid_struct=None, grid_columns=None,
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
            
        editMode = editMode or 'dlg'
        grid_where = '$code IN :codes'
        if related_table:
            grid_where = '%s IN :codes' % relation_path
        if condition:
            grid_where = '%s AND %s' % (grid_where, condition)
        condition_pars = condition_pars or dict()
            
        tblobj = self.db.table(table)
        default_width = '300px'
        if grid_show:
            default_width = '600px'
        params = dict(caption=caption, table=table,
                      grid_struct=grid_struct, grid_columns=grid_columns,
                      grid_where=grid_where, condition_pars=condition_pars,
                      output_codes=output_codes, output_pkeys=output_pkeys,
                      related_table=related_table, grid_show=grid_show, grid_filter=grid_filter,
                      grid_applymethod=grid_applymethod,
                      default_checked_row=default_checked_row,
                      output_related_pkeys=output_related_pkeys)
                      
        if editMode == 'dlg':
            dialogPars = dialogPars or dict()
            dialogPars['title'] = dialogPars.get('title', '%s picker' % tblobj.name_long)
            dialogPars['height'] = dialogPars.get('height', '400px')
            dialogPars['width'] = dialogPars.get('width', default_width)
            params.update(dialogPars)
            bc = self.formDialog(parent, datapath=datapath, formId=nodeId,
                                 cb_center=self.ht_pk_center, **params)
            bc.dataController("FIRE .open;", **{"subscribe_%s_open" % nodeId: True})
        elif editMode == 'bc':
            bcId = '%s_bc' % nodeId
            bc = parent.borderContainer(datapath=datapath, height='100%', nodeId=bcId)
            #bc.contentPane(region='top',_class='pbl_roundedGroupLabel').div('%s picker' %tblobj.name_long)
            #bottom = bc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
            bc.dataController("genro.formById(fid).load()", _onStart=True, fid=nodeId,
                              **{"subscribe_%s_open" % nodeId: True})
            # bc.dataController("genro.formById(fid).load()",_onStart=True,fid=nodeId,**{"subscribe_%s_open" %nodeId:True)
            
            #bottom.button('!!Confirm', action='genro.formById(fid).save(true})',
            #                fid=nodeId,float='right')
            bc.dataController('genro.formById(fid).loaded();', fid=nodeId, _fired="^.loaded")
            bc.dataController('genro.formById(fid).saved();', fid=nodeId, _fired="^.saved")
            
            self.ht_pk_center(bc, region='center',
                              formId=nodeId, #form parameter
                              datapath='.data', #form parameter
                              controllerPath='#%s.form' % bcId, #form parameter
                              **params)
                              
        bc.dataRpc('.data.tree', self.ht_pk_getTreeData, table=table,
                   rootpath=rootpath, rootcaption=tblobj.name_plural,
                   input_pkeys=input_pkeys, input_codes=input_codes,
                   relation_path=relation_path, related_table=related_table,
                   limit_rec_type=limit_rec_type,
                   nodeId='%s_loader' % nodeId,
                   _onResult="""FIRE .reload_tree;
                                     FIRE .prepare_check_status;
                                     if(kwargs._grid_show){
                                        if ($2.input_pkeys){
                                            SET .preview_grid.initial_checked_pkeys = $2.input_pkeys.split(',');
                                        }
                                        FIRE .preview_grid.load;
                                     }
                                     FIRE .loaded;""", _grid_show=grid_show)
                                     
        bc.dataController("""   PUBLISH %s_confirmed; 
                                FIRE .saved;""" % nodeId,
                          nodeId="%s_saver" % nodeId)
                          
        bc.dataController("""
                            FIRE .prepare_check_status;
                            FIRE .preview_grid.load;
                            """,
                          **{'subscribe_%s_tree_checked' % nodeId: True})
                          
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
                          _fired="^.prepare_check_status", output_codes=output_codes or False,
                          output_pkeys=output_pkeys or False,
                          treedata='=.data.tree')
    @public_method                  
    def ht_pk_getTreeData(self, table=None, rootpath=None, limit_rec_type=None, rootcaption=None,
                              input_codes=None, input_pkeys=None, related_table=None,
                              relation_path=None):
        result = self.ht_treeDataStore(table=table, rootpath=rootpath, limit_rec_type=limit_rec_type,
                                       rootcaption=rootcaption)
        htableobj = self.db.table(table)
        if related_table:
            if input_pkeys:
                input_pkeys = input_pkeys.split(',')
                reltableobj = self.db.table(related_table)
                where = '$%s IN :pkeys' % reltableobj.pkey
                q = reltableobj.query(columns='%s AS hcode' % relation_path, where=where,
                                      pkeys=input_pkeys, distinct=True, addPkeyColumn=False)
                input_codes = q.fetch()
                input_codes = [r['hcode'] for r in input_codes]
                
        if input_codes:
            if isinstance(input_codes, basestring):
                input_codes = input_codes.split(',')
            for code in input_codes:
                node = result.getNode('#0.%s' % code)
                if node and not node.attr['child_count'] > 0:
                    node.setAttr(checked=True)
            self._ht_pk_setParentStatus(result)
        return result
            
    def _ht_pk_setParentStatus(self, bag):
        for node in bag.nodes:
            value = node.getValue('static')
            if isinstance(value, Bag):
                self._ht_pk_setParentStatus(value)
                checked_elements = value.digest('#a.checked')
                n_checked = checked_elements.count(True)
                n_fuzzy = checked_elements.count(-1)
                if n_checked == len(value):
                    checked = True
                elif n_checked == 0 and n_fuzzy == 0:
                    checked = False
                else:
                    checked = -1
                node.attr['checked'] = checked
                
    def ht_pk_center(self, parentBC, table=None, formId=None, datapath=None,
                     controllerPath=None, region=None, caption=None, grid_struct=None, grid_columns=None,
                     grid_applymethod=None,
                     related_table=None, grid_where=None, condition_pars=None, output_codes=None,
                     output_related_pkeys=None, grid_show=None,
                     output_pkeys=None, grid_filter=None, default_checked_row=None, **kwargs):
        if grid_show:
            bc = parentBC.borderContainer(_class='pbl_roundedGroup', region=region)
            treepane = bc.contentPane(region='left', width='150px', splitter=True,
                                      datapath=datapath, formId=formId, controllerPath=controllerPath)
            self._ht_pk_view(bc.borderContainer(region='center'),
                             caption=caption, gridId='%s_grid' % formId,
                             table=table, related_table=related_table,
                             grid_where=grid_where, condition_pars=condition_pars,
                             output_related_pkeys=output_related_pkeys,
                             output_pkeys=output_pkeys, grid_struct=grid_struct, grid_applymethod=grid_applymethod,
                             grid_columns=grid_columns, grid_filter=grid_filter,
                             default_checked_row=default_checked_row)
        else:
            treepane = parentBC.contentPane(region=region, datapath=datapath, formId=formId,
                                            controllerPath=controllerPath)
        self._ht_pk_tree(treepane, caption=caption, formId=formId)
            
    def _ht_pk_tree(self, pane, caption=None, formId=None, *kwargs):
        pane.tree(storepath='.tree._root_', font_size='.9em',
                  isTree=False, hideValues=True,
                  _fired='^.#parent.reload_tree',
                  nodeId='%s_tree' % formId, eagerCheck=True,
                  inspect='shift', labelAttribute='caption', onChecked=True)
                  
    def _ht_pk_view(self, bc, caption=None, gridId=None, table=None, grid_columns=None,
                    grid_applymethod=None,
                    grid_struct=None, grid_where=None, condition_pars=None, related_table=None,
                    output_related_pkeys=None, grid_filter=None, default_checked_row=None, **kwargs):
        label = False
        hasToolbar = None
        if grid_filter:
            label = ' '
            hasToolbar = True
        default_checked_row = False if default_checked_row is False else True
        self.includedViewBox(bc, label=label, datapath='.preview_grid',
                             nodeId=gridId, columns=grid_columns,
                             table=related_table or table, filterOn=grid_filter,
                             struct=grid_struct, hasToolbar=hasToolbar,
                             reloader='^.load', addCheckBoxColumn=bool(related_table),
                             selectionPars=dict(where=grid_where,
                                                codes='=.#parent.data.checked_codes',
                                                _delay=1000,
                                                _onResult="""
                                                    var bag =result.getValue();
                                                    var initial_pkeys = GET .initial_checked_pkeys;
                                                    var default_check = kwargs.checked_row_default;
                                                    var cb_initial = function(n){
                                                        var check = dojo.indexOf(initial_pkeys,n.attr._pkey)>=0?true:default_check;
                                                        n.setAttribute('_checked',check);
                                                    };
                                                    var cb = function(n){
                                                        var old_n = old.getNodeByAttr('_pkey',n.attr._pkey);
                                                        n.setAttribute('_checked',(old_n && old_n.attr._checked==false)?false:default_check);
                                                    }
                                                    bag.forEach(initial_pkeys?cb_initial:cb,'static');   
                                                    SET .initial_checked_pkeys = null;
                                                    FIRE .#parent.set_output_pkeys;
                                                """, checked_row_default=default_checked_row,
                                                applymethod=grid_applymethod, **condition_pars),
                             )
                             
        bc.dataController("""
                            var l = [];
                            selection.forEach(function(n){
                                if(n.attr._checked){
                                    l.push(n.attr._pkey);
                                }
                            },'static');
                            this.setRelativeData(output_related_pkeys,l.join(','));
                            """, _fired="^.set_output_pkeys", selection='=.preview_grid.selection',
                          output_related_pkeys=output_related_pkeys, _if='output_related_pkeys',
                          **{'subscribe_%s_row_checked' % gridId: True})
                          