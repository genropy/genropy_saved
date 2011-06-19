# encoding: utf-8
import re
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrbag import Bag
import lxml.html as ht
from StringIO import StringIO
from gnr.core.gnrstring import templateReplace

TEMPLATEROW = re.compile(r"<!--TEMPLATEROW:(.*?)-->")

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('doctemplate', pkey='name', name_long='!!Document template',
                        name_plural='!!Document templates')
        self.sysFields(tbl, id=False)
        tbl.column('name', name_long='!!Name', validate_nodup=True, unique=True,
                   validate_notnull=True, validate_notnull_error='!!Name is mandatory',
                   validate_nodup_error='!!This name is already taken',_sendback=True)
        tbl.column('content', name_long='!!Content')
        tbl.column('metadata', 'X', name_long='!!Metadata')
        tbl.column('varsbag', 'X', name_long='!!Variables')
        tbl.column('username', name_long='!!Username')
        tbl.column('version', name_long='!!Version')
        tbl.column('maintable', name_long='!!Main table')
        tbl.column('resource_name',name_long='!!Resource Name',_sendback=True)

    def trigger_onInserted(self, record_data):
        if record_data.get('resource_name'):
            self.copyToResource(record_data['name'])
        
    def trigger_onUpdated(self, record_data, old_record):
        if record_data.get('resource_name'):
            self.copyToResource(record_data['name'])
    
    def copyToResource(self,pkey):
        record = self.record(pkey=pkey).output('bag')
        table = record['maintable']
        resource_name = record['resource_name']
        varsbag = record['varsbag']
        self.db.application.site.currentPage.setTableResourceContent(table=table,path='tpl/%s' %resource_name,value=record,ext='xml')

    
    def cleanTemplate(self, doctemplate_content, virtual_columns=None):
        virtual_columns = [] if virtual_columns is None else virtual_columns
        EXTRACT_FIELDS_STRIPPED_RE = r'(?:\$)(.*?)(?:<|\s)'
        EXTRACT_FIELDS_RE = r'(\$.*?)(?:<|\s)'
        SUB_SPAN_RE = r'(<span\s+class="tplfieldpath".*?/span>\s*<span\s+class="tplfieldcaption".*?/span>)'
        extract_fields_stripped = re.compile(EXTRACT_FIELDS_STRIPPED_RE)
        sub_span = re.compile(SUB_SPAN_RE)
        extract_fields = re.compile(EXTRACT_FIELDS_RE)

        def replace_span(a):
            b = a.group()
            if 'virtual_column' in b:
                virtual_columns.append(b.split('fieldpath="')[1].split('"')[0])
            return ' '.join(extract_fields.findall(a.group(0), re.MULTILINE))

        return sub_span.sub(replace_span, doctemplate_content)


    def renderTemplate(self, templateBuilder, record_id=None, extraData=None):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,
                                                        virtual_columns=templateBuilder.virtual_columns).output('bag')
        if extraData:
            record.update(extraData)
        record.setItem('_env_', Bag(self.db.currentEnv))
        record.setItem('_template_', templateBuilder.doctemplate_info)
        varsdict = dict([(k,'$%s' %v) for k,v in templateBuilder.varsbag.digest('#v.varname,#v.fieldpath')])
        
        htmlContent = templateReplace(templateBuilder.doctemplate, varsdict, True,False)
        htmlContent = self.expandSubtemplates(htmlContent)
        body = templateBuilder(htmlContent=templateReplace(htmlContent,record, True,False),record=record)
        return body
    
    def expandSubtemplates(self,htmlContent):
        result = Bag()
        doc = ht.parse(StringIO(htmlContent)).getroot()
        htmltables = doc.xpath('//table')
        for t in htmltables:
            attributes = t.attrib
            if 'row_datasource' in attributes:
                subname = attributes['row_datasource']
                tbody = t.xpath('tbody')[0]
                tbody_lastrow = tbody.getchildren()[-1]
                tbody.replace(tbody_lastrow,ht.etree.Comment('TEMPLATEROW:$%s' %subname))
                subtemplate=ht.tostring(tbody_lastrow).replace('%s.'%subname,'')
                result.setItem(subname.replace('.','_'),subtemplate)
        result.setItem('main', TEMPLATEROW.sub(lambda m: '\n%s\n'%m.group(1),ht.tostring(doc)))
        return result
        
 
    def getTemplateBuilder(self, doctemplate=None, templates=None):
        doctemplate = self.recordAs(doctemplate, 'bag')
        doctemplate_content = doctemplate.pop('content')
        doctemplate_info = doctemplate
        htmlbuilder = BagToHtml(templates=templates, templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.varsbag = doctemplate['varsbag']
        htmlbuilder.doctemplate = doctemplate_content
        virtual_columns = [c[0] for c in htmlbuilder.varsbag.digest('#v.fieldpath,#v.virtual_column') if c[1]]
        htmlbuilder.virtual_columns = ','.join(virtual_columns)
        htmlbuilder.data_tblobj = self.db.table(doctemplate_info['maintable'])
        htmlbuilder.doctemplate_info = doctemplate_info
        return htmlbuilder
    
    def sendMail(self,record_id=None,doctemplate=None,templates=None,**kwargs):
        site = self.db.application.site
        from_address= kwargs.pop('from_address', site.getPreference('mail.from_address', pkg='adm'))
        htmlBuilder = self.getTemplateBuilder(doctemplate=doctemplate,templates=templates)
        body = self.renderTemplate(htmlBuilder, record_id=record_id)
        datasource = htmlBuilder.record
        metadata = htmlBuilder.doctemplate_info.getItem('metadata')
        datasource['_meta_'] = metadata
        site.mail_handler.sendmail_template(datasource=datasource,
                                            body= body,
                                            from_address= from_address,
                                            smtp_host= site.getPreference('mail.smtp_host',pkg='adm'),
                                            port=int(site.getPreference('mail.port', pkg='adm')),
                                            password=site.getPreference('mail.password', pkg='adm'),
                                            user= site.getPreference('mail.user', pkg='adm'),
                                            html=True,ssl=False,tls=site.getPreference('mail.tls', pkg='adm'),
                                            **kwargs)
        
        