# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
import xlwt

caption = '!!Export to excel'
tags = 'user'
description='!!Export to excel'

class Main(BaseResourceAction):
    batch_prefix = 'XLS'
    batch_title = 'Export to xls'
    batch_cancellable = False
    batch_delay = 0.5
        
    def result_handler(self):
        return 'Execution completed',dict(url=self.fileUrl,document_name=self.batch_parameters['filename'])
    
    def pre_process(self):
        self.locale = self.page.locale
        self.filename = '%s.xls'%(self.batch_parameters['filename'] or self.maintable.replace('.','_'))
        selection = self.get_selection()
        columns = selection.columns
        self.colHeaders={}
        if self.struct:
            self.colHeaders=dict([(x.replace('.','_').replace('@','_').replace('$',''),y) for x,y in self.struct['#0.#0'].digest('#a.field,#a.name') if (x and y)])
            columns=[c for c in columns if c in self.colHeaders ]
        self.columns = columns
        self.workbook = xlwt.Workbook(encoding='latin-1')
        self.sheet = self.workbook.add_sheet(self.filename)
        float_style = xlwt.XFStyle()
        float_style.num_format_str = '#,##0.00'
        int_style = xlwt.XFStyle()
        int_style.num_format_str = '#,##0'
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        hstyle = xlwt.XFStyle()
        hstyle.font = font0
        self.data = selection.output('dictlist', columns=self.columns, locale=self.locale)
        for c,header in enumerate(self.columns):
            self.sheet.write(0, c, self.colHeaders[header], hstyle)
        self.current_row=1
        
    def do(self):
        selection = self.get_selection()
        for row in self.btc.thermo_wrapper(self.data,'row',message=self.get_record_caption):
            self.process_chunck(row)
        self.post_process()
        
    def process_chunck(self, chunk):
        for c,column in enumerate(self.columns):
            if isinstance(chunk[column], list):
                value=','.join([str(x != None and x or '') for x in chunk[column]])
            else:
                value = chunk[column]
            self.sheet.write(self.current_row, c, value)
        self.current_row += 1
    
    def post_process(self):
        self.filePath=self.page.temporaryDocument(self.filename)
        self.fileUrl=self.page.temporaryDocumentUrl(self.filename)
        self.workbook.save(self.filePath)    
    
    def table_script_parameters_pane(self,pane,**kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.filename',lbl='!!Save as')
        
    def charwidths(self): 
        return {
        '0': 262.637,'1': 262.637,'2': 262.637,'3': 262.637,'4': 262.637,'5': 262.637,'6': 262.637,
        '7': 262.637,'8': 262.637,'9': 262.637,'a': 262.637,'b': 262.637,'c': 262.637,'d': 262.637,
        'e': 262.637,'f': 146.015,'g': 262.637,'h': 262.637,'i': 117.096,'j': 88.178,'k': 233.244,
        'l': 88.178,'m': 379.259,'n': 262.637,'o': 262.637,'p': 262.637,'q': 262.637,'r': 175.407,
        's': 233.244,'t': 117.096,'u': 262.637,'v': 203.852,'w': 321.422,'x': 203.852,'y': 262.637,
        'z': 233.244,'A': 321.422,'B': 321.422,'C': 350.341,'D': 350.341,'E': 321.422,'F': 291.556,
        'G': 350.341,'H': 321.422,'I': 146.015,'J': 262.637,'K': 321.422,'L': 262.637,'M': 379.259,
        'N': 321.422,'O': 350.341,'P': 321.422,'Q': 350.341,'R': 321.422,'S': 321.422,'T': 262.637,
        'U': 321.422,'V': 321.422,'W': 496.356,'X': 321.422,'Y': 321.422,'Z': 262.637,' ': 146.015,
        '!': 146.015,'"': 175.407,'#': 262.637,'$': 262.637,'%': 438.044,'&': 321.422,'\'': 88.178,
        '(': 175.407,')': 175.407,'*': 203.852,'+': 291.556,',': 146.015,'-': 175.407,'.': 146.015,
        '/': 146.015,':': 146.015,';': 146.015,'<': 291.556,'=': 291.556,'>': 291.556,'?': 262.637,
        '@': 496.356,'[': 146.015,'\\': 146.015,']': 146.015,'^': 203.852,'_': 262.637,'`': 175.407,
        '{': 175.407,'|': 146.015,'}': 175.407,'~': 291.556}


    def colwidth(self,n):
        '''Translate human-readable units to BIFF column width units'''
        if n <= 0:
            return 0
        if n <= 1:
            return n * 456
        return 200 + n * 256

    def fitwidth(self,data, bold=False):
        '''Try to autofit Arial 10'''
        units = 220
        charwidths = self.charwidths()
        for char in str(data):
            if char in charwidths:
                units += charwidths[char]
            else:
                units += charwidths['0']
        if bold:
            units *= 1.1
        return max(units, 700) # Don't go smaller than a reported width of 2
    
