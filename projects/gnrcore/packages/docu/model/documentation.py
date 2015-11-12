#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import metadata
import os
import shutil
import textwrap

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('documentation', pkey='id', name_long='!!Documentation', 
                        name_plural='!!Documentation',caption_field='name')
        self.sysFields(tbl,hierarchical='name',df=True,
                        counter=True,user_ins=True,user_upd=True)
        tbl.column('name',name_long='!!Name')
        tbl.column('topics',name_long='!!Topics')
        tbl.column('publish_date',dtype='D',name_long='!!Publish date')
        tbl.column('sourcebag',dtype='X',name_long='Python Source',_sendback=True)
        tbl.column('docbag',dtype='X',name_long='Rst data',_sendback=True)
        tbl.column('doctype',name_long='!!Doc. type')
        tbl.column('old_html')
        tbl.formulaColumn('example_url',"'/webpages/docu_examples/'||$hierarchical_name")

    def trigger_onUpdating(self,record,old_record):
        record['sourcebag'] = record['sourcebag'] or None
        if record['sourcebag']:
            record['sourcebag'] = Bag(record['sourcebag'])
            for v in record['sourcebag'].values():
                v['url'] = '/webpages/docu_examples/%s/%s.py' %(record['hierarchical_name'],v['version'])

    def trigger_onUpdated(self,record,old_record):
        if record['hierarchical_name'] != old_record['hierarchical_name']:
            old_link = '</sys/docserver/rst/%s/%s>' %(self.fullname.replace('.','/'),old_record['hierarchical_name'])
            new_link = '</sys/docserver/rst/%s/%s>' %(self.fullname.replace('.','/'),record['hierarchical_name'])
            def cb(row):
                row['docbag'].replace.replace(old_link,new_link)
            self.batchUpdate(cb,
                            where='$docbag ILIKE :old_link_query OR $content_rst_en ILIKE :old_link_query',
                            old_link_query='%%%s%%',_raw_update=True)

        basepath = self.db.application.site.getStaticPath('site:webpages','docu_examples')
        old_tutorial_record_path = os.path.join(basepath,old_record['hierarchical_name'])
        tutorial_record_path = os.path.join(basepath,record['hierarchical_name'])
        if old_tutorial_record_path != tutorial_record_path:
            if os.path.exists(old_tutorial_record_path):
                shutil.rmtree(old_tutorial_record_path)
        if record['sourcebag'] != old_record['sourcebag']:
            if os.path.exists(tutorial_record_path):
                shutil.rmtree(tutorial_record_path)
            os.makedirs(tutorial_record_path)
        if record['sourcebag']:
            for source_version in record['sourcebag'].values():
                with open(os.path.join(tutorial_record_path,'%s.py' %source_version['version']),'w') as f:
                    f.write(source_version['source'])

    def applyOnTreeNodeAttr(self,_record=None,**kwargs):
        docbag = Bag(_record.pop('docbag',None))
        result = dict(_record=_record)
        for lang,content in docbag.items():
            result['title_%s' %lang] = content['title']
        return result

    def dfAsRstTable(self,pkey):
        rows = self.df_getFieldsRows(pkey=pkey)
        if not rows:
            return
        fdict = dict()
        for r in rows:
            page = r.pop('page',None) or 'Main'
            fdict.setdefault(page,[]).append(r)
       #if len(fdict)<2:
       #    return self.params_grid(title="Main Parameters",rows=rows)
        pages = fdict.keys()
        if 'Main' in pages:
            pages.remove('Main')
            pages = ['Main']+pages
        result = ''
        l0 = '+%s+%s+%s+' %(24*'-',6*'-',50*'-')
        ltemplate = '|%s|%s|%s|' 
        l1 = '+%s+%s+%s+' %(24*'=',6*'=',50*'=')
        result = [l0]
        result.append(ltemplate %('Parameter name'.center(24),'Type'.center(6),'Description'.center(50)))
        result.append(l1)
        for k,p in enumerate(pages):
            if k>0:
                result.append('|%s|' %('*%s Parameters*' %p).center(82) )
                result.append(l0)
            rows = fdict[p]
            for r in rows:
                documentation_rst = r.get('documentation') or r.get('field_tip') or ''
                doclist = textwrap.fill(documentation_rst,50).split('\n')
                for h,docline in enumerate(doclist):
                    if h == 0:
                        pname = r['code']
                        dtype = r['data_type']
                    else:
                        pname = ''
                        dtype = ''
                    result.append(ltemplate %(pname.ljust(24),dtype.ljust(6),docline.ljust(50)))
                result.append(l0)
        return '\n'.join(result)
