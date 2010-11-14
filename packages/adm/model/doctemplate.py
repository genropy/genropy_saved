# encoding: utf-8
import re
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrbag import Bag

from gnr.core.gnrstring import templateReplace

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('doctemplate',pkey='name',name_long='!!Document template',
                      name_plural='!!Document templates')
        self.sysFields(tbl,id=False)
        tbl.column('name',name_long='!!Name',validate_nodup=True,unique=True,
                    validate_notnull=True,validate_notnull_error='!!Name is mandatory',
                    validate_nodup_error='!!This name is already taken')
        tbl.column('content',name_long='!!Content')
        tbl.column('metadata','X',name_long='!!Metadata')
        tbl.column('username',name_long='!!Username')
        tbl.column('version',name_long='!!Version')
        tbl.column('maintable',name_long='!!Main table')
    
    def cleanTemplate(self,doctemplate_content,virtual_columns=None):
        virtual_columns = [] if virtual_columns is None else virtual_columns
        EXTRACT_FIELDS_STRIPPED_RE=r'(?:\$)(.*?)(?:<|\s)'
        EXTRACT_FIELDS_RE=r'(\$.*?)(?:<|\s)'
        SUB_SPAN_RE=r'(<span\s+class="tplfieldpath".*?/span>\s*<span\s+class="tplfieldcaption".*?/span>)'
        extract_fields_stripped=re.compile(EXTRACT_FIELDS_STRIPPED_RE)
        sub_span=re.compile(SUB_SPAN_RE)
        extract_fields=re.compile(EXTRACT_FIELDS_RE)
        def replace_span(a):
            b = a.group()
            if 'virtual_column' in b:
                virtual_columns.append(b.split('fieldpath="')[1].split('"')[0])
            return ' '.join(extract_fields.findall(a.group(0),re.MULTILINE))
        return sub_span.sub(replace_span,doctemplate_content)
        
    
    def renderTemplate(self,templateBuilder,record_id=None,extraData=None):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,virtual_columns=templateBuilder.virtual_columns).output('bag')
        if extraData:
            record.update(extraData)
        record.setItem('_env_',Bag(self.db.currentEnv))
        record.setItem('_template_',templateBuilder.doctemplate_info)
        templateBuilder.record = record
        return templateBuilder(htmlContent=templateReplace(templateBuilder.doctemplate,record,True))
        
    def getTemplateBuilder(self,doctemplate=None,templates=None):
        doctemplate = self.recordAs(doctemplate,'bag')
        doctemplate_content = doctemplate.pop('content')
        doctemplate_info = doctemplate
        virtual_columns = []
        htmlbuilder = BagToHtml(templates=templates,templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.doctemplate =  self.cleanTemplate(doctemplate_content,virtual_columns)
        htmlbuilder.virtual_columns = ','.join(virtual_columns)
        htmlbuilder.data_tblobj = self.db.table(doctemplate_info['maintable'])
        htmlbuilder.doctemplate_info = doctemplate_info
        return htmlbuilder
        
        