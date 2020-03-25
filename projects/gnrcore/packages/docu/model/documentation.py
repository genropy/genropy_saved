#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
import textwrap

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('documentation', pkey='id', name_long='!!Documentation', 
                        name_plural='!!Documentation',caption_field='name',audit='lazy')
        self.sysFields(tbl,hierarchical='name',df=True,
                        counter=True,user_ins=True,user_upd=True)
        tbl.column('name',name_long='!!Name', validate_notnull=True)
        tbl.column('topics',name_long='!!Topics')
        tbl.column('publish_date',dtype='D',name_long='!!Publish date')
        tbl.column('sourcebag',dtype='X',name_long='Python Source',_sendback=True)
        tbl.column('docbag',dtype='X',name_long='Rst data',_sendback=True)
        tbl.column('revision',size=':3', name_long='!!Revision',values='001:Draft,050:Work in progress,080:Pre-release,100:Final')
        tbl.column('author', name_long='Author')
        tbl.column('base_language',size='2',name_long='Base language').relation('docu.language.code',mode='foreignkey')
        tbl.column('old_html')
        tbl.column('sphinx_toc', dtype='B', name_long='Sphinx toc')

        tbl.formulaColumn('example_url',"'/webpages/docu_examples/'||$hierarchical_name")


        tbl.formulaColumn('is_published',"""
            CASE WHEN $publish_date IS NOT NULL THEN EXISTS(#has_published_children)
            ELSE $publish_date<=:env_workdate END
            """,select_has_published_children=dict(table='docu.documentation',
                                                    where="""$hierarchical_pkey ILIKE #THIS.hierarchical_pkey||'%%'
                                                            AND ($publish_date IS NOT NULL AND $publish_date<=:env_workdate)"""),
                    dtype='B')


    def formulaColumn_doc_sources(self):
        result = []
        for lang in self.db.table('docu.language').query().fetch():
            l = lang['code']
            sql_formula = self.model.bagItemFormula('$docbag','%s.rst' %l)
            result.append(dict(name='rst_%s' %l,sql_formula=sql_formula, name_long='!!Rst %s' %l))
            sql_formula = self.model.bagItemFormula('$docbag','%s.title' %l)
            result.append(dict(name='title_%s' %l,sql_formula=sql_formula, name_long='!!Title %s' %l))
        return result


    def trigger_onUpdating(self,record,old_record):
        record['sourcebag'] = record['sourcebag'] or None
        if record['sourcebag']:
            record['sourcebag'] = Bag(record['sourcebag'])
            for v in record['sourcebag'].values():
                v['url'] = '/webpages/docu_examples/%s/%s.py' %(record['hierarchical_name'],v['version'])


    def updateLink(self, record, old_record):
        old_link = '&lt;%s/%s&gt;' %(self.pkg.htmlProcessorName(),old_record['hierarchical_name'])
        new_link = '&lt;%s/%s&gt;' %(self.pkg.htmlProcessorName(),record['hierarchical_name'])
        
        def cb(row):
            row['docbag'] = row['docbag'].replace(old_link,new_link)
        
        self.batchUpdate(cb,where='$docbag ILIKE :old_link_query OR $docbag ILIKE :old_link_query',
                            old_link_query='%%%s%%',_raw_update=True,bagFields=True)

    def trigger_onUpdated(self,record,old_record):
        if record['hierarchical_name'] != old_record['hierarchical_name']:
            self.updateLink(record, old_record)
            if record['sourcebag'] and record['sourcebag']==old_record['sourcebag']:
                self.tutorialRecordNode(old_record).move(self.tutorialRecordNode(record))
        if record['sourcebag'] != old_record['sourcebag']:
            self.writeModulesFromSourceBag(record)

    def tutorialRecordNode(self,record):
        return self.db.application.site.storageNode('site:webpages','docu_examples',record['hierarchical_name'])

    def writeModulesFromSourceBag(self,record):
        tutorial_record_node = self.tutorialRecordNode(record)
        if tutorial_record_node.exists:
            for n in tutorial_record_node.children():
                if n.exists and not n.isdir:
                    tutorial_record_node.delete()
        if record['sourcebag']:
            for source_version in record['sourcebag'].values():
                with tutorial_record_node.child('%(version)s.py' %source_version).open('wb') as f:
                    f.write(source_version['source'])

    @public_method
    def checkSourceBagModules(self,record=None,**kwargs):
        if not record['sourcebag']:
            return
        tutorial_record_node = self.tutorialRecordNode(record)
        for source_version in record['sourcebag'].values():
            n = tutorial_record_node.child('%(version)s.py' %source_version)
            if not n.exists:
                with n.open('wb') as f:
                    f.write(source_version['source'])

    def applyOnTreeNodeAttr(self,_record=None,**kwargs):
        docbag = Bag(_record.pop('docbag',None))
        result = dict(_record=_record)
        for lang,content in docbag.items():
            result['title_%s' %lang] = content['title']
        return result

    def atcAsRstTable(self, pkey, host=None):
        attachments = self.db.table('docu.documentation_atc').query(columns='*,$fileurl',where='$maintable_id=:pkey AND $atc_download IS TRUE', pkey=pkey).fetch()
        if not attachments:
            return
        result = []
        host = host or ''
        tpl = """- `%(description)s <%(host)s%(fileurl)s?download=1>`_ """

        for atc in attachments:
            atc = dict(atc)
            atc['host'] = host
            result.append(tpl % atc)
        return '\n'.join(result)

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
                        if pname.endswith('_'):
                            pname = '%s\_' %pname[0:-1]
                        dtype = r['data_type']
                    else:
                        pname = ''
                        dtype = ''
                    result.append(ltemplate %(pname.ljust(24),dtype.ljust(6),docline.ljust(50)))
                result.append(l0)
        return '\n'.join(result)


    def exportToSphinx(self, path):
        pass

    def tableOfContents(self, pkey=None, ref_date=None):
        where='$publish_date IS NOT NULL AND $publish_date>=:curr_date'
        if pkey:
            where='%s AND $parent_id=:pkey'
        children =self.query(where=where, curr_date=ref_date or self.db.workdate, pkey=pkey).fetch()
        for c in children:
            pass
    
