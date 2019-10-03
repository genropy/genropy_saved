#!/usr/bin/env python
# encoding: utf-8
#
# gnrbaghtml.py
#
# Created by Francesco Porcari on 2010-10-16.
# Copyright (c) 2011 Softwell. All rights reserved.

import os
from gnr.core.gnrstring import toText,templateReplace

from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrbag import Bag, BagCbResolver
from gnr.core.gnrclasses import GnrClassCatalog
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrstring import flatten
from gnr.core.gnrnumber import decimalRound
from collections import defaultdict
import tempfile

try:
    from simpleeval import simple_eval
except ImportError:
    simple_eval = False

class BagToHtml(object):
    """A class that transforms a :ref:`bag` into HTML. It can be used to make a :ref:`print`"""
    css_requires = ''
    templates = ''
    letterhead_id = ''
    letterhead_sourcedata = None
    currencyFormat = u'#,###.00'
    encoding = 'utf-8'
    page_debug = False
    page_format = 'A4'
    page_height = None
    page_width = None
    page_orientation = 'V'
    page_margin_top = 0
    page_margin_left = 0
    page_margin_right = 0
    page_margin_bottom = 0
    page_header_height = 0
    page_footer_height = 0
    page_leftbar_width = 0
    page_rightbar_width = 0
    print_button = None
    row_table = None
    row_struct= None
    row_mode = 'value'
    rows_path = 'rows'
    doc_header_height = 0 # e.g. 10
    doc_footer_height = 0 # e.g. 15
    grid_header_height = 0 # e.g. 6.2
    grid_footer_height = 0
    grid_body_adjustment = 0
    grid_col_headers = None
    grid_col_headers_height = 4
    grid_col_widths = None
    grid_style_cell = None
    grid_columns =  []
    grid_columnsets = {}
    grid_row_height = 5
    renderMode = None
    totalize_carry = False
    totalize_footer = False
    totalize_mode = 'doc' #doc,page
    copies_per_page = 1
    copy_extra_height = 0
    copy = 0
    sheet = 0
    starting_page_number = 0
    body_attributes = None
    sheets_counter = 1
    splittedPages = 0
    watermark_draft_class = 'document_draft'

    @property
    def currentPageFormat(self):
        return getattr(self,'format_%s' %self.page_format)()

    def format_A4(self):
        return dict(height=280,width=200)

    @property
    def paperHeight(self):
        return self.page_height or self.currentPageFormat['height']

    @property
    def paperWidth(self):
        return self.page_width or self.currentPageFormat['width']

    def defaultKwargs(self):
        return dict(border_color = '#e0e0e0',border_width = .3)

    def __init__(self, locale='en', encoding='utf-8', templates=None, templateLoader=None, **kwargs):
        self.locale = locale
        self.encoding = encoding
        self.thermo_kwargs = None
        self.thermo_wrapper = None
        self.currentGrid = None
        self.catalog = GnrClassCatalog() 
        if templates:
            self.templates = templates
        if templateLoader:
            self.templateLoader = templateLoader
    
    def adaptGridColumns(self):
        self.grid_columns = self.grid_columns or [] 
        if self.grid_col_widths:
            self.grid_columns = []
            headers = self.grid_col_headers or ''
            if ':' in headers:
                headers, headers_height = self.grid_col_headers.split(':')
                self.grid_col_headers_height = int(headers_height)
            grid_col_headers = headers.split(',') if headers else []
            len_headers_fill = len(self.grid_col_widths) - len(grid_col_headers)
            if len_headers_fill>0:
                grid_col_headers += (['']*len_headers_fill)
            for i,mm_width in enumerate(self.grid_col_widths):
                name = grid_col_headers[i]
                header_style = None
                if name=='|':
                    name = ''
                    header_style = 'border-top:0mm;border-bottom:0mm;'
                self.grid_columns.append(dict(mm_width=mm_width,name=name,header_style=header_style))

    def init(self, *args, **kwargs):
        """A ``init`` hook method"""
        pass
        
    def outputDocName(self, ext=''):
        """Set the filename extension and return it
        
        :param ext: the filename extension"""
        return 'temp.%s' % ext
        
    def onRecordLoaded(self):
        """Hook method."""
        pass
        


    def orientation(self):
        """Set the page orientation to 'Landscape' if the :ref:`bagtohtml_page_width` is greater
        than the :ref:`bagtohtml_page_height`, else set the orientation to 'Portrait'"""
        if self.page_width>self.page_height:
            return 'Landscape'
        else:
            return 'Portrait'
            
    def __call__(self, record=None, filepath=None, folder=None, filename=None, hideTemplate=False, rebuild=True,
                 htmlContent=None,page_debug=None, is_draft=None,orientation=None, **kwargs):
        """Return the html corresponding to a given record. The html can be loaded from
        a cached document or created as new if still doesn't exist"""
        if record is None:
            record = Bag()
        self.htmlContent = htmlContent
        self._data = Bag()
        self._gridsColumnsBag = Bag()
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
        self.page_orientation = orientation or self.page_orientation
        self.print_button = kwargs.pop('print_button', self.print_button)
        self.grid_prev_running_totals = defaultdict(int)
        self.grid_running_totals = defaultdict(int)
        if self.onRecordLoaded() is False:
            return False
        if self.splittedPages:
            self.pages_folder = os.path.splitext(self.filepath)[0]
        self.showTemplate(hideTemplate is not True)
        self.htmlTemplate = None
        self.prepareTemplates()
        self.page_debug = page_debug or self.page_debug
        self.newBuilder()
        result = self.createHtml(filepath=self.filepath,body_attributes=self.body_attributes)
        return result

    def newBuilder(self):
        self.builder = GnrHtmlBuilder(page_width=self.page_width, page_height=self.page_height,
                                    page_margin_top=self.page_margin_top, page_margin_bottom=self.page_margin_bottom,
                                    page_margin_left=self.page_margin_left, page_margin_right=self.page_margin_right,
                                    page_debug=self.page_debug, print_button=self.print_button,
                                    htmlTemplate=self.htmlTemplate, css_requires=self.get_css_requires(),
                                    showTemplateContent=self.showTemplateContent,default_kwargs=self.defaultKwargs(),parent=self)
        self.builder.initializeSrc(body_attributes=self.body_attributes)
        self.builder.styleForLayout()

    @property
    def body(self):
        return self.builder.body

    def get_css_requires(self):
        """Get the :ref:`"css_requires" webpage variable <css_requires>` in its string format
        and return it as a list"""
        return self.css_requires.split(',')

    def fillLetterheadSourceData(self,node,**kwargs):
        if node.label=='html':
            node.value = templateReplace(node.value,self.letterhead_sourcedata or self.record)
        
    def prepareTemplates(self):
        """Set the correct value of every measure of the page: height, width, header, footer, margins"""
        top_layer = Bag()
        if not self.htmlTemplate:
            self.htmlTemplate = self.templateLoader(letterhead_id=self.letterhead_id,name=self.templates)
            if self.htmlTemplate:
                self.htmlTemplate.walk(self.fillLetterheadSourceData)
                top_layer =  self.htmlTemplate['#%i' %(len(self.htmlTemplate)-1)]
        d = self.__dict__
        paper_height = float(d.get('page_height') or top_layer['main.page.height'] or self.paperHeight)
        paper_width = float(d.get('page_width') or top_layer['main.page.width'] or self.paperWidth)
        if self.page_orientation=='V': 
            self.page_height = paper_height
            self.page_width = paper_width
        else:
            self.page_width = paper_height
            self.page_height = paper_width
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
        self.main()
        if not self.splittedPages:
            self.builder.toHtml(filepath=filepath)
            return self.builder.html
        else:
            pages = [os.path.join(self.pages_folder,p) for p in sorted(os.listdir(self.pages_folder))]
            self.builder = None
            return pages
        
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

    def getNewPage(self):
        return self.builder.newPage()
        
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
        
        self.adaptGridColumns()
        if self.htmlContent:
            page = self.getNewPage()
            page.div("%s::HTML" % self.htmlContent)
        else:
            self.mainLoop()

    def getWatermarkClass(self):
        if self.is_draft:
            return self.watermark_draft_class

    def onNewPage(self,page):
        watermark_class = self.getWatermarkClass()
        if watermark_class:
            page.div(style='position:absolute; top:0; left:0; right:0; bottom:0; z-index:10000',_class=watermark_class)

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
            t = (currPage + 1 + self.starting_page_number,
                             self.current_page_number + 1 + self.starting_page_number)
            if len(mask)-len(mask.replace(r'%s',''))>2:
                result = mask % t
            else:
                result = mask % t[0]
            return result
            
        return BagCbResolver(getPage, currPage=self.current_page_number)

    @property
    def current_page_number(self):
        return self.copies[self.copykey]['currPage']
    
    def gridColumnsInfo(self):
        return dict(columns=self.grid_columns,columnsets=self.grid_columnsets)


    @property
    def columnsBag(self):
        gridName = self.currentGrid or '_main_'
        if gridName not in self._gridsColumnsBag:
            self._gridsColumnsBag[gridName] = self._gridSheetsBag(gridName)
        result = self._gridsColumnsBag[gridName][self._sheetKey(self.sheet)]['columns']
        return result

    def _gridSheetsBag(self,gridName):
        result = Bag()
        info = self.gridColumnsInfo()
        columns = info['columns']
        columnsets = info['columnsets']
        for s in range(self.sheets_counter):
            sheet_columnsBag = Bag()
            sheet_columnsets = {}
            filtertuple = ('*',s)
            for i,col in enumerate(columns):
                if col.get('sheet','*') in filtertuple:
                    sheet_columnsBag.addItem('col_%02i' %i,None,_attributes=col)
            for key,colset in columnsets.items():
                if colset.get('sheet','*') in filtertuple:
                    sheet_columnsets[key] = colset
            result[self._sheetKey(s)] = Bag(dict(columns=sheet_columnsBag,columnsets=sheet_columnsets))
        return result
    
    @property
    def columnsets(self):
        gridName = self.currentGrid or '_main_'
        if gridName in self._gridsColumnsBag:
            return self._gridsColumnsBag[gridName][self._sheetKey(self.sheet)]['columnsets']
    
    def _sheetKey(self,sheetNumber):
        return 's_%02i' %sheetNumber


    def copyHeight(self):
        """TODO"""
        return (self.page_height - self.page_margin_top - self.page_margin_bottom -\
                self.page_header_height - self.page_footer_height -\
                self.copy_extra_height * (self.copies_per_page - 1)) / self.copies_per_page
                
    def copyWidth(self):
        """TODO"""
        return (self.page_width - self.page_margin_left - self.page_margin_right -\
                self.page_leftbar_width - self.page_rightbar_width)
                
    def lineIterator(self,nodes):
        lastNode = nodes[-1] 
        for lineno,rowDataNode in enumerate(nodes):
            self.lineno = lineno
            self.isLastRow = rowDataNode is lastNode
            self.prevDataNode = self.currRowDataNode
            self.currRowDataNode = rowDataNode
            extra_row_height = self.onNewRow() or 0
            row_kw = self.getRowAttrsFromData()
            self.updateRunningTotals(rowData=self.rowData)
            rowheight = row_kw.pop('height',None) or self.calcRowHeight()
            for copy in range(self.copies_per_page):
                self.copy = copy
                yield (lineno,rowDataNode,rowheight,row_kw,extra_row_height)
        self.updateRunningTotals(rowData=None)


    def mainLoop(self):
        """TODO"""
        self._paperPages = {}
        self.copy = 0
        self.sheet = 0
        self.lastPage = False
        self.defineStandardStyles()
        self.defineCustomStyles()
        self.currGrid= None
        if self.getData(self.rows_path) is None:
            self.setData(self.rows_path,self.gridData())
        lines = self.getData(self.rows_path)
        if not lines and hasattr(self,'empty_row'):
            lines = Bag()
            lines.setItem('empty',Bag(self.empty_row),**self.empty_row)
        if not lines:
            return
        self.currRowDataNode = None
        if isinstance(lines, Bag):
            nodes = lines.getNodes()
        elif hasattr(lines, 'next'):
            nodes = list(lines)
        else:
            nodes = lines
        if hasattr(self, 'thermo_wrapper') and self.thermo_kwargs:
            nodes = self.thermo_wrapper(nodes, **self.thermo_kwargs)
        carry_height = self.totalizeCarryHeight()

        for lineno,rowDataNode,rowheight,row_kw,extra_row_height in self.lineIterator(nodes):
            bodyUsed = self.copyValue('grid_body_used')

            gridNetHeight = self.grid_height - self.calcGridHeaderHeight() - self.calcGridFooterHeight() -\
                            carry_height - self.totalizeFooterHeight() - self.grid_row_height
            availableSpace = gridNetHeight-bodyUsed-self.grid_body_adjustment
            doNewPage =  (rowheight+extra_row_height) > availableSpace
            if doNewPage:
                carry_height = self.totalizeCarryHeight()
            for sheet in range(self.sheets_counter):
                self.sheet = sheet
                if doNewPage:
                    self._newPage()
                if not self.rowData:
                    continue
                row = self.copyValue('body_grid').row(height=rowheight, **row_kw)
                self.copies[self.copykey]['grid_body_used'] = self.copyValue('grid_body_used') + rowheight+extra_row_height
                self.currColumn = 0
                self.currRow = row
                self.prepareRow(row)
                
        for copy in range(self.copies_per_page):
            self.copy = copy
            for sheet in range(self.sheets_counter):
                self.sheet = sheet
                self._closePage(True)
        
    def getRowAttrsFromData(self):
        return dictExtract(self.rowData,'row_')

    def gridData(self):
        pass
    
    def onNewRow(self):
        pass

    def runningTotalsDefaults(self):
        result = dict()
        lastspanfield = None
        self._caption_column = None
        for col in self.columnsBag:
            colattr = col.attr
            field = flatten(colattr.get('field'))
            if colattr.get('totalize'):
                lastspanfield = None
            else:
                if not lastspanfield:
                    lastspanfield = field
                    self._caption_column = self._caption_column or field
                    result['%s_colspan' %field] = 0
                else:
                    result['%s_colspan' %lastspanfield] +=1
        return result
    
    def gridRunningTotals(self,lastPage=None):
        rowData = self.runningTotalsDefaults()
        rowData.update(self.grid_prev_running_totals)
        captions_kw = getattr(self,'totalize_%s' %self.renderMode,None) if self.renderMode else {}
        if captions_kw is True:
            captions_kw = dict()
        elif isinstance(captions_kw,basestring):
            captions_kw = dict(caption=captions_kw,content_class='totalize_caption')
        elif isinstance(captions_kw,dict):
            captions_kw = dict(captions_kw)
        else:
            captions_kw = None
        sheetTotalizers = filter(lambda t: t, [tot for tot in self.columnsBag.digest('#a.totalize')])
        if captions_kw and sheetTotalizers:
            caption = captions_kw.pop('caption')
            rowData[self._caption_column] = caption
            for k,v in captions_kw.items():
                rowData['%s_%s' %(self._caption_column,k)] = v
        self.onRunningTotals(rowData=rowData,lastPage=lastPage)
        return rowData
    
    def onRunningTotals(self,rowData=None,lastPage=None):
        pass

    def _newPage(self):
        if self.copyValue('currPage') >= 0:
            self._closePage()
        self.copies[self.copykey]['currPage'] = self.copyValue('currPage') + 1
        self.copies[self.copykey]['grid_body_used'] = 0
        self._createPage()
        self._openPage()

    def customizedRowData(self,rowData):
        return rowData


    def _rowDataCustomized(self,rowDataNode):
        if not rowDataNode:
            return dict()
        if isinstance(rowDataNode, dict) or isinstance(rowDataNode,Bag):
            rowData = rowDataNode
        elif self.row_mode == 'attribute':
            rowData = rowDataNode.attr
        else:
            rowData = rowDataNode.value
        return self.customizedRowData(rowData)

    @property
    def rowData(self):
        return self._rowDataCustomized(self.currRowDataNode)
            
    @property
    def previousRowData(self):
        return self._rowDataCustomized(self.prevDataNode)
    
    def rowField(self, path=None, **kwargs):
        """TODO
        
        :param path: TODO"""
        #if self.row_mode=='attribute':
        #    data = self.currRowDataNode.attr
        #else:
        #    data = self.currRowDataNode.value
        return self.field(path, root=self.rowData, **kwargs)


    def getCellStyle(self,style):
        stylelist = style.split(';') if style else []
        return ';'.join(self.grid_style_cell_list+stylelist)
    
    @property
    def grid_style_cell_list(self):
        if not hasattr(self,'_grid_style_cell_list'):
            self._grid_style_cell_list = self.grid_style_cell.split(';') if self.grid_style_cell else []
        return self._grid_style_cell_list 

    def prepareRow(self,row):
        #overridable
        self.fillGridRow()
    
    
    def fillGridRow(self):
        rowData = self.rowData
        self.renderMode = None
        self.renderGridRow(rowData=rowData)
    
    fillRow = fillGridRow

    def renderGridRow(self,rowData=None):
        self._currSpanCell = None
        for colNode in self.columnsBag:
            self.renderGridCell(col=colNode.attr,rowData=rowData)
        
    def renderGridCell(self,col=None,rowData=None,parentRow=None):
        pars = self.getGridCellPars(col,rowData)
        if pars.get('hidden'):
            return
        colspan = pars.pop('colspan',1)
        mm_width = pars.pop('mm_width',0)
        parentRow = parentRow or self.currRow
        if self._currSpanCell:
            if mm_width==0:
                curr_total_width = self._currSpanCell.attributes['extra_width'] + self._currSpanCell.width
                self._currSpanCell.attributes['extra_width'] = curr_total_width
                self._currSpanCell.width = 0
            else:
                self._currSpanCell.attributes['extra_width'] += mm_width
            self._currSpanCell.attributes['colspan_count'] -= 1
            if not self._currSpanCell.attributes['colspan_count']: 
                self._currSpanCell = None
            return
        value = self.getGridCellValue(col,rowData)
        content_class = pars.pop('content_class',None)
        align_class = pars.pop('align_class',None)
        align_class = align_class or self._guessAlign(value=value)
        content_class = '%s %s' %(content_class,align_class) if content_class else align_class
        locale = pars.pop('locale',None) or self.locale
        format = pars.pop('format',None)
        mask = pars.pop('mask',None)
        currency = pars.pop('currency',None)
        white_space = pars.pop('white_space',None) or 'nowrap'
        value = self.toText(value, locale, format, mask, self.encoding, currency=currency)
        cell = parentRow.cell(value, width=mm_width,overflow='hidden',
                            white_space=white_space,
                            content_class=content_class, **pars)
        if colspan>1:
            self._currSpanCell = cell
            cell.attributes['extra_width'] = 0
            cell.attributes['colspan_count'] = colspan

    def getGridCellPars(self,col=None,rowData=None):
        rowData = rowData or dict()
        if isinstance(col,int):
            col = self.columnsBag.getAttr('#%i' %col)
        field = col['field']
        columnset = col.get('columnset')
        result = dict()
        if columnset and self.columnsets:
            result.update(dictExtract(self.columnsets[columnset],'cells_'))
        result.update(col)
        anycell_kw = rowData.get('anycell_kw') or dict()
        result.update(anycell_kw)
        flattenkey = flatten(field)
        extra_kw = rowData.get('%s_kw' %flattenkey) or dict()
        extra_kw.update(dictExtract(rowData,'%s_' %flattenkey))
    
        extra_kw.update(dictExtract(rowData,'%s_kw_' %field))
        result.update(extra_kw)
        return result
    
    def cellFormulaValue(self,col=None,rowData=None):
        if not simple_eval:
            return
        variables = dict()
        for k,v in rowData.items():
            variables[k] = v
        variables['previousRowData'] = self.previousRowData
        variables['grid_running_totals'] = dict(self.grid_running_totals)
        
        variables['record'] = self.record

        formula = col['formula']
        if formula.startswith('+=') or formula.startswith('%='):
            mainField = flatten(formula[2:].strip())
            if formula.startswith('+='):
                prevValue = self.previousRowData.get(col['field'],self.grid_prev_running_totals[mainField])
                result = prevValue + rowData[mainField]
            else:
                variables['mainFieldTotal'] = self.getColTotal(mainField)
                formula = '(%s or 0)/mainFieldTotal*100' %mainField
                result = simple_eval(formula,names=variables)
        else:
            result = simple_eval(col['formula'],names=variables)
        return result 

    def getColTotal(self,field):
        field = flatten(field)
        colsTotals = self.getData('colsTotals') or Bag()
        if field in colsTotals:
            return colsTotals[field]
        colsTotals[field] = self.getData(self.rows_path).sum('#a.%s' %field) or 0
        self.setData('colsTotals',colsTotals)
        return colsTotals[field]

    def getGridCellValue(self,col=None,rowData=None):
        if isinstance(col,int):
            col = self.columnsBag.getAttr('#%i' %col)
        field = col['field']
        field_getter = col.get('field_getter')
        
        if not self.renderMode:
            if field=='_linenumber':
                rowData[field] = self.lineno+1
            elif callable(field_getter):
                rowData[field] = field_getter(rowData=rowData,col=field)
            elif col.get('formula'):
                rowData[field_getter or field] = self.cellFormulaValue(col,rowData)  
        if field_getter and not field_getter in rowData:
            field_getter = None
        return rowData.get(field_getter or field)
        
    def rowCell(self, field=None, value=None, default=None, locale=None,
                format=None, mask=None, currency=None,white_space='nowrap',align_class=None,
                content_class=None, totalize=None,**kwargs):
                
        """Allow to get data from record. You can use it in the :meth:`prepareRow` method
        
        :param field: the name of the table :ref:`column`
        :param value: TODO
        :param default: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param format: the format of the cell (e.g: use ``HH:mm``)
        :param mask: TODO
        :param currency: TODO"""
        colNode = self.columnsBag.nodes[self.currColumn]
        curr_attr = colNode.attr
        self.currColumn = self.currColumn + 1
        if curr_attr.get('hidden'):
            return
        if field:
            if callable(field):
                value = field()
            else:
                value = self.rowField(field, default=default, locale=locale, format=format,
                                      mask=mask, currency=currency)
        content_class = '%s %s' %(content_class,align_class) if content_class else align_class or self._guessAlign(value=value)
        value = self.toText(value, locale, format, mask, self.encoding, currency=currency)
        self.currRow.cell(value, width=curr_attr['mm_width'],overflow='hidden',
                            white_space=white_space,content_class=content_class, **kwargs)
        return value
    
    def _guessAlign(self,value=None,dtype=None):
        if not dtype:
            dtype = self.catalog.getType(value)
        return 'aligned_right' if dtype in ['N','L','R','F'] else 'aligned_left'

    def _createPage(self):
        curr_copy = self.copies[self.copykey]
        if self.copy == 0:
            self.paperPage = self.getNewPage()
            #self.page_header_height = self.page_header_height or getattr(self.builder,'page_header_height')
            #self.page_footer_height = self.page_footer_height or getattr(self.builder,'page_footer_height')

        page_layout = self.mainLayout(self.paperPage)
        #if self.page_header_height:
        #    curr_copy['page_header'] = self.page_layout.row(height=self.page_header_height,lbl_height=4,lbl_class='caption').cell()
        if self.calcDocHeaderHeight():
            curr_copy['doc_header'] = page_layout.row(height=self.calcDocHeaderHeight(), lbl_height=4,
                                                           lbl_class='caption').cell()
        curr_copy['doc_body'] = page_layout.row(height=0, lbl_height=4, lbl_class='caption').cell()
        if self.calcDocFooterHeight():
            curr_copy['doc_footer'] = page_layout.row(height=self.calcDocFooterHeight(), lbl_height=4,
                                                           lbl_class='caption').cell()
            #if self.page_footer_height:
            #    curr_copy['page_footer'] = self.page_layout.row(height=self.page_footer_height,lbl_height=4,lbl_class='caption').cell()

    def _get_paperPage(self):
        return self._paperPages[self.sheet]
       
    def _set_paperPage(self, paperPage):
        self._paperPages[self.sheet] = paperPage

    paperPage = property(_get_paperPage, _set_paperPage)

    def mainLayout(self, page):
        """Hook method that could be overridden. It gives the :ref:`print_layout_page`
        object to which you have to append a :meth:`layout <gnr.core.gnrhtml.GnrHtmlSrc.layout>`
        :param page: the page object"""
        return page.layout(**self.mainLayoutParamiters())
    
    def mainLayoutParamiters(self):
        return dict(font_family='Arial Narrow',font_size='11pt',
                    name='mainLayout',top=1,left=1,right=1,bottom=1,border_width=0)
        
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
        totalizeFooterHeight = self.totalizeFooterHeight()
        if totalizeFooterHeight:
            row = self.copyValue('body_grid').row(height=totalizeFooterHeight, _class='totalizer_row totalizer_footer')
            self.currColumn = 0
            self.currRow = row
            self.renderMode = 'footer'
            self.renderGridRow(self.gridRunningTotals(lastPage=lastPage))
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
        if self.splittedPages:
            currPage = self.current_page_number +1
            if lastPage or currPage % self.splittedPages == 0:
                pages_path = os.path.join(self.pages_folder,'pages_%04i.html'%currPage)
                self.builder.toHtml(filepath=pages_path)
                self.newBuilder()


    def _docBody(self, body):
        header_height = self.calcGridHeaderHeight()
        wrapper = body
        if self.columnsets:
            header_height = header_height/2
            extlayout = body.layout(border_width=0,top=0,left=0,right=0,bottom=0)
            gp = self.gridLayoutParameters()
            colsetlayout = extlayout.row(height=header_height).cell().layout(left=gp.get('left'),right=gp.get('right'),top=0,bottom=0,
                                                border_width=.3,border_color='transparent')
            self.prepareColumnsets(colsetlayout.row())
            wrapper = extlayout.row().cell()
        grid = self.gridLayout(wrapper)
        if header_height:    
            self.gridHeader(grid.row(height=header_height))
        totalizeCarryHeight = self.totalizeCarryHeight()
        if totalizeCarryHeight:
            row = grid.row(height=totalizeCarryHeight, _class='totalizer_row totalizer_carry')
            self.currColumn = 0
            self.currRow = row
            self.renderMode = 'carry'
            self.renderGridRow(self.gridRunningTotals(lastPage=self.lastPage))
        self.copies[self.copykey]['body_grid'] = grid
    
    def prepareColumnsets(self,row):
        currentColsetCell = None
        for colNode in self.columnsBag:
            pars = colNode.attr
            if pars.get('hidden'):
                continue
            if not pars.get('columnset'):
                row.cell(width=pars.get('mm_width'))
                currentColsetCell = None
            elif currentColsetCell is not None and pars['columnset'] == currentColsetCell.columnset:
                if currentColsetCell.width:
                    if pars.get('mm_width'):
                        currentColsetCell.width += (pars.get('mm_width')+.3)
                    else:
                        currentColsetCell.attributes['extra_width'] = currentColsetCell.width
                        currentColsetCell.width = 0
                else:
                    currentColsetCell.attributes['extra_width'] = currentColsetCell.attributes.get('extra_width') or 0
                    currentColsetCell.attributes['extra_width']+=pars.get('mm_width')+.3
            else:
                colsetattr = dict(self.columnsets[pars['columnset']])
                colsetattr.pop('tag',None)
                colsetattr.pop('code',None)
                name = colsetattr.pop('name','')
                currentColsetCell = row.cell(self.toText(name), 
                                            width=pars.get('mm_width'),
                                            _class=colsetattr.pop('_class',None) or 'gnrcolumnset',
                                            **colsetattr)
                currentColsetCell.columnset = pars['columnset']
        
    def gridLayout(self, body):
        """Hook method. if you define a :ref:`print_layout_grid` in
        your :ref:`print`. Through this method you receive the center of the page and you can
        define the layout of the grid
        
        :param grid: the :ref:`print_layout_grid`"""
        return body.layout(**self.gridLayoutParameters())  

    def gridLayoutParameters(self):
        return dict(name='gridLayout',um='mm',border_color='#e0e0e0',
                            top=.1,bottom=.1,left=.1,right=.1,
                            font_size='9pt',
                            border_width=.3,lbl_class='caption',
                            text_align='left')
 
    def gridHeader(self, row):
        """It can be overridden
        
        :param row: the grid row"""
        lbl_height = self.grid_col_headers_height
        for colNode in self.columnsBag:
            pars = colNode.attr
            if pars.get('hidden'):
                continue
            row.cell(lbl=self.toText(pars.get('name','')), lbl_height=lbl_height, width=pars.get('mm_width'), style=pars.get('header_style'))
            
    def gridFooter(self, row):
        """It can be overridden
        
        :param row: the grid row"""
        return

    @property
    def totalizingColumns(self):
        if not hasattr(self,'_totalizingColumns'):
            self._totalizingColumns = [col for col in self.gridColumnsInfo()['columns'] if col.get('totalize')]
        return self._totalizingColumns

    def updateRunningTotals(self,rowData):
        self.grid_prev_running_totals = dict(self.grid_running_totals)
        if not rowData:
            return
        for col in self.totalizingColumns:
            self.grid_running_totals[col.get('field_getter') or col['field']] += (self.getGridCellValue(col,rowData) or 0)

    def totalizeFooterHeight(self):
        if not (self.totalizingColumns and self.totalize_footer):
            return 0
        if self.totalize_mode == 'page' or self.isLastRow or self.lastPage:
            return self.grid_row_height
        return 0

    def totalizeCarryHeight(self):
        if not self.totalizingColumns:
            return 0
        firstPage = self.current_page_number == 0
        if self.totalize_carry and self.grid_prev_running_totals:
            if self.totalize_mode == 'page' or firstPage:
                return self.grid_row_height
        return 0


    def fillBodyGrid(self):
        """TODO"""
        row = self.copyValue('body_grid').row()
        for colNode in self.columnsBag:
            pars = colNode.attr
            if pars.get('hidden'):
                continue
            row.cell(width=pars.get('mm_width'))
            
    def copyValue(self, valuename):
        """TODO
        
        :param valuename: the name of the value to copy"""
        return self.copies[self.copykey][valuename]

    @property
    def grid_height(self):
        if not hasattr(self,'_grid_height'):
            self._grid_height = self.copyHeight() - self.calcDocHeaderHeight() - self.calcDocFooterHeight()
        return self._grid_height

    @property
    def copies(self):
        if not hasattr(self,'_copies'):
            self._copies = {}
            for copy in range(self.copies_per_page):
                for sheet in range(self.sheets_counter):
                    self._copies['%02i_%02i' %(sheet,copy)] = dict(grid_body_used=self.grid_height, currPage=-1)
        return self._copies

    @property
    def copykey(self):
        return '%02i_%02i' %(self.sheet,self.copy)
        
    def calcRowHeight(self):
        """override for special needs"""
        return self.grid_row_height
        
    def calcGridHeaderHeight(self):
        """override for special needs"""
        result = self.grid_header_height
        if self.columnsets:
            return result*2
        return result
        
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
                        .gnrcolumnset{
                            text-align:center;
                            background:#888; 
                            color:white;
                            border-bottom-width:0;
                            font-size:8pt;
                            border-top-left-radius:2mm;
                            border-top-right-radius:2mm;
                        }
                        .totalizer_row{
                            background:whitesmoke;
                            color:#444;
                        }
                        .totalize_caption{
                            text-align:right;
                            padding-right:2mm;
                            font-weight: normal;
                            font-style:italic;
                        }

                         """)