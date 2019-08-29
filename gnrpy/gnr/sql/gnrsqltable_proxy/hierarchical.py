# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package            : GenroPy sql - see LICENSE for details
# module gnrsqlmodel : an advanced data storage system
# Copyright (c)      : 2004 - 2007 Softwell sas - Milano 
# Written by         : Giovanni Porcari,Michele Bertoldi, 
#                      Saverio Porcari, Francesco Porcari,Francesco Cavazzana
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

from builtins import str
#from builtins import object
from gnr.core.gnrstring import encode36
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import extract_kwargs

class TableHandlerTreeResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'table':None,
                   'parent_id': None,
                   'root_id':None,
                   'caption_field':None,
                   'alt_pkey_field':None,
                   'condition':None,
                   'condition_kwargs':None,
                   '_condition_id':None,
                   'dbstore':None,
                   'columns':None,
                   'related_kwargs':None,
                   '_isleaf':None,
                   'readOnly':False,
                   '_page':None}
    classArgs = ['table','parent_id']

    @property
    def relatedCaptionField(self):
        db = self._page.db
        related_tblobj = db.table(self.related_kwargs['table'])
        return self.related_kwargs.get('caption_field') or related_tblobj.attributes.get('caption_field')

    @property
    def db(self):
        return self._page.db

    def load(self):
        result = Bag()
        if self.related_kwargs:
            for related_row in self.getRelatedChildren(self.parent_id):
                r = dict(related_row)
                pkey = r.pop('pkey',None)
                result.setItem(pkey, None,
                                child_count=0,
                                 caption=r[self.relatedCaptionField],
                                 pkey=pkey, treeIdentifier='%s_%s'%(self.parent_id, pkey),
                                 node_class='tree_related',**r)
        if not self._isleaf:
            children = self.getChildren(self.parent_id)
            if len(children):
                self.setChildren(result,children)
        return result

    def getRelatedChildren(self,parent_id=None):
        related_tblobj = self.db.table(self.related_kwargs['table'])
        result = []
        if parent_id:
            related_kwargs = dict(self.related_kwargs)
            includeAlias = related_kwargs.pop('includeAlias', None)
            caption_field = self.relatedCaptionField
            columns = self.related_kwargs.get('columns') or '*,$%s' %caption_field
            relation_path = self.related_kwargs['path']
            condition = self.related_kwargs.get('condition')
            condition_kwargs = dictExtract(related_kwargs,'condition_')
            where = ' (%s=:pkey) ' % relation_path
            if includeAlias:
                tblobj = self.db.table(self.table)
                aliasTableName = '%s_alias' %tblobj.fullname
                aliasJoiner = related_tblobj.model.getJoiner(aliasTableName)
                aliasRelationName = aliasJoiner['relation_name']
                mainJoiner = tblobj.model.getJoiner(aliasTableName)
                aliasFkey = mainJoiner.get('many_relation','').split('.')[-1]
                where = "(%s) OR @%s.%s=:pkey"%(where, aliasRelationName, aliasFkey)
            
            if condition:
                where = '(%s) AND %s'%(where,condition)
            result = related_tblobj.query(where=where,columns=columns, _storename=self.dbstore,
                                            pkey=parent_id,**condition_kwargs).fetch()
        return result

    def getChildren(self,parent_id):
        tblobj = self.db.table(self.table)
        where = '$parent_id IS NULL'
        if self.root_id:
            where = '$id=:r_id'
        elif parent_id:
            where='$parent_id=:p_id'
        caption_field = self.caption_field
        if not caption_field:
            if tblobj.attributes.get('hierarchical_caption_field'):
                caption_field = tblobj.attributes['hierarchical_caption_field']
            elif tblobj.attributes['hierarchical'] != 'pkey':
                caption_field = tblobj.attributes['hierarchical'].split(',')[0]
            else:
                caption_field = tblobj.attributes.get('caption_field')
            self.caption_field = caption_field
        condition_kwargs = self.condition_kwargs or dict()
        for k,v in list(condition_kwargs.items()):
            condition_kwargs.pop(k)
            condition_kwargs[str(k)] = v
        condition_pkeys = None
        if self.condition:
            condition_pkeys = self.getConditionPkeys()
            where = ' ( %s ) AND ( $id IN :condition_pkeys ) ' %where
        order_by = tblobj.attributes.get('order_by') or '$%s' %caption_field
        columns = self.columns or '*'
        q = tblobj.query(where=where,p_id=parent_id,r_id=self.root_id,columns='%s,$child_count,$%s' %(columns,caption_field),
                         condition_pkeys=condition_pkeys,
                         order_by=order_by,_storename=self.dbstore,**condition_kwargs)
        return q.fetch()

    def setChildren(self,result,children):
        pkeyfield = self.db.table(self.table).pkey
        for r in children:
            record = dict(r)
            caption = r[self.caption_field]
            pkey = record[pkeyfield]
            child_count=record['child_count']
            value = None
            if child_count:
                value = TableHandlerTreeResolver(_page=self._page,table=self.table,
                                            parent_id=pkey,caption_field=self.caption_field,
                                            alt_pkey_field=self.alt_pkey_field,
                                            dbstore=self.dbstore,
                                            condition=self.condition,
                                            related_kwargs=self.related_kwargs,
                                            _condition_id=self._condition_id,columns=self.columns)
            elif self.related_kwargs:
                related_children = self.getRelatedChildren(pkey)
                if related_children:
                    value = TableHandlerTreeResolver(_page=self._page,table=self.table,parent_id=pkey,caption_field=self.caption_field,
                                            dbstore=self.dbstore,condition=self.condition,related_kwargs=self.related_kwargs,
                                            _condition_id=self._condition_id,columns=self.columns,_isleaf=True)
                    child_count = len(related_children)
                elif not self.related_kwargs.get('_allowEmptyFolders'):
                    continue
            result.setItem(pkey,value,
                            **self.applyOnTreeNodeAttr(caption=caption,
                                    child_count=child_count,pkey=record.get(self.alt_pkey_field) if self.alt_pkey_field else (pkey or '_all_'),
                                    parent_id=self.parent_id,
                                    hierarchical_pkey=record['hierarchical_pkey'],
                                    treeIdentifier=pkey,_record=record))
        return result

    def applyOnTreeNodeAttr(self,**kwargs):
        result = dict(kwargs)
        tblobj = self.db.table(self.table)
        if hasattr(tblobj,'applyOnTreeNodeAttr'):
            result.update(tblobj.applyOnTreeNodeAttr(**kwargs) or dict())
        return result

    def resolverSerialize(self):
        attr = super(TableHandlerTreeResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    def getConditionPkeys(self):
        if self._condition_id:
            condition_pkeys = self._page.pageStore().getItem('hresolver.%s' %self._condition_id)
        else:
            self._condition_id = self._page.getUuid()
            db = self._page.db
            tblobj = db.table(self.table)
            condition_kwargs = self.condition_kwargs or dict()
            valid = tblobj.query(where='$child_count=0 AND ( %s )' %self.condition,columns='$hierarchical_pkey',
                                 _storename=self.dbstore,addPkeyColumn=False,**condition_kwargs).fetch()
            condition_pkeys = set()
            for r in valid:
                for pk in r['hierarchical_pkey'].split('/'):
                    condition_pkeys.add(pk)
            condition_pkeys = list(condition_pkeys)
            with self._page.pageStore() as store:
                store.setItem('hresolver.%s' %self._condition_id,condition_pkeys)
        return condition_pkeys


class HierarchicalHandler(object):
    """docstring for HierarchicalHandler"""
    def __init__(self, tblobj):
        self.tblobj = tblobj
        self.db = self.tblobj.db


    def hierarchicalSearch(self,seed=None,related_table=None,related_path=None,related_caption_field=None,**kwargs):
        """return hierarchical paths for a given search seed"""
        if related_table:
            related_tblobj = self.db.table(related_table)
            caption_field = related_caption_field or related_tblobj.attributes['caption_field']
            f = related_tblobj.query(where="$%s ILIKE :seed" %caption_field,addPkeyColumn=False,
                                seed='%%%s%%' %seed,columns="""@%s.hierarchical_pkey AS hrelpk""" %related_path,
                                ).fetch()
        else:
            caption_field = self.tblobj.attributes.get('hierarchical_caption_field') or self.tblobj.attributes['caption_field']
            f = self.tblobj.query(where="$%s ILIKE :seed" %caption_field,seed='%%%s%%' %seed,columns="""$hierarchical_pkey AS hrelpk""",
                            addPkeyColumn=False).fetch()
        result = set()
        for r in f:
            result = result.union(r['hrelpk'].split('/'))
        return list(result)



    def trigger_before(self,record,old_record=None):
        tblobj = self.tblobj
        pkeyfield = tblobj.pkey
        parent_id=record.get('parent_id')
        parent_record = None
        if parent_id:
            parent_record = tblobj.query(where='$%s=:pid' %pkeyfield,pid=parent_id).fetch()
            parent_record = parent_record[0] if parent_record else None
        for fld in tblobj.attributes.get('hierarchical').split(','):
            parent_h_fld='_parent_h_%s'%fld
            h_fld='hierarchical_%s'%fld
            v=record.get(pkeyfield if fld=='pkey' else fld) 
            record[parent_h_fld]= parent_record[h_fld] if parent_record else None
            record[h_fld]= '%s/%s'%( parent_record[h_fld], v) if parent_record else v
        if parent_record:
            for field,colobj in tblobj.columns.items():
                if colobj.attributes.get('copyFromParent'):
                    record[field] = parent_record[field]
        if tblobj.column('_row_count') is None:
            return 
        record['_parent_h_count'] = parent_record['_h_count'] if parent_record else None
        if old_record is None and record.get('_row_count') is None:
            #has counter and inserting a new record without '_row_count'
            where = '$parent_id IS NULL' if not record.get('parent_id') else '$parent_id =:p_id' 
            last_counter = tblobj.readColumns(columns='$_row_count',where=where,
                                        order_by='$_row_count desc',limit=1,p_id=parent_id)
            record['_row_count'] = (last_counter or 0)+1
        if old_record is None or tblobj.fieldsChanged('_row_count,_parent_h_count',record,old_record):
            record['_h_count'] = '%s%s' %(record.get('_parent_h_count') or '',encode36(record['_row_count'],2))
        


    def trigger_after(self,record,old_record=None,**kwargs):
        tblobj = self.tblobj
        hfields = tblobj.attributes.get('hierarchical').split(',')
        changed_hfields=[fld for fld in hfields if record.get('hierarchical_%s'%fld) != old_record.get('hierarchical_%s'%fld)]
        order_by = None
        changed_counter = False
        if '_row_count' in record:
            order_by = '$_row_count'
            changed_counter = (record['_row_count'] != old_record['_row_count']) or (record['_parent_h_count'] != old_record['_parent_h_count'])
        if changed_hfields or changed_counter:
            fetch = tblobj.query(where='$parent_id=:curr_id',addPkeyColumn=False, for_update=True,curr_id=record[tblobj.pkey],order_by=order_by,
                                    bagFields=True).fetch()
            for k,row in enumerate(fetch):
                new_row = dict(row)
                for fld in changed_hfields:
                    new_row['_parent_h_%s'%fld]=record['hierarchical_%s'%fld]
                if changed_counter:
                    if new_row.get('_row_count') is None:
                        new_row['_row_count'] = k+1
                    new_row['_parent_h_count'] = record['_h_count']
                    new_row['_h_count'] = '%s%s' %(new_row['_parent_h_count'] or '',encode36(new_row['_row_count'],2))
                tblobj.update(new_row, row)

    @extract_kwargs(condition=True,related=True)
    def getHierarchicalData(self,caption_field=None,condition=None,
                            condition_kwargs=None,caption=None,
                            dbstore=None,columns=None,related_kwargs=None,
                            resolved=False,parent_id=None,root_id=None,alt_pkey_field=None,**kwargs):
        b = Bag()
        caption = caption or self.tblobj.name_plural
        condition_kwargs = condition_kwargs or dict()
        condition_kwargs.update(dictExtract(kwargs,'condition_'))
        related_kwargs = related_kwargs or {}
        v = TableHandlerTreeResolver(_page=self.tblobj.db.currentPage,
                                        table=self.tblobj.fullname,caption_field=caption_field,condition=condition,dbstore=dbstore,columns=columns,related_kwargs=related_kwargs,
                                                condition_kwargs=condition_kwargs,root_id=root_id,parent_id=parent_id,alt_pkey_field=alt_pkey_field)
        b.setItem('root',v,caption=caption,child_count=1,pkey='',treeIdentifier='_root_',table=self.tblobj.fullname,
                    search_method=self.tblobj.hierarchicalSearch,search_related_table=related_kwargs.get('table'),
                    search_related_path=related_kwargs.get('path'),search_related_caption_field=related_kwargs.get('caption_field'))
        if resolved:
            def cb(self,*args,**kwargs):
                pass
            b.walk(cb,_mode='')
        return b

    def pathFromPkey(self,pkey=None,related_kwargs=None,dbstore=None):
        hierarchical_pkey =  self.tblobj.readColumns(columns='$hierarchical_pkey',pkey=pkey,_storename=dbstore)
        path = hierarchical_pkey.replace('/','.') if hierarchical_pkey else 'root'
        return path

    def getHierarchicalPathsFromPkeys(self,pkeys=None,related_kwargs=None,parent_id=None,dbstore=None,alt_pkey_field=None,**kwargs):
        if not pkeys:
            return 
        pkeys = pkeys.split(',')
        pkey_field = alt_pkey_field or self.tblobj.pkey
        if not related_kwargs:
            f = self.tblobj.query(where='$%s IN :pk' %pkey_field,pk=pkeys,columns='$hierarchical_pkey AS _hpath',_storename=dbstore).fetch()
        else:
            related_table = self.db.table(related_kwargs['table'])
            relpkey =related_table.pkey
            f = related_table.query(where='$%s IN :pk' %pkey_field,pk=pkeys,addPkeyColumn=True,
                    columns='@%s.hierarchical_pkey AS _hpath,$%s' %(related_kwargs['path'],relpkey) ,
                    _storename=dbstore).fetch()
            f = [dict(_hpath='%s/%s' %(r['_hpath'],r[relpkey]) ) for r in f]
        if parent_id:
            return ','.join([r['_hpath'].split(parent_id,1)[1][1:].replace('/','.') for r in f if r['_hpath']])
        else:
            return ','.join([r['_hpath'].replace('/','.') for r in f if r['_hpath']])


    def getAncestors(self,pkey=None,hierarchical_pkey=None,meToo=True,columns=None,order_by=None,**kwargs):
        if not hierarchical_pkey:
            hierarchical_pkey = self.tblobj.readColumns(columns='$hierarchical_pkey' ,pkey=pkey)
        p = hierarchical_pkey
        where = ['( :p ILIKE $hierarchical_pkey || :suffix)']
        if meToo:
            where.append('( :p = $hierarchical_pkey )')
        where =  ' OR '.join(where)
        order_by= order_by or '$hlevel'
        return self.tblobj.query(where=where,p=p,suffix='/%%',order_by=order_by,columns=columns,**kwargs).fetch()

