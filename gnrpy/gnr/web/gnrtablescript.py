#!/usr/bin/env python
# encoding: utf-8
"""
gnrtablescript.py

Created by Saverio Porcari on 2009-07-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import os.path
import tempfile
from gnr.core.gnrbag import Bag, BagCbResolver
from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrstring import toText
from gnr.core.gnrlang import NotImplementedException
from gnr.core.gnrstring import slugify, templateReplace

class TableScript(object):
    def __init__(self, page=None, resource_table=None, db=None, locale='en', tempFolder='', **kwargs):
        if page:
            self.page = page
            self.site = self.page.site
            self.locale = self.page.locale
            self.db = self.page.db
            self.docFolder = tempFolder or self.page.temporaryDocument()
            self.thermoKwargs = None
        else:
            self.db = db
            self.locale = locale
            self.tempFolder = tempFolder
        self.resource_table = resource_table
        self.init(**kwargs)

    def __call__(self, *args, **kwargs):
        raise NotImplementedException()

    def getFolderPath(self, *folders):
        folders = folders or []
        if folders and folders[0] == '*connections':
            folders = [self.page.connectionDocument(*list(folders[1:] + ('',)))]
        elif folders and folders[0] == '*users':
            folders = [self.page.userDocument(*list(folders[1:] + ('',)))]
        result = os.path.join(*folders)
        return result

    def getDocumentUrl(self, *args):
        args = args or []
        if args and args[0] == '*connections':
            result = [self.page.connectionDocumentUrl(*list(args[1:] + ('',)))]
        elif args and args[0] == '*users':
            result = [self.page.userDocumentUrl(*list(args[1:] + ('',)))]
        result = os.path.join(*result)
        return result

    def filePath(self, filename, *folders):
        return os.path.join(self.getFolderPath(*folders), filename)

    def fileUrl(self, folder, filename):
        return self.page.temporaryDocumentUrl(folder, filename)

class TableScriptOnRecord(TableScript):
    def __call__(self, record=None, **kwargs):
        raise NotImplementedException()

    def getData(self, path, default=None):
        wildchars = []
        if path[0] in wildchars:
            value = 'not yet implemented'
        else:
            value = self._data.getItem(path, default)
        return value

    def loadRecord(self, record=None, **kwargs):
        self._data = Bag()
        self._data['record'] = self.db.table(self.maintable or self.resource_table).recordAs(record, mode='bag')
        if kwargs:
            self._data['kwargs'] = Bag()
            for k, v in kwargs.items():
                self._data['kwargs.%s' % k] = v
        return self.onRecordLoaded(**kwargs)

    def onRecordLoaded(self, **kwargs):
        pass


    def outputDocName(self, ext=''):
        maintable_obj = self.db.table(self.maintable)
        if ext and not ext[0] == '.':
            ext = '.%s' % ext
        caption = ''
        if self.getData('record'):
            caption = slugify(maintable_obj.recordCaption(self.getData('record')))
        doc_name = '%s_%s%s' % (maintable_obj.name, caption, ext)
        return doc_name


class RecordToHtmlPage(TableScriptOnRecord):
    maintable = ''
    templates = ''
    rows_path = 'rows'
    html_folder = '*connections/html'
    pdf_folder = '*connections/pdf'
    encoding = 'utf-8'
    page_debug = False
    page_width = 200
    page_height = 280
    page_margin_top = 0
    page_margin_left = 0
    page_margin_right = 0
    page_margin_bottom = 0
    print_button = None
    currencyFormat = u'#,###.00'
    row_mode = 'bag'
    #override these lines
    row_mode = 'value'
    page_header_height = 0 #
    page_footer_height = 0
    page_leftbar_width = 0
    page_rightbar_width = 0
    doc_header_height = 0 # eg 10
    doc_footer_height = 0 # eg 15
    grid_header_height = 0 # eg 6.2
    grid_footer_height = 0
    grid_col_widths = [0, 0, 0]
    grid_row_height = 5
    copies_per_page = 1
    copy_extra_height = 0
    starting_page_number = 0

    def init(self, **kwargs):
        self.maintable = self.maintable or self.resource_table
        self.maintable_obj = self.db.table(self.maintable)
        self.stopped = False

    def __call__(self, record=None, filepath=None,
                 rebuild=False, dontSave=False, pdf=False, runKwargs=None,
                 showTemplateContent=None, **kwargs):
        """This method returns the html corresponding to a given record.
           the html can be loaded from a cached document or created if still doesn't exist.
        """
        if not record:
            return False
        self.showTemplateContent = showTemplateContent or True
        loadResult = self.loadRecord(record, **kwargs)
        if loadResult == False:
            return False
        self.htmlTemplate = None
        if self.templates:
            self.htmlTemplate = self.db.table('adm.htmltemplate').getTemplate(self.templates)
            self.page_height = self.page_height or self.htmlTemplate['main.page.height'] or 280
            self.page_width = self.page_width or self.htmlTemplate['main.page.width'] or 200
            self.page_header_height = self.page_header_height or  self.htmlTemplate['layout.top?height'] or 0
            self.page_footer_height = self.page_footer_height or  self.htmlTemplate['layout.bottom?height'] or 0
            self.page_leftbar_width = self.page_leftbar_width or  self.htmlTemplate['layout.left?width'] or 0
            self.page_rightbar_width = self.page_leftbar_width or  self.htmlTemplate['layout.right?width'] or 0
            self.page_margin_top = self.page_margin_top or self.htmlTemplate['main.page.top'] or 0
            self.page_margin_left = self.page_margin_left or self.htmlTemplate['main.page.left'] or 0
            self.page_margin_right = self.page_margin_right or self.htmlTemplate['main.page.right'] or 0
            self.page_margin_bottom = self.page_margin_bottom or self.htmlTemplate['main.page.bottom'] or 0

        self.builder = GnrHtmlBuilder(page_width=self.page_width, page_height=self.page_height,
                                      page_margin_top=self.page_margin_top, page_margin_bottom=self.page_margin_bottom,
                                      page_margin_left=self.page_margin_left, page_margin_right=self.page_margin_right,
                                      page_debug=self.page_debug, print_button=self.print_button,
                                      htmlTemplate=self.htmlTemplate,
                                      showTemplateContent=self.showTemplateContent)
        #if not (dontSave or pdf):
        self.filepath = filepath or os.path.join(self.hmtlFolderPath(), self.outputDocName(ext='html'))
        #else:
        #    self.filepath = None
        if self.page_height<self.page_width:
            self.orientation='Landscape'
        else:
            self.orientation='Portrait'
        
        if rebuild or not os.path.isfile(self.filepath):
            html = self.createHtml(filepath=self.filepath, **kwargs)

        else:
            with open(self.filepath, 'r') as f:
                html = f.read()
        if pdf:
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            self.page.getService('print').htmlToPdf(self.filepath, temp.name, orientation = self.orientation)
            with open(temp.name, 'rb') as f:
                html = f.read()
        self.onRecordExit(self.getData('record'))
        return html

    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, **kwargs):
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding, **kwargs)

    def createHtml(self, filepath=None, **kwargs):
        #filepath = filepath or self.filepath
        self.initializeBuilder()
        self.main()
        if not self.stopped:
            self.builder.toHtml(filepath=filepath)
            return self.builder.html

    def initializeBuilder(self):
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.getNewPage = self.builder.newPage
        self.builder.styleForLayout()

class RecordToHtmlMail(RecordToHtmlPage):
    pass

class RecordToHtmlNew(RecordToHtmlPage):
    def onRecordExit(self, recordBag):
        return

    def hmtlFolderPath(self):
        return self.getFolderPath(*self.html_folder.split('/'))

    def pdfFolderPath(self):
        return self.getFolderPath(*self.pdf_folder.split('/'))

    def field(self, path, default=None, locale=None,
              format=None, mask=None, root=None, **kwargs):
        if root is None:
            root = self._data['record']
        if isinstance(root, Bag):
            datanode = root.getNode(path)
            value = datanode.value
            attr = datanode.attr
        else:
            value = root.get(path)
            attr = {}
        if value is None:
            value = default
        elif isinstance(value, Bag):
            return value

        format = format or attr.get('format')
        mask = mask or attr.get('mask')
        return self.toText(value, locale, format, mask, self.encoding, **kwargs)

    def main(self):
        """can be overridden"""
        self.mainLoop()

    def pageCounter(self, mask=None):
        mask = mask or '%s/%s'

        def getPage(currPage=0):
            result = mask % (currPage + 1 + self.starting_page_number,
                             self.copies[self.copy]['currPage'] + 1 + self.starting_page_number)
            return result

        return BagCbResolver(getPage, currPage=self.copies[self.copy]['currPage'])


    def copyHeight(self):
        return (self.page_height - self.page_margin_top - self.page_margin_bottom -\
                self.page_header_height - self.page_footer_height -\
                self.copy_extra_height * (self.copies_per_page - 1)) / self.copies_per_page

    def copyWidth(self):
        return (self.page_width - self.page_margin_left - self.page_margin_right -\
                self.page_leftbar_width - self.page_rightbar_width)

    def mainLoop(self):
        self.copies = []
        self.lastPage = False
        self.defineStandardStyles()
        self.defineCustomStyles()
        self.doc_height = self.copyHeight() #- self.page_header_height - self.page_footer_height
        self.grid_height = self.doc_height - self.calcDocHeaderHeight() - self.doc_footer_height
        self.grid_body_height = self.grid_height - self.grid_header_height - self.grid_footer_height
        for copy in range(self.copies_per_page):
            self.copies.append(dict(grid_body_used=self.grid_height, currPage=-1))
        lines = self.getData(self.rows_path)
        if lines:
            nodes = lines.getNodes()
            if self.thermoKwargs:
                nodes = self.page.btc.thermo_wrapper(nodes, **self.thermoKwargs)
            for rowDataNode in nodes:
                self.currRowDataNode = rowDataNode
                for copy in range(self.copies_per_page):
                    self.copy = copy
                    rowheight = self.calcRowHeight()
                    availableSpace = self.grid_height - self.copyValue('grid_body_used') -\
                                     self.calcGridHeaderHeight() - self.calcGridFooterHeight()
                    if rowheight > availableSpace:
                        self._newPage()
                    row = self.copyValue('body_grid').row(height=rowheight)
                    self.copies[self.copy]['grid_body_used'] = self.copyValue('grid_body_used') + rowheight
                    self.currColumn = 0
                    self.currRow = row
                    self.prepareRow(row)

            for copy in range(self.copies_per_page):
                self.copy = copy
                self._closePage(True)

    def _newPage(self):
        if self.copyValue('currPage') >= 0:
            self._closePage()
        self.copies[self.copy]['currPage'] = self.copyValue('currPage') + 1
        self.copies[self.copy]['grid_body_used'] = 0
        self._createPage()
        self._openPage()

    def _get_rowData(self):
        if self.row_mode == 'attribute':
            return self.currRowDataNode.attr
        else:
            return self.currRowDataNode.value

    rowData = property(_get_rowData)

    def rowField(self, path=None, **kwargs):
        if self.row_mode == 'attribute':
            data = self.currRowDataNode.attr
        else:
            data = self.currRowDataNode.value
        return self.field(path, root=data, **kwargs)

    def rowCell(self, field=None, value=None, default=None, locale=None,
                format=None, mask=None, currency=None, **kwargs):
        if field:
            if callable(field):
                value = field()
            else:
                value = self.rowField(field, default=default, locale=locale, format=format, mask=mask,
                                      currency=currency)
        if value is not None:
            #if self.lastPage:
            #    print 'last page'
            #    print self.currColumn
            #    print self.grid_col_widths[self.currColumn]
            value = self.toText(value, locale, format, mask, self.encoding)
            self.currRow.cell(value, width=self.grid_col_widths[self.currColumn], overflow='hidden',
                              white_space='nowrap', **kwargs)
        self.currColumn = self.currColumn + 1
        return value

    def _createPage(self):
        curr_copy = self.copies[self.copy]
        if self.copy == 0:
            self.paperPage = self.getNewPage()
        self.page_layout = self.mainLayout(self.paperPage)
        #if self.page_header_height:
        #    curr_copy['page_header'] = self.page_layout.row(height=self.page_header_height,lbl_height=4,lbl_class='caption').cell()
        if self.doc_header_height:
            curr_copy['doc_header'] = self.page_layout.row(height=self.calcDocHeaderHeight(), lbl_height=4,
                                                           lbl_class='caption').cell()
        curr_copy['doc_body'] = self.page_layout.row(height=0, lbl_height=4, lbl_class='caption').cell()
        if self.doc_footer_height:
            curr_copy['doc_footer'] = self.page_layout.row(height=self.doc_footer_height, lbl_height=4,
                                                           lbl_class='caption').cell()
            #if self.page_footer_height:
            #    curr_copy['page_footer'] = self.page_layout.row(height=self.page_footer_height,lbl_height=4,lbl_class='caption').cell()

    def mainLayout(self, page):
        """must be overridden"""
        pass

    def _openPage(self):
        #if self.page_header_height:
        #    self.pageHeader(self.copyValue('page_header')) #makeTop
        if self.doc_header_height:
            self.docHeader(self.copyValue('doc_header'))
        self._docBody(self.copyValue('doc_body'))

    def _closePage(self, lastPage=None):
        if lastPage:
            self.lastPage = True
        self.fillBodyGrid()
        footer_height = self.calcGridFooterHeight()
        if footer_height:
            row = self.copyValue('body_grid').row(height=footer_height)
            self.currColumn = 0
            self.currRow = row
            self.gridFooter(row)
        if self.doc_footer_height:
            self.docFooter(self.copyValue('doc_footer'), lastPage=lastPage)
            #if self.page_footer_height:
            #    self.pageFooter(self.copyValue('page_footer'),lastPage=lastPage)

    def _docBody(self, body):
        header_height = self.calcGridHeaderHeight()
        grid = self.gridLayout(body)
        if header_height:
            self.gridHeader(grid.row(height=header_height))
        self.copies[self.copy]['body_grid'] = grid

    def gridLayout(self, grid):
        """must be overridden"""
        print 'gridLayout must be overridden'

    def gridHeader(self, row):
        """can be overridden"""
        lbl_height = 4
        headers = self.grid_col_headers
        if ':' in headers:
            headers, lbl_height = headers.split(':')
            lbl_height = int(lbl_height)
        for k, lbl in enumerate(self.grid_col_headers.split(',')):
            style = None
            if lbl == '|':
                lbl = ''
                style = 'border-top:0mm;border-bottom:0mm;'
            row.cell(lbl=lbl, lbl_height=lbl_height, width=self.grid_col_widths[k], style=style)

    def gridFooter(self, row):
        """can be overridden"""
        print 'gridFooter must be overridden'

    def fillBodyGrid(self):
        row = self.copyValue('body_grid').row()
        for w in self.grid_col_widths:
            row.cell(width=w)

    def copyValue(self, valuename):
        return self.copies[self.copy][valuename]

    def calcRowHeight(self):
        """override for special needs"""
        return self.grid_row_height

    def calcGridHeaderHeight(self):
        """override for special needs"""
        return self.grid_header_height

    def calcGridFooterHeight(self):
        """override for special needs"""
        return self.grid_footer_height

    def calcDocHeaderHeight(self):
        """override for special needs"""
        return self.doc_header_height

    def defineCustomStyles(self):
        """override this for custom styles"""
        pass

    def docFooter(self, footer, lastPage=None):
        pass

    def pageFooter(self, footer, lastPage=None):
        pass

    def pageHeader(self, header):
        pass

    def docHeader(self, header):
        pass

    def defineStandardStyles(self):
        self.body.style("""
                        .caption{text-align:center;
                                 color:gray;
                                 font-size:8pt;
                                 height:4mm;
                                 line-height:4mm;
                                 font-weight: normal;
                                 }
                        .smallCaption{font-size:7pt;
                                  text-align:left;
                                  color:gray;
                                  text-indent:1mm;
                                  width:auto;
                                  font-weight: normal;
                                  line-height:auto;
                                  line-height:3mm;
                                  height:3mm;""")

        self.body.style("""
                        .extrasmall {font-size:6pt;text-align:left;line-height:3mm;}
                        .textfield {text-indent:0mm;margin:1mm;line-height:3mm}
                        .dotted_bottom {border-bottom:1px dotted gray;}
                                                
                        .aligned_right{
                            text-align:right;
                            margin-right:1mm;
                        }
                        .aligned_left{
                            text-align:left;
                            margin-left:1mm;
                        }
                        .aligned_center{
                            text-align:center;
                        }
                         """)


class RecordToHtml(TableScriptOnRecord):
    maintable = ''
    templates = ''
    html_folder = '*connections/html'
    pdf_folder = '*connections/pdf'
    encoding = 'utf-8'
    page_debug = False
    page_width = 200
    page_height = 280
    print_button = None
    page_margin_top = 0
    page_margin_left = 0
    page_margin_right = 0
    page_margin_bottom = 0
    htmlTemplate = None


    def init(self, **kwargs):
        self.maintable = self.maintable or self.resource_table
        self.maintable_obj = self.db.table(self.maintable)
        if self.templates:
            self.htmlTemplate = self.db.table('adm.htmltemplate').getTemplate(self.templates)
        self.builder = GnrHtmlBuilder(page_width=self.page_width, page_height=self.page_height,
                                      page_margin_top=self.page_margin_top, page_margin_bottom=self.page_margin_bottom,
                                      page_margin_left=self.page_margin_left, page_margin_right=self.page_margin_right,
                                      page_debug=self.page_debug, print_button=self.print_button,
                                      htmlTemplate=self.htmlTemplate)

    def __call__(self, record=None, filepath=None,
                 rebuild=False, dontSave=False, pdf=False, runKwargs=None, **kwargs):
        """This method returns the html corresponding to a given record.
           the html can be loaded from a cached document or created if still doesn't exist.
        """
        if not record:
            return
        self.loadRecord(record, **kwargs)
        if kwargs:
            self._data['kwargs'] = Bag()
            for k, v in kwargs.items():
                self._data['kwargs.%s' % k] = v

        #if not (dontSave or pdf):
        self.filepath = filepath or os.path.join(self.hmtlFolderPath(), self.outputDocName(ext='html'))
        #else:
        #    self.filepath = None
        if self.page_height<self.page_width:
            self.orientation='Landscape'
        else:
            self.orientation='Portrait'
        
        if rebuild or not os.path.isfile(self.filepath):
            html = self.createHtml(filepath=self.filepath, **kwargs)

        else:
            with open(self.filepath, 'r') as f:
                html = f.read()
        if pdf:
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            self.page.getService('print').htmlToPdf(self.filepath, temp.name, orientation=self.orientation)
            with open(temp.name, 'rb') as f:
                html = f.read()
        return html

    def createHtml(self, filepath=None, **kwargs):
        #filepath = filepath or self.filepath
        self.initializeBuilder()
        self.main()
        self.builder.toHtml(filepath=filepath)
        return self.builder.html

    def initializeBuilder(self):
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.getNewPage = self.builder.newPage
        self.builder.styleForLayout()

    def hmtlFolderPath(self):
        return self.getFolderPath(*self.html_folder.split('/'))

    def pdfFolderPath(self):
        return self.getFolderPath(*self.pdf_folder.split('/'))

    def field(self, path, default=None, locale=None,
              format=None, mask=None, root=None):
        root = root or self._data['record']
        datanode = root.getNode(path, default)
        value = datanode.value
        attr = datanode.attr
        if value is None:
            value = default
        if isinstance(value, Bag):
            return value
        format = format or attr.get('format')
        mask = mask or attr.get('mask')
        return self.toText(value, locale, format, mask, self.encoding)

    def toText(self, obj, locale=None, format=None, mask=None, encoding=None):
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
        