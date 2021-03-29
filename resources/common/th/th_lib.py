# -*- coding: utf-8 -*-

# th_lib.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

from builtins import str
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
import os

class TableHandlerCommon(BaseComponent):
    def onLoadingRelatedMethod(self,table,sqlContextName=None):
        return 'onLoading_%s' % table.replace('.', '_')
    
    def _th_mangler(self,pane,table,nodeId=None):
        tableCode = table.replace('.','_')
        if nodeId and nodeId.endswith('#'):
            nodeId = nodeId.replace('#',str(id(pane)))
        th_root = nodeId or tableCode #'%s_%i' %(tableCode,id(pane.parentNode))
        return th_root
        
    def _th_relationExpand(self,pane,relation=None,condition=None,
                        condition_kwargs=None,default_kwargs=None,relation_kwargs=None,original_kwargs=None):
        inheritedAttributes = pane.getInheritedAttributes()
        relation_kwargs = relation_kwargs or dict()
        if inheritedAttributes.get('_lazyBuild'):
            condition_kwargs['_onBuilt']=True
        maintable=original_kwargs.get('maintable') or inheritedAttributes.get('table') or self.maintable
        if default_kwargs is None:
            default_kwargs = dict()
        tblrel = self.db.table(maintable)
        relation_attr = tblrel.model.relations.getAttr(relation, 'joiner')
        if not relation_attr:
            raise Exception('Missing relation {}'.format(relation))
        if relation_attr.get('inheritLock') is not None and 'inheritLock' not in original_kwargs:
            original_kwargs['inheritLock'] = relation_attr['inheritLock']
        if relation_attr.get('inheritProtect') is not None and 'inheritProtect' not in original_kwargs:
            original_kwargs['inheritProtect'] = relation_attr['inheritProtect']

        relationKey = relation_attr['one_relation'].split('.')[2]
        condition_kwargs['_loader'] = '^#FORM.controller.loaded'
        condition_kwargs['_if'] = 'fkey && fkey!="*newrecord*" && fkey!="*norecord*"'
        relcondition,table,fkeyfield = self._th_relationExpand_one(tblrel,relation_attr,condition=condition,original_kwargs=original_kwargs,condition_kwargs=condition_kwargs,default_kwargs=default_kwargs)
        _foreignKeyFormPath = original_kwargs.get('_foreignKeyFormPath','=#FORM/parent/#FORM')
        
        if tblrel.pkey!=relationKey:
            #relation is not on primary key
            default_kwargs[fkeyfield] = '%s.record.%s' %(_foreignKeyFormPath, relationKey)
            condition_kwargs['fkey'] = '=#FORM.record.%s' %relationKey
        else:
            default_kwargs[fkeyfield] = '%s.pkey' %_foreignKeyFormPath
            condition_kwargs['fkey'] = '=#FORM.pkey'
        if (relation_attr.get('onDelete')=='setnull') or (relation_attr.get('onDelete_sql')=='setnull'):
            original_kwargs['store_unlinkdict'] = dict(one_name = relation_attr.get('one_rel_name',tblrel.name_plural),field=relation_attr['many_relation'].split('.')[-1])
        elif (relation_attr.get('onDelete')=='cascade'):
            original_kwargs['store_excludeDraft'] = False
            original_kwargs['store_excludeLogicalDeleted'] = False
        for suffix,altrelation in relation_kwargs.items():
            alt_relation_attr = tblrel.model.relations.getAttr(altrelation, 'joiner')
            altcond,table,altfkey = self._th_relationExpand_one(tblrel,alt_relation_attr,condition=condition,condition_kwargs=condition_kwargs,suffix=suffix)
            relcondition = '%s OR %s' %(relcondition,altcond)
        condition = relcondition if not condition else '(%s) AND (%s)' %(relcondition,condition)  
        return table,condition,fkeyfield

    def _th_relationExpand_one(self,tblrel,relation_attr,suffix=None,condition=None,original_kwargs=None,condition_kwargs=None,default_kwargs=None):
        many = relation_attr['many_relation'].split('.')
        fkey = many.pop()
        table = str('.'.join(many))
        fkey = str(fkey)
        condition_kwargs['_fkey_name_%s' %suffix if suffix else '_fkey_name'] = fkey
        relcondition = '$%s=:fkey' %fkey                   
        return relcondition,table,fkey
        
    def _th_getResourceName(self,name=None,defaultModule=None,defaultClass=None):
        if not name:
            return '%s:%s' %(defaultModule,defaultClass)
        if ':' not in name:
            return '%s:%s' %(defaultModule,name)
        if name.startswith(':'):
            return '%s%s' %(defaultModule,name)
        return name
        

    def mixinExternalTHResource(self,table=None,resourceName=None,defaultClass=None,rootCode=None):
        rootCode = rootCode or table.replace('.','_')
        self._th_mixinResource(rootCode=rootCode,table=table,resourceName=resourceName)

    def _th_mixinResource(self,rootCode=None,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourcePath = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        tableObj = self.db.table(table)
        pluginId = getattr(tableObj, '_pluginId', None)
        self.mixinComponent(resourcePath,mangling_th=rootCode,safeMode=True)
        self.mixinComponent('tables',tablename,resourcePath,pkg=pkg,mangling_th=rootCode, pluginId=pluginId, pkgOnly=True,safeMode=True)
        project_mainpackage = self.package.attributes.get('mainpkg')
        if project_mainpackage:
            self.mixinComponent('tables','_packages',pkg,tablename,resourcePath,pkg=project_mainpackage,mangling_th=rootCode, pkgOnly=True,safeMode=True)
        
        enabled_packages = self._call_kwargs.get('enabled_packages','*')
        if enabled_packages=='*':
            enabled_packages = list(self.application.packages.keys()) 
        else:
            enabled_packages = enabled_packages.split(',')
        for refpkg in enabled_packages:
            if refpkg!=self.package.name:
                self.mixinComponent('tables','_packages',pkg,tablename,resourcePath,pkg=refpkg,mangling_th=rootCode, pkgOnly=True,safeMode=True)
        self.mixinComponent('tables','_packages',pkg,tablename,resourcePath,pkg=self.package.name,mangling_th=rootCode, pkgOnly=True,safeMode=True)
        return
    
    def _th_getResClass(self,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        return self.importTableResource(table,resourceName)
            
    def _th_hook(self,method,mangler=None,asDict=False,dflt=None,defaultCb=None):
        if isinstance(mangler,Bag):
            inattr = mangler.getInheritedAttributes()
            mangler = inattr.get('th_root') or inattr.get('frameCode') or inattr.get('nodeId')
        return self.mangledHook(method,mangler=mangler,asDict=asDict,dflt=dflt,defaultCb=defaultCb)

    @public_method
    def th_searchRelationPath(self,table=None,destTable=None,**kwargs):
        joiners = self.db.table(destTable).model.getTableJoinerPath(table)
        result = []
        values = []
        cbdict = dict()
        for j in joiners:
            caption_path = []
            relpath_list = []
            for r in j:
                relpath_list.append(r['relpath'])
                tblobj = self.db.table(r['table'])
                caption_path.append(self._(tblobj.name_plural if r['mode'] == 'M' else tblobj.name_long))
            if len(relpath_list)>1:
                relpath = '.'.join(relpath_list)
            else:
                relpath = relpath_list[0]
                if not relpath.startswith('@'):
                    relpath = '$%s' %relpath
            result.append(relpath)
            values.append('%s:%s' %(relpath,'/'.join(caption_path)))
            cbdict[relpath] = caption_path

        return dict(relpathlist=result,masterTableCaption=self._(self.db.table(table).name_long),cbvalues=','.join(values))



    def th_prepareQueryBag(self,querybase,table=None):
        result = Bag()
        if not querybase:
            return result
        table = table or self.maintable
        tblobj = self.db.table(table)
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        val = querybase.get('val')
        if column:
            column_dtype = tblobj.column(column).getAttr('query_dtype') or tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', val,
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': self.db.table(table).whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(table, column),
                        'value_caption':val})
        return result
    
    @public_method
    def th_multidbStoreQueryPicker(self,pane,**kwargs):
        frame = pane.bagGrid(storepath='.dbstores',title='!!Db Stores',pbl_classes=True,margin='2px',
                            datapath='#WORKSPACE.dbstorePicker',addrow=False,delrow=False,
                            struct=self.th_multidbStoreQueryPicker_struct)
        bar = frame.top.bar.replaceSlots('#','#,allstores,searchOn,5')
        bar.allstores.checkbox(value='^#WORKSPACE.queryOnAllStores',label='!!All stores')
        bar.dataFormula('#ANCHOR.multiStores',"queryOnAllStores?'*':(queryDbStores || null)",
                        queryOnAllStores='^#WORKSPACE.queryOnAllStores',
                        queryDbStores='^#WORKSPACE.queryDbStores')
        dbstorebag = Bag()
        dbstorebag.setItem(self.db.rootstore,None,dbstore='MAINSTORE',_pkey=self.db.rootstore)
        for dbstore in self.db.dbstores:
            dbstorebag.addItem(dbstore,None,dbstore=dbstore,_pkey=dbstore)
        frame.data('.dbstores',dbstorebag)
        
    def th_multidbStoreQueryPicker_struct(self,struct):
        r=struct.view().rows()
        r.checkboxcolumn(checkedId='#WORKSPACE.queryDbStores',name=' ',hidden='^#WORKSPACE.queryOnAllStores')
        r.cell('dbstore',width='20em',name='!!Store')