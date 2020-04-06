from gnr.pdf.gnrrml import GnrPdf

#class GnrWebPDF(GnrPdf):
#    
#    def getPdf(self, table, record, filename = None, folder=None):
#        record = self.db.table(table).recordAs(record, mode='bag')
#        self.filename=filename or self.getFilename(record)
#        self.filePath=self.page.temporaryDocument(folder, self.filename)
#        self.fileUrl=self.page.temporaryDocumentUrl(folder, self.filename)
#        self.createStory(record)
#
#    #def _get_pdf_url(self):
#    #    self.toPdf(self.filePath)
#    #    return self.pdfUrl
#    #pdfUrl=property(_get_pdf_url)
#


class JobTicketPDF(GnrWebPDF):
    
    def init(self, page):
        self.pdf=GnrWebPDF()
        self.page=page
        self.template(pageSize='A4',um='cm')
        self.defineStyles()
        self.pageTemplate('main')
    

    
    def getFilename(self, record):
        return 'job_ticket_%s.pdf'%record['code'].strip()
    
    def defineStyles(self):
        self.tableStyle('invHeader')
        self.paraStyle(name="TopCenter", fontName="Helvetica", fontSize="8", alignment="center", spaceBefore="0.2cm", spaceAfter="0.1cm")

    def createStory(self,record):
        jobs = record['@pforce_job_invoice_id']
        client = record['@client_id'
        division_data = mainpage.db.table('pforce.office').record('*',
                                                           where='code=:officecode',
                                                           officecode='PFPER').output('bag')
        story = self.story('main')
        self.topHeader(story,division_data)
        self.invHeader(story,record, client)
        self.rows(story, record, jobs)
        
            
    def rows(self, story, record, jobs):
        for j in jobs:
            self.jobRow(story, record, jobs)
            
    def topHeader(self,story,division_data):
        tbl = story.blockTable(colWidths="6cm,4cm", style="topHeader")
        tbl.row(['image placeholder','PRINTFORCE'])
        tbl.row([division_data['address']], startcol=1)
        tbl.row([division_data['suburb']], startcol=1)
        tbl.row([division_data['post_code']], startcol=1)
        tbl.row([division_data['state']], startcol=1)
        tbl.row([division_data['phone']], startcol=1)
        tbl.row('info@printforce.com.au'], startcol=1)
        
    def invHeader(self,story,record, client):
        tbl = story.blockTable(colWidths="4cm,6cm,4cm,6cm", style="invHeader")
        if record['old_id']:
            invoice_number='%s (%s)' % (record['invoice_number'], record['old_id'])
        tbl.row(['Invoice number',invoice_number,'Account',
                [self.para(client('company_name'),
                 self.para(client('pty_ltd_name'),
                 self.para(client('@main_address_id.street')),
                 self.para('%s %s %s' % (client('@main_address_id.suburb'),
                                         client('@main_address_id.postcode'),
                                         client('@main_address_id.state')))])
        tbl.row(['Date', record['invoice_date'], None, None]
        tbl.row(['Currency', 'AUSD', None, None]
        tbl.row(['ABN', client['abn'], None, None]
        tbl.row(['ACN', client['acn'], None, None]
                                                                     
    
    def jobRow(self,story,division_data):
        pass
        
    def footer(self,story,division_data):
        pass
            
    def tableStyle_topHeader(self, sh):
        sh.blockFont(name='Helvetica', size=9)   
        sh.blockAlignment(value='left')
        sh.lineStyle(kind='GRID', colorName='black', thickness='0')
        sh.lineStyle(kind='OUTLINE', colorName='black', thickness='0')
        sh.blockSpan(start="0,0", stop="0,-1")
    
    def tableStyle_invHeader(self, sh):
        sh.blockFont(name='Helvetica', size=9)   
        sh.blockAlignment(value='right', start='0,0', stop='0,-1')
        sh.blockAlignment(value='left', start='1,0', stop='1,-1')
        sh.blockAlignment(value='right', start='2,0', stop='2,-1')
        sh.blockAlignment(value='left', start='3,0', stop='3,-1')
        sh.blockSpan(start="2,0", stop="2,3")
        sh.blockSpan(start="3,0", stop="3,3")
        
        sh.lineStyle(kind='GRID', colorName='black', thickness='0.5')
        sh.lineStyle(kind='OUTLINE', colorName='black', thickness='0.5')
        sh.blockSpan(start="0,0", stop="0,-1")
    
    def tableStyle_jobRow(self, sh):
        pass
    
    def tableStyle_rows(self, sh):
        pass
        
    def tableStyle_footer(self, sh):
        pass
        
        
    def pageTemplate_main(self,template):
        template.frame(id='first', x1="0.8cm", y1="16.8cm", width="18.9cm", height="11.1cm")
        
if __name__=='__main__':
    from gnr.app.gnrapp import GnrApp
    filename='ticket.pdf'
    app = GnrApp('pforce')
    m=Main(db=app.db, filename=filename)
    m.getPdf('qgzzuu7CEd23BwAX8t4orw')
    m.toRml('~/ticket.rml')
    m.toPdf('~/ticket.pdf')
    