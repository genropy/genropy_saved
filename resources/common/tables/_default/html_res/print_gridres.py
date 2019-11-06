#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrnumber import decimalRound


from gnr.core.gnrbag import Bag

class Main(TableScriptToHtml):
    page_header_height = 0 #topHeight
    page_footer_height = 0 
    doc_header_height = 10 #headerHeight
    doc_footer_height = 0 #footerHeight
    grid_footer_height = 0 
    grid_header_height = 4.3
    grid_col_widths=[0] #rowColWidth
    grid_row_height=5

    def onRecordLoaded(self):
        userObjectIdOrCode = self.getData('userobject')
        struct = self.getData('currentGridStruct')
        printParams = self.getData('printParams') or Bag()
        letterhead = self.getData('letterhead') or self.getData('letterhead_id')
        self.row_table = self.tblobj.fullname
        self.row_mode = 'attribute'
        if userObjectIdOrCode:
            data,metadata = self.page.db.table('adm.userobject'
                                ).loadUserObject(userObjectIdOrCode=userObjectIdOrCode,
                                                table=self.tblobj.fullname)
            if struct is None:
                struct =  data.getItem('struct')
            self.setData('currentQuery',self.getData('currentQuery') or data.getItem('query'))
            printParams = printParams or data.getItem('printParams') or Bag()
            printParams['title'] = printParams['title'] or metadata.get('description')
            self.row_table = metadata.get('tbl') or self.row_table
            letterhead = data['letterhead']
        self.htmlTemplate = letterhead
        totalize_mode = self.getData('totalize_mode') or printParams['totalize_mode']
        totalize_footer =  self.getData('totalize_footer') or printParams['totalize_footer']
        totalize_carry = self.getData('totalize_carry') or printParams['totalize_carry']
        if totalize_mode or totalize_footer or totalize_carry:
            self.totalize_mode = totalize_mode or 'doc'
            self.totalize_footer = totalize_footer or True
            self.totalize_carry = totalize_carry
        self.page_orientation = printParams['orientation'] or self.getData('orientation') or 'V'
        self.setStruct(struct)
        if not self.getData('print_title'):
            self.setData('print_title',printParams['title'] or 'print_grid_{}'.format(self.row_table.replace('.','_')))

    def gridColumnsInfo(self):
        struct = self.getStruct()
        tot_width = decimalRound(self.page_width-self.page_margin_left -self.page_margin_right-2)
        cells = struct['#0.#0'].digest('#a')
        max_width_cell = sorted(cells,key=lambda r:r['q_width'])[-1]['q_width']
        min_mm_width = self.getData('printParams.min_mm_width',5)
        min_mm_elastic_width = self.getData('printParams.min_mm_elastic_width',20)
        for c in cells:
            if c['q_width'] == max_width_cell:
                c['mm_width'] = 0
                c['mm_min_width'] = min_mm_elastic_width
            else:
                c['mm_width'] = max(int(c['q_width']*tot_width),min_mm_width)
        self.structAnalyze(struct)
        return dict(columns=self.gridColumnsFromStruct(struct=struct),
                    columnsets=self.gridColumnsetsFromStruct(struct))




    def gridData(self):
        if self.getData('grid_datamode')=='bag':
            self.row_mode = 'value'
        else:
            self.row_mode = 'attribute'
        result = self._getSourceData()
        if self.subtotals_breakers:
            sortlist = self.subtotals_breakers
            if self.row_mode == 'attribute':
                sortlist = ['#a.{}'.format(col.get('field_getter') or col.get('field')) for col in self.subtotals_breakers]
            result = result.sort(','.join(sortlist))
        return result 

    def _getSourceData(self):
        currentQuery = self.getData('currentQuery')
        if currentQuery:
            return self._selection_from_query(currentQuery).output('grid')
        allrows = self.getData('allrows')
        extra_parameters = self.getData('extra_parameters')
        if extra_parameters['currentData']:
            if allrows and extra_parameters['allGridData']:
                return extra_parameters['allGridData']
            return extra_parameters['currentData']
        columns = self.grid_sqlcolumns if self.callingBatch.selectedPkeys else None
        allSelectionPkeys = extra_parameters['allSelectionPkeys']
        if allrows:
            if allSelectionPkeys:
                self.callingBatch.selectedPkeys = allSelectionPkeys
            else:
                self.callingBatch.selectedRowidx = []
        return self.callingBatch.get_selection(columns=columns).output('grid')
        
    def _selection_from_query(self,query):
        if query['where']:
            limit = query['queryLimit']
            customOrderBy = query['customOrderBy']
            where = query['where']
            self._selection_from_savedQuery_fill_parameters(where)
            selection_kwargs = {}
            where,selection_kwargs = self.tblobj.sqlWhereFromBag(where, selection_kwargs)
            selection_kwargs['columns'] = self.grid_sqlcolumns
            if customOrderBy:
                order_by = []
                for fieldpath,sorting in customOrderBy.digest('#v.fieldpath,#v.sorting'):
                    fieldpath = '$%s' %fieldpath if not fieldpath.startswith('@') else fieldpath
                    sorting = 'asc' if sorting else 'desc'
                    order_by.append('%s %s' %(fieldpath,sorting))
                selection_kwargs['order_by'] = ' , '.join(order_by)
            if limit:
                selection_kwargs['limit'] = limit
            return self.tblobj.query(where=where,**selection_kwargs).selection()
        
    def _selection_from_savedQuery_fill_parameters(self,wherebag):
        def fillpar(n):
            if n.value is None and n.attr.get('value_caption','').startswith('?'):
                bp_name = n.attr['value_caption'][1:].lower().replace(' ','_')
                if bp_name in self._data:
                    n.value = self.getData(bp_name)
        wherebag.walk(fillpar)
        
    def docHeader(self, header):
        layout = header.layout(name='doc_header',um='mm',
                                   top=0,bottom=0,left=0,right=0,
                                   lbl_height=3,
                                   border_width=0)
        row = layout.row()
        row.cell(self.getData('print_title'), content_class='caption')    

    def outputDocName(self, ext=''):
        return '%s.%s' %(self.getData('print_title') ,ext)
