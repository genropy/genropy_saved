# encoding: utf-8
import re
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrbag import Bag
from StringIO import StringIO
from gnr.core.gnrstring import templateReplace

TEMPLATEROW = re.compile(r"<!--TEMPLATEROW:(.*?)-->")

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('doctemplate', pkey='id', name_long='!!Document template',
                        name_plural='!!Document templates',rowcaption='$name')
        self.sysFields(tbl)
        tbl.column('name', name_long='!!Name', validate_nodup=True, unique=True,
                   validate_notnull=True, validate_notnull_error='!!Name is mandatory',
                   validate_nodup_error='!!This name is already taken',_sendback=True)
        tbl.column('content', name_long='!!Content',_sendback=True)
        tbl.column('templatebag','X')
        tbl.column('metadata', 'X', name_long='!!Metadata')
        tbl.column('varsbag', 'X', name_long='!!Variables',_sendback=True)
        tbl.column('username', name_long='!!Username')
        tbl.column('version', name_long='!!Version')
        tbl.column('locale', name_long='!!Locale')
        tbl.column('maintable', name_long='!!Main table')
        tbl.column('resource_name',name_long='!!Resource Name',_sendback=True)

    def trigger_onInserting(self, record_data):
        self.compileTemplate(record_data)
        
    def trigger_onUpdating(self,record_data,old_record=None):
        self.compileTemplate(record_data)
    
    def trigger_onInserted(self, record_data):
        if record_data.get('resource_name'):
            self.copyToResource(record_data['name'])
        
    def trigger_onUpdated(self, record_data, old_record):
        if record_data.get('resource_name'):
            self.copyToResource(record_data)
    
    def copyToResource(self,record):
        table = record['maintable']
        resource_name = record['resource_name']
        self.db.application.site.currentPage.setTableResourceContent(table=table,path='tpl/%s' %resource_name,
                                                                     value=record['templatebag'],
                                                                     ext='xml')

    def renderTemplate(self, templateBuilder, record_id=None, extraData=None, locale=None, formats=None,**kwargs):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,
                                                        virtual_columns=templateBuilder.virtual_columns).output('bag')
        if extraData:
            record.update(extraData)
        locale = locale or templateBuilder.locale
        formats = templateBuilder.formats or dict()
        formats.update(templateBuilder.formats or dict())
        record.setItem('_env_', Bag(self.db.currentEnv))
        #record.setItem('_template_', templateBuilder.doctemplate_info)
        body = templateBuilder(htmlContent=templateReplace(templateBuilder.doctemplate,record, safeMode=True,noneIsBlank=False,locale=locale, formats=formats),
                            record=record,**kwargs)
        return body
    
    
    def compileTemplate(self,record):
        import lxml.html as ht
        tplvars =  record['varsbag'].digest('#v.varname,#v.fieldpath,#v.virtual_column,#v.format')
        #varsdict = dict([(varname,'$%s' %fldpath) for varname,fldpath,virtualcol,format in tplvars])
        #virtual_columns = [fldpath for varname,fldpath,virtualcol,format in tplvars if virtualcol]
        #columns = [fldpath for varname,fldpath,virtualcol in tplvars]
        formats = dict()
        columns = []
        virtual_columns = []
        varsdict = dict()
        for varname,fldpath,virtualcol,format in tplvars:
            varsdict[varname] = '$%s' %fldpath
            formats[fldpath] = format
            columns.append(fldpath)
            if virtualcol:
                virtual_columns.append(fldpath)
                
        template = templateReplace(record['content'], varsdict, True,False)
        templatebag = Bag()
        doc = ht.parse(StringIO(template)).getroot()
        htmltables = doc.xpath('//table')
        for t in htmltables:
            attributes = t.attrib
            if 'row_datasource' in attributes:
                subname = attributes['row_datasource']
                tbody = t.xpath('tbody')[0]
                tbody_lastrow = tbody.getchildren()[-1]
                tbody.replace(tbody_lastrow,ht.etree.Comment('TEMPLATEROW:$%s' %subname))
                subtemplate=ht.tostring(tbody_lastrow).replace('%s.'%subname,'')
                templatebag.setItem(subname.replace('.','_'),subtemplate)
        templatebag.setItem('main', TEMPLATEROW.sub(lambda m: '\n%s\n'%m.group(1),ht.tostring(doc)),
                            maintable=record['maintable'],locale=record['locale'],virtual_columns=','.join(virtual_columns),columns=','.join(columns),formats=formats)
        record['templatebag'] = templatebag
        
 
    def getTemplateBuilder(self, templatebag=None, templates=None):
        #doctemplate = self.recordAs(doctemplate, 'bag')
        #doctemplate_content = doctemplate.pop('content')
        #doctemplate_info = doctemplate
        htmlbuilder = BagToHtml(templates=templates, templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.doctemplate = templatebag
        htmlbuilder.virtual_columns = templatebag.getItem('main?virtual_columns')
        htmlbuilder.locale = templatebag.getItem('main?locale')
        htmlbuilder.formats = templatebag.getItem('main?formats')
        htmlbuilder.data_tblobj = self.db.table(templatebag.getItem('main?maintable'))
        #htmlbuilder.doctemplate_info = doctemplate_info
        return htmlbuilder
    
    def sendMail(self,record_id=None,doctemplate=None,templates=None,**kwargs):
        site = self.db.application.site
        htmlBuilder = self.getTemplateBuilder(doctemplate=doctemplate,templates=templates)
        body = self.renderTemplate(htmlBuilder, record_id=record_id)
        datasource = htmlBuilder.record
        metadata = htmlBuilder.doctemplate_info.getItem('metadata')
        datasource['_meta_'] = metadata
        site.mail_handler.sendmail_template(datasource=datasource,
                                            body= body,
                                            smtp_host= site.getPreference('mail.smtp_host',pkg='adm'),
                                            port=int(site.getPreference('mail.port', pkg='adm')),
                                            password=site.getPreference('mail.password', pkg='adm'),
                                            user= site.getPreference('mail.user', pkg='adm'),
                                            html=True,ssl=False,tls=site.getPreference('mail.tls', pkg='adm'),
                                            **kwargs)
        
        