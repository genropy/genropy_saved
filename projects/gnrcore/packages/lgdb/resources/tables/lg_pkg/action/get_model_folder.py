# -*- coding: utf-8 -*-

from collections import OrderedDict
from gnr.core.gnrstring import flatten
from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag

START_SOURCE = """# encoding: utf-8

class Table(object):
""" 

topic = 'form_batch'
description = 'Model folder from package'

class Main(BaseResourceAction):
    batch_prefix = 'model_folder'
    batch_title = 'Model folder from package'

    def pre_process(self):
        pkg = self.get_selection_pkeys()[0]
        self.resultNode= self.page.site.storageNode('page:{}'.format(pkg))
        self.zipNode= self.page.site.storageNode('page:{}.zip'.format(pkg))
        self.columns_records = self.db.table('lgdb.lg_column'
                                ).query(where='@lg_table_id.lg_pkg=:pkg',pkg=pkg).fetchGrouped('lg_table_id')
        self.tables_records = self.db.table('lgdb.lg_table').query(where='$id IN :pkeys',pkeys=list(self.columns_records.keys())).fetch()

        self.relations_records = self.db.table('lgdb.lg_relation'
                                ).query(where='@relation_column.@lg_table_id.lg_pkg=:pkg',pkg=pkg).fetchGrouped('relation_column')
    
    def do(self):
        for tbl in self.btc.thermo_wrapper(self.tables_records, 
                                        message=lambda item, progress, maximum: item['name']):
            self.makeTableModel(tbl)

    def makeTableModel(self,tbl):
        table_data = self.makeTableModelBag(tbl)
        self.makeOneTable(table_data)

    def makeTableModelBag(self,tbl):
        table_data = Bag()
        table_data['name'] = tbl['name'].lower().replace(' ','_').replace('.','_')
        table_data['legacy_name'] = tbl['sqlname']
        table_data['name_long'] = tbl['description']
        table_data['sqlname'] = tbl['sqlname']
        table_data['legacy_db'] = tbl['legacy_db']
        pkey = tbl['primary_key']
        if pkey:
            pkey = pkey.lower()
        table_data['pkey'] = pkey or None
        columns_bag = Bag()
        table_data['_columns'] = columns_bag
        caption_field = None
        for colrec in self.columns_records[tbl['id']]:
            legacy_name = colrec['name']
            if legacy_name=='_multikey':
                legacy_name = None
            colname = colrec['name'].lower()
            dtype=colrec.get('data_type')
            if not caption_field and dtype in ('A','T','C') and colname!=pkey:
                caption_field = colname
            b = Bag(dict(name=colname,legacy_name=legacy_name,sqlname=legacy_name,
                                                name_long=colrec.get('description'),dtype=dtype,
                                                size=str(colrec.get('size')) if colrec.get('size') else None,
                                                indexed=colrec.get('indexed'),
                                                unique=colrec.get('unique')))
            columns_bag.setItem(colname,b)
            for relation in self.relations_records.get(colrec['full_name'],[]):
                b.setItem('_relation',Bag(dict(relation=relation['related_column'],onDelete='raise')))
        table_data['caption_field'] = caption_field
        return table_data


    def makeOneTable(self,table_data=None):
        l = [START_SOURCE]
        table = table_data.pop('name')
        sn = self.resultNode.child('{}.py'.format(table))
        table_data['name_long'] = table_data['name_long'] or table
        table_data['name_plural'] = table_data['name_plural'] or table
        table_data['caption_field'] = table_data['caption_field'] or table_data['pkey']
        columns = table_data.pop('_columns') or Bag()
        l.append(
            """    def config_db(self,pkg):\n        tbl =  pkg.table('%s'%s)""" %(table,self.bagToArgString(table_data))
        )
        for col in columns.values():
            relation = col.pop('_relation')
            s = self._columnPythonCode(col,relation)
            l.append('\n        {}'.format(s))
        with sn.open('w') as f:
            f.write(''.join(l))

    def _columnPythonCode(self,c,relation=None):
        attributes = Bag()
        col = c.deepcopy()
        name = flatten(col.pop('name'))
        dtype = col.pop('dtype')
        size = col.pop('size')
        name_long = col.pop('name_long')
        name_short = col.pop('name_short')
        tag = col.pop('tag') #column,formulaColumn,aliasColumn,pyColumn
        if dtype and dtype not in ('A','T','C'):
            attributes['dtype'] = dtype
        if size:
            attributes['size'] = size
        attributes.setItem('name_long', name_long or name,localized=True)
        if name_short:
            attributes.setItem('name_short', name_short,localized=True)
        attributes.update(col)
        relationCode = ''
        if relation and relation['relation']:
            relationCode = '.%s' %self._relationPythonCode(relation)
        coltype = 'column'
        if attributes['sql_formula'] or attributes['select'] or attributes['exists']:
            coltype = 'formulaColumn'
        elif attributes['relation_path']:
            coltype = 'aliasColumn'
        elif attributes['pymethod']:
            coltype = 'pyColumn'
        return "tbl.%s('%s'%s)%s" % (coltype,name, self.bagToArgString(attributes),relationCode)

    def bagToArgString(self,arguments,prefix=','):
        if not arguments:
            return ''
        atlst = []
        for k,v in arguments.items():
            if v in ('',None):
                continue
            if isinstance(v,str):
                v = ("'%s'" if not "'" in v else 'u"%s"') %v
            elif isinstance(v, Bag):
                v = "dict(%s)" %self.bagToArgString(v,prefix='')
            atlst.append("%s=%s" %(k,v))
        return '%s%s' %(prefix,','.join(atlst))

    def _relationPythonCode(self,relation):
        relpath = relation.pop('relation')
        r = relpath.split('.')
        if len(r)==3:
            pkg,table,id = r
            if pkg == 'main':
                relpath = '%s.%s' %(table,id)
        relation_name = relation.pop('relation_name')
        foreignkey = relation.pop('foreignkey')
        attributes = Bag()
        if relation_name:
            attributes['relation_name'] = relation_name
        if foreignkey:
            attributes['mode'] = 'foreignkey'
        for k, v in relation.items():
            if v is not None:
                attributes[k] = v
        atlst = []
        for k,v in attributes.items():
            if v == 'True':
                v = True
            if isinstance(v,basestring):
                if "'" in v:
                    v = '"%s"' %v
                else:
                    v = "'%s'" %v
            atlst.append("%s=%s" %(k,v))
        return """relation('%s',%s)"""  %(relpath,', '.join(atlst))




    def post_process(self):
        self.page.site.zipFiles([self.resultNode.internal_path], self.zipNode.internal_path)
        self.result_url = self.page.site.getStaticUrl(self.zipNode.fullpath)

    def result_handler(self):
        resultAttr = dict()
        resultAttr['url'] = self.result_url
        return 'Model done', resultAttr