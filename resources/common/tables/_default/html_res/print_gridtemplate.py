#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace

from gnr.core.gnrbag import Bag

class Main(TableScriptToHtml):
    page_header_height = 0 #topHeight
    page_footer_height = 0 
    doc_header_height = 0 #headerHeight
    doc_footer_height = 0 #footerHeight
    grid_header_height = 0
    grid_footer_height = 0 
    grid_col_widths=[0] #rowColWidth
    row_mode='values'
    grid_row_height=5.3
    rows_path = 'rows'

    def gridLayout(self,body):
        return body.layout(name='rowsL',um='mm',border_color='gray',
                            top=1,bottom=1,left=1,right=1,
                            border_width=.3,
                            style='line-height:5mm;text-align:left;font-size:7.5pt')

    def mainLayout(self,page):
        style = """font-family:"Lucida Grande", Lucida, Verdana, sans-serif;
                    text-align:left;
                    line-height:5mm;
                    font-size:9pt;
                    """
        return page.layout(name='pageLayout',width=190,
                            height=self.page_height,
                            um='mm',top=0,
                            left=5,border_width=0,
                            lbl_height=4,lbl_class='caption',
                            style=style)

    def prepareRow(self,row):
        self.rowCell(value='%s::HTML' %templateReplace(self.row_tpl,Bag(self.currRowDataNode)))

    def onRecordLoaded(self):
        #self.grid_col_headers = self.getData('grid_col_headers')
        self.row_tpl = self.getData('row_tpl')
        self.grid_row_height =self.getData('grid_row_height')


    def outputDocName(self, ext=''):
        return '%s.%s' %(self.getData('titolo'),ext)
