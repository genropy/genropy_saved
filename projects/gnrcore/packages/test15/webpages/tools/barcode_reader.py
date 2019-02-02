# -*- coding: utf-8 -*-
# 
"""ClientPage tester"""

from builtins import object
class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                     gnrcomponents/barcode_reader/barcode_reader:BarcodeReader"""
    
    def test_1_plain(self, pane):
        """Barcode reader"""
        bc=pane.borderContainer(height='600px')
        bc.barcodeReaderBox(region='center',readers="ean_reader",destination='.scanned_barcode',zoom=.5)

        bc.contentPane(region='bottom',height='100px').div('^.barcodes')
        bc.dataController("""console.log('scanned_barcode',scanned_barcode);
                """,
                            scanned_barcode='^.scanned_barcode',barcodes='=.barcodes',
                            _delay=2000)
    
    def test_2_tb(self,pane):
        fb = pane.formbuilder()
        fb.barcodeReaderTextBox(value='^.barcode',codes="ean",lbl='Barcode',
                                sound='ping',delay=5)
        fb.dataController("""
            console.log('barcode',barcode)
            SET .barcode = null;
        """,barcode='^.barcode',_if='barcode',_delay=500)