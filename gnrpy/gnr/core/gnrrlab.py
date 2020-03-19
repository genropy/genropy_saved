from reportlab.pdfgen import canvas
from io import BytesIO
from gnr.core.gnrstring import slugify

class RlabResource(object):
    """TODO"""
    rows_table = None
    virtual_columns = None
    pdf_folder = 'page:pdf'
    cached = None
    client_locale = False
    row_relation = None
    subtotal_caption_prefix = '!![en]Totals'


    def __init__(self, page=None, resource_table=None, parent=None, **kwargs):
        self.parent = parent
        self.page = page
        self.site = page.site
        self.db = page.db
        self.locale = self.page.locale if self.client_locale else self.site.server_locale
        self.tblobj = resource_table
        self.maintable = resource_table.fullname if resource_table else None
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.thermo_wrapper = self.page.btc.thermo_wrapper
        self.letterhead_sourcedata = None
        self._gridStructures = {}
        self.record = None
        

    def __call__(self, record=None, pdf=None, downloadAs=None, thermo=None,record_idx=None, resultAs=None,
                    language=None,locale=None,**kwargs):
        if not record:
            return
        self.thermo_kwargs = thermo
        self.record_idx = record_idx
        if record=='*':
            record = None
        else:
            record = self.tblobj.recordAs(record, virtual_columns=self.virtual_columns)
        if locale:
            self.locale = locale #locale forced
        self.language = language    
        if self.language:
            self.language = self.language.lower()
            self.locale = locale or '{language}-{languageUPPER}'.format(language=self.language,
                                        languageUPPER=self.language.upper())
        elif self.locale:
            self.language = self.locale.split('-')[0].lower()
        result = self.makePdf(record=record, **kwargs) 

        if downloadAs:
            with self.pdfSn.open('rb') as f:
                self.page.response.add_header("Content-Disposition", str("attachment; filename=%s" % self.pdfSn.basename))
                self.page.response.content_type = 'application/pdf'
                result = f.read()
            return result            
        else:
            return self.pdfSn.url() if resultAs=='url' else self.pdfSn.fullpath

    def getPdfPath(self, *args, **kwargs):
        """potrebbe essere ereditato"""
        return self.site.getPdfStorageNode(*args, **kwargs).internal_path

    def getPdfStorageNode(self, *args, **kwargs):
        return self.site.storageNode(self.pdf_folder, *args, **kwargs)

    def makePdfIO(self, record=None, **kwargs):
        pdf = BytesIO()
        self.canvas = canvas.Canvas(pdf)
        self.main()
        self.canvas.showPage()
        self.canvas.save()
        pdf.seek(0)
        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_pdf.pdf'))
        self.response.content_type = 'application/pdf'
        return pdf.read()

    def outputDocName(self, ext='pdf'):
        """TODO
        :param ext: TODO"""
        if ext and not ext[0] == '.':
            ext = '.%s' % ext
        caption = ''
        if self.record is not None:
            caption = slugify(self.tblobj.recordCaption(self.record))
            idx = self.record_idx
            if idx is not None:
                caption = '%s_%i' %(caption,idx)
        doc_name = '%s_%s%s' % (self.tblobj.name, caption, ext)
        return doc_name

    def makePdf(self, record=None, **kwargs):
        self.record = record
        self.pdfSn = self.getPdfStorageNode(self.outputDocName())
        with self.pdfSn.local_path() as pdf_path:
            self.canvas = canvas.Canvas(pdf_path)
            self.main()
            self.canvas.showPage()
            self.canvas.save()

    def main(self):
        """must be overridden"""
        pass

    



