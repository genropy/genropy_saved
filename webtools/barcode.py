#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrBaseWebTool subclass ---------------------------


from gnr.web.gnrbasewebtool import GnrBaseWebTool
from code39 import Code39Encoder
from code128 import Code128Encoder
from datamatrix import DataMatrixEncoder
from qrcode import QRCodeEncoder
from ean13 import EAN13Encoder
import tempfile
import mimetypes
encoders = {
    'code39' : Code39Encoder,
    'code128' : Code128Encoder,
    'datamatrix' : DataMatrixEncoder,
    'qrcode': QRCodeEncoder,
    'ean13' : EAN13Encoder
    
}
class Barcode(GnrBaseWebTool):
    #content_type = 'image/png'
    #headers = [('header_name','header_value')]
    

    def __call__(self,text=None, mode='code128',height=None,width=None,suffix='.png', **kwargs):
        print text
        encoder = encoders.get(mode)
        if not encoder:
            return
        barcode = encoder(text)
        temp = tempfile.NamedTemporaryFile(suffix=suffix)
        barcode.save(temp.name)
        self.content_type = mimetypes.guess_type(temp.name)[0]
        return temp.read()
        