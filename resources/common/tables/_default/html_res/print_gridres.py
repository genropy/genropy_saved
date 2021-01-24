#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import math

from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrnumber import decimalRound
from gnr.core.gnrlang import position



from gnr.core.gnrbag import Bag

class Main(TableScriptToHtml):
    page_header_height = 0 #topHeight
    page_footer_height = 0
    doc_header_height = 10 #headerHeight
    page_width = 292    #da utilizzare per letterhead che poi sovrascrive
    page_height = 198   #da utilizzare per letterhead che poi sovrascrive
    doc_footer_height = 0 #footerHeight
    grid_footer_height = 0 
    grid_header_height = 4.3
    grid_col_widths=[0] #rowColWidth
    grid_row_height=5
    html_folder = 'page:preview_html'
    pdf_folder = 'page:preview_pdf'

    def onRecordLoaded(self):
        self.row_table = self.row_table or self.tblobj.fullname
        userObjectIdOrCode = self.parameter('userobject') #userobject si trova in extra_parameters
        struct = self.parameter('currentGridStruct')
        printParams = self.parameter('printParams') or Bag()
        letterhead_id = printParams['letterhead_id']
        currentQuery = self.parameter('currentQuery')

        if userObjectIdOrCode: #Non è chiaro quando dovrebbe attivarsi questo caso.
            data,metadata = self.page.db.table('adm.userobject'
                                ).loadUserObject(userObjectIdOrCode=userObjectIdOrCode,
                                                table=self.tblobj.fullname,objtype='gridprint')
            if struct is None:
                struct =  data.getItem('struct')
            currentQuery = currentQuery or data.getItem('query')
            printParams = printParams or data.getItem('printParams') or Bag()
            printParams['print_title'] = printParams['print_title'] or metadata.get('description')
            self.row_table = metadata.get('tbl') or self.row_table
            letterhead_id = letterhead_id or data['letterhead_id']

        self.letterhead_id = letterhead_id
        self.setData('currentQuery',currentQuery)
        totalize_mode = printParams['totalize_mode']
        totalize_footer = printParams['totalize_footer']
        totalize_carry =  printParams['totalize_carry']
        self.cell_characters_limit = {}
        if totalize_mode or totalize_footer or totalize_carry:
            self.totalize_mode = totalize_mode or 'doc'
            self.totalize_footer = totalize_footer or True
            self.totalize_carry = totalize_carry
        self.page_orientation = printParams['orientation']
        self.setStruct(struct)
        print_title = printParams['print_title'] or 'Untitled'
        self.setData('print_title',print_title)

    def gridColumnsInfo(self):
        struct = self.getStruct()
        tot_width = decimalRound(self.page_width-self.page_margin_left -self.page_margin_right-2)
        cells = struct['#0.#0'].digest('#a')
        max_width_cell = sorted(cells,key=lambda r:r['q_width'])[-1]['q_width']
        min_mm_width = self.parameter('printParams.min_mm_width',5)
        min_mm_elastic_width = self.parameter('printParams.min_mm_elastic_width',20)
        for c in cells:
            if c['q_width'] == max_width_cell:
                c['mm_width'] = 0
                c['mm_min_width'] = min_mm_elastic_width
            else:
                c['mm_width'] = max(int(c['q_width']*tot_width),min_mm_width)
            if c.get('character_limit'):
                c['white_space'] = 'normal'
                self.cell_characters_limit[c['field_getter']] = c.get('character_limit')
        #self.structAnalyze(struct)
        return dict(columns=self.gridColumnsFromStruct(struct=struct),
                    columnsets=self.gridColumnsetsFromStruct(struct))

    def gridData(self):
        if self.parameter('grid_datamode')=='bag':
            self.row_mode = 'value'
        else:
            self.row_mode = 'attribute'
        return self._getSourceData()

    def _cleanWhere(self,where):
        if not where:
            return
        wrongLinesPathlist = []
        def cb(node,_pathlist=None):
            attr = node.attr
            if not (attr.get('op') and attr.get('column')):
                if not isinstance(node.value,Bag):
                    wrongLinesPathlist.append('.'.join(_pathlist+[node.label]))
        where.walk(cb,_pathlist=[])
        for path in wrongLinesPathlist:
            where.popNode(path)

    
    def _getSourceData(self):
        self.row_table = self.tblobj.fullname
        currentQuery = self.getData('currentQuery') or Bag()
        if currentQuery or self.record['selectionPkeys']:
            return self._selection_from_query(currentQuery).output('grid')
        allrows = self.parameter('allrows')
        extra_parameters = self.parameter('extra_parameters')
        if extra_parameters['currentData']:
            if allrows and extra_parameters['allGridData']:
                return extra_parameters['allGridData']
            return extra_parameters['currentData']

    def _selection_from_query(self,query):
        customOrderBy = query['customOrderBy']
        limit = query['queryLimit'] or self.parameter('previewLimit')
        where = query['where']
        self._cleanWhere(where)
        selection_kwargs = {}
        if where and not self.parameter('use_current_selection'):
            self._selection_from_savedQuery_fill_parameters(where)
            where,selection_kwargs = self.tblobj.sqlWhereFromBag(where, selection_kwargs)
        elif self.record['selectionPkeys']:
            where = '${pkey} IN :selectionPkeys'.format(pkey=self.tblobj.pkey)
            selection_kwargs = {'selectionPkeys':self.record['selectionPkeys']}
        if customOrderBy:
            order_by = []
            for fieldpath,sorting in customOrderBy.digest('#v.fieldpath,#v.sorting'):
                fieldpath = '$%s' %fieldpath if not fieldpath.startswith('@') else fieldpath
                sorting = 'asc' if sorting else 'desc'
                order_by.append('%s %s' %(fieldpath,sorting))
            selection_kwargs['order_by'] = ' , '.join(order_by)
        if limit:
            selection_kwargs['limit'] = limit
        selection_kwargs['columns'] = self.grid_sqlcolumns
        if self.parameter('condition'):
            where = '{condition} AND {where}'.format(condition=self.parameter('condition'),where=where)
        result = self.tblobj.query(where=where,**selection_kwargs).selection()
        if not selection_kwargs.get('order_by') and selection_kwargs.get('selectionPkeys'):
            pkeys = selection_kwargs.get('selectionPkeys')
            result.data.sort(key = lambda r : position(r['pkey'], pkeys))
        return result
        
    def _selection_from_savedQuery_fill_parameters(self,wherebag):
        wherepars = self.parameter('wherepars')
        if wherepars:
            for path in wherepars.getIndexList():
                wherebag[path] = wherepars[path]
        
    def docHeader(self, header):
        layout = header.layout(name='doc_header',um='mm',
                                   top=0,bottom=0,left=0,right=0,
                                   lbl_height=3,
                                   border_width=0)
        row = layout.row()
        row.cell(self.getData('print_title'), content_class='caption')    


    def calcRowHeight(self):
        if not self.cell_characters_limit:
            return self.grid_row_height
        l = []
        for k,v in self.cell_characters_limit.items():
            txt = (self.rowData.get(k) or '')
            l.append(math.ceil(len(txt)/float(v))) 
        return max(l) * self.grid_row_height

    def outputDocName(self, ext=''):
        return '%s.%s' %(self.parameter('print_title') or self.page.getUuid() ,ext)
