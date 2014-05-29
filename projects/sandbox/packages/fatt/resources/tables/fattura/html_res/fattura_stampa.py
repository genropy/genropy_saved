#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import TableScriptToHtml
CURRENCY_FORMAT = '#,###.00'

class Main(TableScriptToHtml):
    maintable = 'fatt.fattura'
    def main(self):
        page = self.getNewPage()
        principale = page.layout('principale',top=1,left=1,right=1,bottom=1,border_width=0)
        self.testata(principale.row(height=30))
        self.righe(principale.row())
        self.piede(principale.row(height=10))

    def testata(self,row):
        self.datiFattura(row.cell(width=80).layout('dati_fattura',top=1,left=1,
                                                    right=1,bottom=1,border_width=0))

        row.cell()
        self.datiCliente(row.cell(width=50).layout('dati_cliente',top=1,left=1,right=1,bottom=1,border_width=0))

    def datiFattura(self,layout):
        r1 = layout.row(height=8)
        r1.cell('N.Fattura')
        r1.cell(self.field('protocollo'))
        r2 = layout.row(height=8)
        r2.cell('Data Fattura')
        r2.cell(self.field('data'))
        layout.row()

    def datiCliente(self,layout):
        layout.row(height=5).cell('Spett.')
        layout.row(height=5).cell(self.field('@cliente_id.ragione_sociale'))
        layout.row(height=5).cell(self.field('@cliente_id.indirizzo'))
        layout.row(height=5).cell('%s (%s)' %(self.field('@cliente_id.@comune_id.denominazione'),self.field('@cliente_id.provincia')))
        layout.row()

    def righe(self,row):
        self.body.style(""".grigliaRigheHeader{
                background:whitesmoke;
                color:gray;
                font-size:8pt;
                text-align:center;
            }
            .grigliaRigheCell{
                font-size:9pt;
                padding-left:1mm;
                padding-right:1mm;
            }
            .alignRight{
                text-align:right;
            }

            """)
        layout = row.cell().layout('righe_fattura',top=1,left=1,right=1,bottom=1,
                                    border_width=.3,border_color='silver',
                                    content_class='grigliaRigheCell',row_border=False)
        testata_righe = layout.row(height=4,content_class='grigliaRigheHeader')
        testata_righe.cell('Prodotto')
        testata_righe.cell(u'Quantità',width=20)
        testata_righe.cell('Pr.Unitario',width=20)
        testata_righe.cell('Pr.Totale',width=20)
        testata_righe.cell('Aliquota',width=20)
        testata_righe.cell('IVA',width=20)
        for righe_fattura in self.record['@righe'].values():
            r = layout.row(height=5)
            r.cell(righe_fattura['@prodotto_id.descrizione'])
            r.cell(righe_fattura['quantita'],width=20,_class='alignRight')
            r.cell(self.toText(righe_fattura['prezzo_unitario'],format=CURRENCY_FORMAT),width=20,_class='alignRight')
            r.cell(self.toText(righe_fattura['prezzo_totale'],format=CURRENCY_FORMAT),width=20,_class='alignRight')
            r.cell(self.toText(righe_fattura['aliquota_iva'],format=CURRENCY_FORMAT),width=20,_class='alignRight')
            r.cell(self.toText(righe_fattura['iva'],format=CURRENCY_FORMAT),width=20,_class='alignRight')
        testata_righe = layout.row()
        testata_righe.cell()
        testata_righe.cell(width=20)
        testata_righe.cell(width=20)
        testata_righe.cell(width=20)
        testata_righe.cell(width=20)
        testata_righe.cell(width=20)


    def piede(self,row):
        row.cell()
        l = row.cell(width=70).layout('totali_fattura',top=1,left=1,right=1,bottom=1,
                                    border_width=.3,border_color='silver',lbl_class='grigliaRigheHeader',
                                    content_class='grigliaRigheCell alignRight')
        r = l.row()
        r.cell(self.field('totale_imponibile',format=CURRENCY_FORMAT),lbl='Imponibile')
        r.cell(self.field('totale_iva',format=CURRENCY_FORMAT),lbl='IVA')
        r.cell(self.field('totale_fattura',format=CURRENCY_FORMAT),lbl='Totale')




