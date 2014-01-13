# -*- coding: UTF-8 -*-

# th_lib.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrclasses import GnrMixinError

class TableHandlerCommon(BaseComponent):
    
    def onLoadingRelatedMethod(self,table,sqlContextName=None):
        return 'onLoading_%s' % table.replace('.', '_')
    
    def _th_mangler(self,pane,table,nodeId=None):
        tableCode = table.replace('.','_')
        if nodeId and nodeId.endswith('#'):
            nodeId = nodeId.replace('#',str(id(pane)))
        th_root = nodeId or tableCode #'%s_%i' %(tableCode,id(pane.parentNode))
        return th_root
        
    def _th_relationExpand(self,pane,relation=None,condition=None,condition_kwargs=None,default_kwargs=None,original_kwargs=None):
        inheritedAttributes = pane.getInheritedAttributes()
        if inheritedAttributes.get('_lazyBuild'):
            condition_kwargs['_onBuilt']=True
        maintable=original_kwargs.get('maintable') or inheritedAttributes.get('table') or self.maintable
        if default_kwargs is None:
            default_kwargs = dict()
        #relation_attr = self.db.table(maintable).model.getRelation(relation)
        tblrel = self.db.table(maintable)
        relation_attr = tblrel.model.relations.getAttr(relation, 'joiner')
        many = relation_attr['many_relation'].split('.')
        if (relation_attr.get('onDelete')=='setnull') or (relation_attr.get('onDelete_sql')=='setnull'):
            original_kwargs['store_unlinkdict'] = dict(one_name = relation_attr.get('one_rel_name',tblrel.name_plural),field=relation_attr['many_relation'].split('.')[-1])
        fkey = many.pop()
        table = str('.'.join(many))
        fkey = str(fkey)
        condition_kwargs['_fkey_name'] = fkey
        condition_kwargs['fkey'] = '=#FORM.pkey'
        condition_kwargs['_loader'] = '^#FORM.controller.loaded'
        condition_kwargs['if'] = 'fkey && fkey!="*newrecord*" && fkey!="*norecord*"'
        basecondition = '$%s=:fkey' %fkey       
        condition = basecondition if not condition else '(%s) AND (%s)' %(basecondition,condition)  
        default_kwargs[fkey] = original_kwargs.get('foreignKeyGetter','=#FORM/parent/#FORM.pkey')
        return table,condition 
        
    def _th_getResourceName(self,name=None,defaultModule=None,defaultClass=None):
        if not name:
            return '%s:%s' %(defaultModule,defaultClass)
        if not ':' in name:
            return '%s:%s' %(defaultModule,name)
        if name.startswith(':'):
            return '%s%s' %(defaultModule,name)
        return name
        
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
            enabled_packages = self.application.packages.keys() 
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
            mangler = inattr.get('th_root') or inattr.get('frameCode')
        if hasattr(self,'legacy_dict'):
            method=self.legacy_dict.get(method,method)
        if asDict:
            prefix='%s_%s_'% (mangler,method)
            return dict([(fname,getattr(self,fname)) for fname in dir(self) 
                                     if fname.startswith(prefix) and fname != prefix])
        if hasattr(self,'legacy_dict'):
            return getattr(self,method)          
        def emptyCb(*args,**kwargs):
            return dflt
        handler = getattr(self,'%s_%s' %(mangler.replace('.','_'),method),None)
        if handler is None and defaultCb is False:
            return None
        return handler or defaultCb or emptyCb
        



