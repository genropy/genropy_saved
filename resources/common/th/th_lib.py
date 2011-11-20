# -*- coding: UTF-8 -*-

# th_lib.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrclasses import GnrMixinError

class TableHandlerCommon(BaseComponent):
    
    def _th_relationExpand(self,pane,relation=None,condition=None,condition_kwargs=None,default_kwargs=None,original_kwargs=None):
        maintable=original_kwargs.get('maintable') or pane.getInheritedAttributes().get('table') or self.maintable
        if default_kwargs is None:
            default_kwargs = dict()
        #relation_attr = self.db.table(maintable).model.getRelation(relation)
        relation_attr = self.db.table(maintable).model.relations.getAttr(relation, 'joiner')
        many = relation_attr['many_relation'].split('.')
        if (relation_attr.get('onDelete')=='setnull') or (relation_attr.get('onDelete_sql')=='setnull'):
            original_kwargs['store_unlinkdict'] = dict(one_name = relation_attr.get('one_rel_name'),field=relation_attr['many_relation'].split('.')[-1])
        fkey = many.pop()
        table = str('.'.join(many))
        fkey = str(fkey)
        condition_kwargs['fkey'] = '=#FORM.pkey'
        condition_kwargs['_loader'] = '^#FORM.controller.loaded'
        basecondition = '$%s=:fkey' %fkey       
        condition = basecondition if not condition else '(%s) AND (%s)' %(basecondition,condition)  
        default_kwargs[fkey] = '=#FORM/parent/#FORM.pkey'
        return table,condition 
        
    def _th_getResourceName(self,name=None,defaultModule=None,defaultClass=None):
        if not name:
            return '%s:%s' %(defaultModule,defaultClass)
        if not ':' in name:
            return '%s:%s' %(name,defaultClass)
        if name.startswith(':'):
            return '%s%s' %(defaultModule,name)
        return name
        
    def _th_mixinResource(self,rootCode=None,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        try:
            self.mixinComponent('tables','_packages',pkg,tablename,resourceName,pkg=self.package.name,mangling_th=rootCode, pkgOnly=True)
        except GnrMixinError:
            tableObj = self.db.table(table)
            pluginId = getattr(tableObj, '_pluginId', None)
            self.mixinComponent('tables',tablename,resourceName,pkg=pkg,mangling_th=rootCode, pluginId=pluginId, pkgOnly=True)
        return resourceName
            
    
    def _th_getResClass(self,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        return self.importTableResource(table,resourceName)
        
            
    def _th_hook(self,method,mangler=None,asDict=False,dflt=None):
        if isinstance(mangler,Bag):
            mangler = mangler.getInheritedAttributes().get('th_root')
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
        return getattr(self,'%s_%s' %(mangler.replace('.','_'),method),emptyCb) 
        



