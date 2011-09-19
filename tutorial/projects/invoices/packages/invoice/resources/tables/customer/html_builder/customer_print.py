#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  customer_print.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import TableScriptToHtml

class Main(TableScriptToHtml):
    maintable = 'invoice.customer'
    rows_table = '???'
    rows_path = 'rows' # posso mettere anche dei relation paths (se però li metto allora la bag è gerarchica
                       #    quindi il row_mode è value)
                       # rows_path è il path dove vado a mettere la selection() vedi line  130
    row_mode='attribute' # le possibilità sono:
                         #  'value': se la Bag su cui salvo i dati della query attraverso la selection è una Bag normale
                         #   cioè gerarchica, quindi non piatta
                         #  'attribute' lo uso se la Bag è piatta!

    page_header_height = 0
    page_footer_height = 0
    doc_header_height = 10
    doc_footer_height = 10
    grid_header_height = 6.2
    grid_footer_height = 0
    grid_col_widths=[17,12,0,0,20,15,15,20]
    grid_col_headers = 'Data,Ora,Paziente,Prestazione,Convenzione,Importo,Costo,Fattura'
    grid_row_height=5.3
    
    def docHeader(self,header):
        # I receive the header and I can append a layout with rows and cell
        layout = header.layout(name='header',um='mm',
                                   lbl_class='smallCaption',
                                   top=1,bottom=1,left=1,right=1,
                                   lbl_height=3,
                                   border_width=.3,
                                   border_color='gray',
                                   style='line-height:6mm;text-align:left;text-indent:2mm;')        
        row=layout.row(height=10)
        row.cell("%s %s" %(self.field('@anagrafica_id.nome'), self.field('@anagrafica_id.cognome')),lbl='Prestazioni di')
        row.cell(self.toText(self.getData('period.from')), lbl='Dal',width=30,content_class='aligned_right')
        row.cell(self.toText(self.getData('period.to')), lbl='al', width=30,content_class='aligned_right')
        row.cell(self.pageCounter(), lbl='Pagina', width=12,content_class='aligned_right')

    def docFooter(self, footer,lastPage=None):
        if not lastPage:
            return
        layout = footer.layout(name='footerL',um='mm',border_color='gray',
                               lbl_class='smallCaption',
                               top=1,bottom=1,left=80,right=1,
                               lbl_height=3,border_width=0.3,
                               content_class='aligned_right')
        row=layout.row(height=0)
        lastPage = lastPage or False
        if lastPage:
            totals_dict = {}
            totals_dict['importo'],totals_dict['costo'] = self.getData('rows').sum('#a.importo,#a.costo')
            
            row.cell(self.toText(totals_dict['importo'],format=self.currencyFormat),lbl='Totale importo')
            row.cell(self.toText(totals_dict['costo'],format=self.currencyFormat),lbl='Totale costo')
        else:
            row.cell()
            
    def gridLayout(self,body):
        # here you receive the body (the center of the page) and you can define the layout
        # that contains the grid
        return body.layout(name='rowsL',um='mm',border_color='gray',
                            top=1,bottom=1,left=1,right=1,
                            border_width=.3,lbl_class='caption',
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
        # this callback prepare the row of the maingrid
        style_cell = 'text-indent:2mm;border-bottom-style:dotted;'
        self.rowCell('data',style=style_cell)
        self.rowCell('ora',format='HH:mm', style=style_cell)
        self.rowCell('paziente', style=style_cell)
        self.rowCell('prestazione', style=style_cell)
        self.rowCell('convenzione_codice', style=style_cell)
        self.rowCell('importo',format=self.currencyFormat, style=style_cell,content_class='aligned_right')
        self.rowCell('costo',format=self.currencyFormat, style=style_cell,content_class='aligned_right')
        self.rowCell('fattura', style=style_cell,content_class='aligned_right')
        
    def onRecordLoaded(self):
        where = '$data >= :data_inizio AND $data<= :data_fine AND medico_id=:m_id'
        columns ="""$medico,$data,$ora,$paziente,$prestazione,
                    @convenzione_id.codice AS convenzione_codice,
                    $importo,$costo,@fattura_id.numero AS fattura"""
        query = self.db.table(self.rows_table).query(columns=columns, where=where, 
                                                             data_inizio=self.getData('period.from'),
                                                             data_fine=self.getData('period.to'),
                                                             m_id=self.record['id'])
        selection = query.selection() # è un'alternativa alla fetch() che ritorna
                                      # un oggetto "selection" che fornisce differenti output
                                      # (doc i vari modi)
        if not selection:
            return False
        self.setData('rows',selection.output('grid')) # l'output 'grid' è una bag che ha delle label
                                                      # ! Tutte le informazioni sono negli attributi (quindi è una Bag piatta, non gerarchica)

        
    def outputDocName(self, ext=''):
        medico = self.getData('record.@anagrafica_id.ragione_sociale')
        mlist = medico.split(' ')
        medico = ''.join(mlist)
        return '%s.%s' %(medico.lower(),ext)