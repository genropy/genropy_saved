#!/usr/bin/env python
# encoding: utf-8
#
# gnrbaghtml.py
#
# Created by Francesco Porcari on 2010-10-16.
# Copyright (c) 2011 Softwell. All rights reserved.

import os
from gnr.core.gnrstring import toText
from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrbag import Bag, BagCbResolver
from gnr.core.gnrdecorator import extract_kwargs
import tempfile

class BagToHtml(object):
    """A class that transforms a :ref:`bag` into HTML. It can be used to make a :ref:`print`"""
    css_requires = ''
    templates = ''
    letterhead_id = ''
    currencyFormat = u'#,###.00'
    encoding = 'utf-8'
    page_debug = False
    page_width = 200
    page_height = 280
    page_margin_top = 0
    page_margin_left = 0
    page_margin_right = 0
    page_margin_bottom = 0
    page_header_height = 0
    page_footer_height = 0
    page_leftbar_width = 0
    page_rightbar_width = 0
    print_button = None
    row_mode = 'value'
    rows_path = 'rows'
    doc_header_height = 0 # e.g. 10
    doc_footer_height = 0 # e.g. 15
    grid_header_height = 0 # e.g. 6.2
    grid_footer_height = 0
    grid_col_headers = None
    grid_col_widths = [0, 0, 0]
    grid_row_height = 5
    copies_per_page = 1
    copy_extra_height = 0
    starting_page_number = 0
    body_attributes = None
    
    def __init__(self, locale='en', encoding='utf-8', templates=None, templateLoader=None, **kwargs):
        self.locale = locale
        self.encoding = encoding
        self.thermo_kwargs = None
        self.thermo_wrapper = None
        if templates:
            self.templates = templates
        if templateLoader:
            self.templateLoader = templateLoader
            
    def init(self, *args, **kwargs):
        """A ``init`` hook method"""
        pass
        
    def outputDocName(self, ext=''):
        """Set the filename extension and return it
        
        :param ext: the filename extension"""
        return 'temp.%s' % ext
        
    def onRecordLoaded(self):
        """Hook method. Allow to define the query to be executed for the :ref:`print`
        
        Example::
        
            def onRecordLoaded(self):
                where = '$date >= :begin_date AND $date <= :end_date AND doctor_id=:d_id'
                columns ='''$doctor,$date,$hour,$patient,$performance,
                            @convention_id.code AS convention_code,
                            $amount,$cost,@invoice_id.number AS invoice'''
                query = self.db.table(self.rows_table).query(columns=columns, where=where, 
                                                             begin_data = self.getData('period.from'),
                                                             end_data = self.getData('period.to'),
                                                             d_id=self.record['id'])
                selection = query.selection()
                if not selection:
                    return False
                self.setData('rows',selection.output('grid'))"""
        pass
        
    def orientation(self):
        """Set the page orientation to 'Landscape' if the :ref:`bagtohtml_page_width` is greater
        than the :ref:`bagtohtml_page_height`, else set the orientation to 'Portrait'"""
        if self.page_width>self.page_height:
            return 'Landscape'
        else:
            return 'Portrait'
            
    def __call__(self, record=None, filepath=None, folder=None, filename=None, hideTemplate=False, rebuild=True,
                 htmlContent=None,page_debug=None, is_draft=None, **kwargs):
        """Return the html corresponding to a given record. The html can be loaded from
        a cached document or created as new if still doesn't exist"""
        if record is None:
            record = Bag()
        self.htmlContent = htmlContent
        self._data = Bag()
        self.is_draft = is_draft
        self.record = record
        self.setData('record', record) #compatibility
        for k, v in kwargs.items():
            self.setData(k, v)
        if not filepath:
            folder = folder or tempfile.mkdtemp()
            filepath = os.path.join(folder, filename or self.outputDocName(ext='html'))
        self.filepath = filepath        
        if not rebuild:
            with open(self.filepath, 'r') as f:
                result = f.read()
            return result
            
        self.templates = kwargs.pop('templates', self.templates)
        self.letterhead_id = kwargs.pop('letterhead_id', self.letterhead_id)
        self.print_button = kwargs.pop('print_button', self.print_button)
        if self.onRecordLoaded() is False:
            return False

        self.showTemplate(hideTemplate is not True)
        self.htmlTemplate = None
        self.prepareTemplates()
        self.page_debug = page_debug or self.page_debug
        self.builder = GnrHtmlBuilder(page_width=self.page_width, page_height=self.page_height,
                                      page_margin_top=self.page_margin_top, page_margin_bottom=self.page_margin_bottom,
                                      page_margin_left=self.page_margin_left, page_margin_right=self.page_margin_right,
                                      page_debug=self.page_debug, print_button=self.print_button,
                                      htmlTemplate=self.htmlTemplate, css_requires=self.get_css_requires(),
                                      showTemplateContent=self.showTemplateContent,parent=self)
        result = self.createHtml(filepath=self.filepath,body_attributes=self.body_attributes)
        return result
        
    def get_css_requires(self):
        """Get the :ref:`"css_requires" webpage variable <css_requires>` in its string format
        and return it as a list"""
        return self.css_requires.split(',')
        
    def prepareTemplates(self):
        """Set the correct value of every measure of the page: height, width, header, footer, margins"""
        top_layer = Bag()
        if not self.htmlTemplate:
            self.htmlTemplate = self.templateLoader(letterhead_id=self.letterhead_id,name=self.templates)
            if self.htmlTemplate:
                top_layer =  self.htmlTemplate['#%i' %(len(self.htmlTemplate)-1)]
        d = self.__dict__
        self.page_height = float(d.get('page_height') or top_layer['main.page.height'] or self.page_height)
        self.page_width = float(d.get('page_width') or top_layer['main.page.width'] or self.page_width)
        self.page_margin_top = float(d.get('page_margin_top') or top_layer['main.page.top'] or self.page_margin_top)
        self.page_margin_left = float(d.get('page_margin_left')or top_layer['main.page.left'] or self.page_margin_left)
        self.page_margin_right = float(d.get('page_margin_right')or top_layer['main.page.right'] or self.page_margin_right)
        self.page_margin_bottom = float(d.get('page_margin_bottom') or top_layer['main.page.bottom'] or self.page_margin_bottom)
        self.page_header_height = float(d.get('page_header_height') or top_layer['layout.top?height'] or self.page_header_height)
        self.page_footer_height = float(d.get('page_footer_height') or top_layer['layout.bottom?height'] or self.page_footer_height)
        self.page_leftbar_width = float(d.get('page_leftbar_width') or top_layer['layout.left?width'] or self.page_leftbar_width)
        self.page_rightbar_width = float(d.get('page_rightbar_width')or top_layer['layout.right?width'] or self.page_rightbar_width)

    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, **kwargs):
        """TODO
        
        :param obj: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param format: TODO
        :param mask: TODO
        :param encoding: the multibyte character encoding you choose"""
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding, **kwargs)
        
    def createHtml(self, filepath=None, body_attributes=None):
        """TODO
        
        :param filepath: the path where html will be saved"""
        #filepath = filepath or self.filepath
        self.initializeBuilder(body_attributes=body_attributes)
        self.main()
        self.builder.toHtml(filepath=filepath)
        return self.builder.html
        
    def showTemplate(self, value):
        """TODO
        
        :param value: TODO"""
        self.showTemplateContent = value
        
    def setTemplates(self, templates):
        """Set a template.
        
        :param templates: TODO"""
        self.templates = templates
        
    def getTemplates(self, templates):
        """TODO
        
        :param templates: TODO"""
        return self.templates

    def initializeBuilder(self, body_attributes=None):
        """TODO"""
        self.builder.initializeSrc(body_attributes=body_attributes)
        self.body = self.builder.body
        self.getNewPage = self.builder.newPage
        self.builder.styleForLayout()

    def getNewPage(self):
        pass

        
    def getData(self, path, default=None):
        """Make a :meth:`getItem() <gnr.core.gnrbag.Bag.getItem>` on data if
        ... TODO
        
        :param path: the path of data (e.g: ``'period.from'``)
        :param default: the default return value for a not found item"""
        wildchars = []
        if path[0] in wildchars:
            value = 'not yet implemented'
        else:
            value = self._data.getItem(path, default)
        return value
        
    def setData(self, path, value, **kwargs):
        """Make a :meth:`setItem() <gnr.core.gnrbag.Bag.setItem>` on data
        
        :param path: the path of data (e.g: ``'period.from'``)
        :param default: the default return value for a not found item"""
        self._data.setItem(path, value, **kwargs)
        
    def onRecordExit(self, recordBag):
        """Hook method.
        
        :param recordBag: a :ref:`bag` that contains the result of the batch"""
        return
        
    def field(self, path, default=None, locale=None,
              format=None, mask=None, root=None, **kwargs):
        """TODO
        
        :param path: TODO
        :param default: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param format: TODO
        :param mask: TODO
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` documentation section"""
        if root is None:
            root = self._data['record']
        attr = {}
        if isinstance(root, Bag):
            datanode = root.getNode(path)
            if datanode:
                value = datanode.value
                attr = datanode.attr
            else:
                value = default
        else:
            value = root.get(path)
        format = format or attr.get('format')
        mask = mask or attr.get('mask')
        if value is None:
            value = default
        elif isinstance(value, Bag) and not format:
            return value
        return self.toText(value, locale, format, mask, self.encoding, **kwargs)
        
    def main(self):
        """It can be overridden"""
        if self.htmlContent:
            page = self.getNewPage()
            page.div("%s::HTML" % self.htmlContent)
        else:
            self.mainLoop()

    def onNewPage(self,page):
        if self.is_draft:
            page.div(style='position:absolute; top:0; left:0; right:0; bottom:0; z-index:10000',_class='document_draft')
            
    def pageCounter(self, mask=None):
        """Allow to automatically number the pages created in a :ref:`print`. You can choose
        the format output with the *mask* parameter
        
        :param mask: format output of the pageCounter method. By default is ``'%s/%s'``
        
                     **Example**: if you print three pages then they will be numbered
                     as `1/3`, `2/3` and `3/3`
                     
                     **Syntax**: You can alternatively set it as ``'%s of %s'``,
                     ``'%s - %s'`` and so on"""
        mask = mask or '%s/%s'
        
        def getPage(currPage=0):
            result = mask % (currPage + 1 + self.starting_page_number,
                             self.copies[self.copy]['currPage'] + 1 + self.starting_page_number)
            return result
            
        return BagCbResolver(getPage, currPage=self.copies[self.copy]['currPage'])
        
    def copyHeight(self):
        """TODO"""
        return (self.page_height - self.page_margin_top - self.page_margin_bottom -\
                self.page_header_height - self.page_footer_height -\
                self.copy_extra_height * (self.copies_per_page - 1)) / self.copies_per_page
                
    def copyWidth(self):
        """TODO"""
        return (self.page_width - self.page_margin_left - self.page_margin_right -\
                self.page_leftbar_width - self.page_rightbar_width)
                
    def mainLoop(self):
        """TODO"""
        self.copies = []
        self.lastPage = False
        self.defineStandardStyles()
        self.defineCustomStyles()
        self.doc_height = self.copyHeight() #- self.page_header_height - self.page_footer_height
        self.grid_height = self.doc_height - self.calcDocHeaderHeight() - self.calcDocFooterHeight()
        self.grid_body_height = float(self.grid_height or 0) - float(self.grid_header_height or 0) - float(self.grid_footer_height or 0)
        for copy in range(self.copies_per_page):
            self.copies.append(dict(grid_body_used=self.grid_height, currPage=-1))
            
        lines = self.getData(self.rows_path)
        if not lines and hasattr(self,'empty_row'):
            lines = Bag()
            lines.setItem('empty',Bag(self.empty_row),**self.empty_row)
        if lines:
            if isinstance(lines, Bag):
                nodes = lines.getNodes()
            elif hasattr(lines, 'next'):
                nodes = list(lines)
            else:
                nodes = lines
            lastNode = nodes[-1] 
            if hasattr(self, 'thermo_wrapper') and self.thermo_kwargs:
                nodes = self.thermo_wrapper(nodes, **self.thermo_kwargs)
            for rowDataNode in nodes:
                self.isLastRow = rowDataNode is lastNode
                self.currRowDataNode = rowDataNode
                for copy in range(self.copies_per_page):
                    self.onNewRow()
                    self.copy = copy
                    rowheight = self.calcRowHeight()
                    availableSpace = self.grid_height - self.copyValue('grid_body_used') -\
                                     self.calcGridHeaderHeight() - self.calcGridFooterHeight()
                    if rowheight > availableSpace:
                        self._newPage()
                    if not self.rowData:
                        continue
                    row = self.copyValue('body_grid').row(height=rowheight)
                    self.copies[self.copy]['grid_body_used'] = self.copyValue('grid_body_used') + rowheight
                    self.currColumn = 0
                    self.currRow = row
                    self.prepareRow(row)
                    
            for copy in range(self.copies_per_page):
                self.copy = copy
                self._closePage(True)

        
    def onNewRow(self):
        pass
                
    def _newPage(self):
        if self.copyValue('currPage') >= 0:
            self._closePage()
        self.copies[self.copy]['currPage'] = self.copyValue('currPage') + 1
        self.copies[self.copy]['grid_body_used'] = 0
        self._createPage()
        self._openPage()
        
    def _get_rowData(self):
        if isinstance(self.currRowDataNode, dict) or isinstance(self.currRowDataNode,Bag):
            return self.currRowDataNode
        elif self.row_mode == 'attribute':
            return self.currRowDataNode.attr
        else:
            return self.currRowDataNode.value
            
    rowData = property(_get_rowData)
    
    def rowField(self, path=None, **kwargs):
        """TODO
        
        :param path: TODO"""
        #if self.row_mode=='attribute':
        #    data = self.currRowDataNode.attr
        #else:
        #    data = self.currRowDataNode.value
        return self.field(path, root=self.rowData, **kwargs)
        
    def rowCell(self, field=None, value=None, default=None, locale=None,
                format=None, mask=None, currency=None,white_space='nowrap', **kwargs):
                
        """Allow to get data from record. You can use it in the :meth:`prepareRow` method
        
        :param field: the name of the table :ref:`column`
        :param value: TODO
        :param default: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param format: the format of the cell (e.g: use ``HH:mm``)
        :param mask: TODO
        :param currency: TODO"""
        
        if field:
            if callable(field):
                value = field()
            else:
                value = self.rowField(field, default=default, locale=locale, format=format,
                                      mask=mask, currency=currency)
        if value is not None:
            #if self.lastPage:
            #    print 'last page'
            #    print self.currColumn
            #    print self.grid_col_widths[self.currColumn]
            value = self.toText(value, locale, format, mask, self.encoding)
            self.currRow.cell(value, width=self.grid_col_widths[self.currColumn], overflow='hidden',
                              white_space=white_space, **kwargs)
        self.currColumn = self.currColumn + 1
        return value

    def _createPage(self):
        curr_copy = self.copies[self.copy]
        if self.copy == 0:
            self.paperPage = self.getNewPage()
            #self.page_header_height = self.page_header_height or getattr(self.builder,'page_header_height')
            #self.page_footer_height = self.page_footer_height or getattr(self.builder,'page_footer_height')

        self.page_layout = self.mainLayout(self.paperPage)
        #if self.page_header_height:
        #    curr_copy['page_header'] = self.page_layout.row(height=self.page_header_height,lbl_height=4,lbl_class='caption').cell()
        if self.calcDocHeaderHeight():
            curr_copy['doc_header'] = self.page_layout.row(height=self.calcDocHeaderHeight(), lbl_height=4,
                                                           lbl_class='caption').cell()
        curr_copy['doc_body'] = self.page_layout.row(height=0, lbl_height=4, lbl_class='caption').cell()
        if self.calcDocFooterHeight():
            curr_copy['doc_footer'] = self.page_layout.row(height=self.doc_footer_height, lbl_height=4,
                                                           lbl_class='caption').cell()
            #if self.page_footer_height:
            #    curr_copy['page_footer'] = self.page_layout.row(height=self.page_footer_height,lbl_height=4,lbl_class='caption').cell()
            
    def mainLayout(self, page):
        """Hook method that must be overridden. It gives the :ref:`print_layout_page`
        object to which you have to append a :meth:`layout <gnr.core.gnrhtml.GnrHtmlSrc.layout>`
        
        :param page: the page object"""
        print 'mainLayout must be overridden'
        
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
        if self.calcDocFooterHeight():
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
        """Hook method. MANDATORY if you define a :ref:`print_layout_grid` in
        your :ref:`print`. Through this method you receive the center of the page and you can
        define the layout of the grid
        
        :param grid: the :ref:`print_layout_grid`"""
        print 'gridLayout must be overridden'
        
    def gridHeader(self, row):
        """It can be overridden
        
        :param row: the grid row"""
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
        """It can be overridden
        
        :param row: the grid row"""
        return
        
    def fillBodyGrid(self):
        """TODO"""
        row = self.copyValue('body_grid').row()
        for w in self.grid_col_widths:
            row.cell(width=w)
            
    def copyValue(self, valuename):
        """TODO
        
        :param valuename: the name of the value to copy"""
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

    def calcDocFooterHeight(self):
        """override for special needs"""
        return self.doc_footer_height
        
    def defineCustomStyles(self):
        """override this for custom styles"""
        pass
        
    def docFooter(self, footer, lastPage=None):
        """Hook method. Define the footer of the :ref:`print_layout_doc` in the :ref:`print_layout`
        
        :param footer: the footer object
        :param lastPage: boolean. More information in the :ref:`lastpage` section
        
        .. note:: the method is called only if the :ref:`bagtohtml_doc_footer_height`
                  has a value different from ``0``"""
        pass
        
    def pageFooter(self, footer, lastPage=None):
        """Hook method. Define the footer of the :ref:`print_layout_page` in the :ref:`print_layout`
        
        :param footer: the footer object
        :param lastPage: boolean. More information in the :ref:`lastpage` section
        
        .. note:: the method is called only if the :ref:`bagtohtml_page_footer_height`
                  has a value different from ``0``"""
        pass
        
    def pageHeader(self, header):
        """Hook method. Define the header of the :ref:`print_layout_page` in the :ref:`print_layout`
        
        :param header: the header object
        
        .. note:: the method is called only if the :ref:`bagtohtml_page_header_height`
                  has a value different from ``0``"""
        pass
        
    def docHeader(self, header):
        """Hook method. Define the header of the :ref:`print_layout_doc` in the :ref:`print_layout`
        
        :param header: the header object
        
        The docHeader() method allows to receive an object called header to which you
        can append a layout structure made by :meth:`layouts <gnr.core.gnrhtml.GnrHtmlSrc.layout>`,
        :meth:`rows <gnr.core.gnrhtml.GnrHtmlSrc.row>`, and :meth:`cells <gnr.core.gnrhtml.GnrHtmlSrc.cell>`
        
        .. note:: the method is called only if the :ref:`bagtohtml_doc_header_height`
                  has a value different from ``0``"""
        pass
        
    def defineStandardStyles(self):
        """TODO"""
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
                            margin-right:1.5mm;
                        }
                        .aligned_left{
                            text-align:left;
                            margin-left:1.5mm;
                        }
                        .aligned_center{
                            text-align:center;
                        }
                         """)