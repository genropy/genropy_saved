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
    grid_row_height=5.3
    row_mode = 'attribute'

    def docHeader(self, header):
        layout = header.layout(name='doc_header',um='mm',
                                   top=0,bottom=0,left=0,right=0,
                                   lbl_height=3,
                                   border_width=0)
        row = layout.row()
        row.cell(self.getData('print_title'),content_class='caption')

    def gridData(self):
        return self.sourceSelectionData
    
    def gridColumns(self):
        struct = self.sourceStruct
        tot_width = decimalRound(self.page_width-self.page_margin_left -self.page_margin_right-2)
        cells = struct['#0.#0'].digest('#a')
        max_width_cell = sorted(cells,key=lambda r:r['q_width'])[-1]['q_width']
        for c in cells:
            if c['q_width'] == max_width_cell:
                c['mm_width'] = 0
            else:
                c['mm_width'] = int(c['q_width']*tot_width)
        return self.gridColumnsFromStruct(struct=struct,table=self.row_table)

    def outputDocName(self, ext=''):
        return '%s.%s' %(self.getData('titolo'),ext)
