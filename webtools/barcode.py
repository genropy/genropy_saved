#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool
#from code39 import Code39Encoder
from hubarcode.code128 import Code128Encoder
from hubarcode.datamatrix import DataMatrixEncoder
from hubarcode.qrcode import QRCodeEncoder
from hubarcode.ean13 import EAN13Encoder
import tempfile
import mimetypes

encoders = {
    #'code39' : Code39Encoder,
    'code128': Code128Encoder,
    'datamatrix': DataMatrixEncoder,
    'qrcode': QRCodeEncoder,
    'ean13': EAN13Encoder

}
class Barcode(BaseWebtool):
    #content_type = 'image/png'
    #headers = [('header_name','header_value')]


    def __call__(self, text=None, mode='code128', height=None,ttf_font=None,ttf_fontsize=None,
                label_border=None,bottom_border=None,suffix='.png', **kwargs):
        encoder = encoders.get(mode)
        if not encoder:
            return
        options = dict(height=height,ttf_fontsize=ttf_fontsize,ttf_font=ttf_font,
                        label_border=label_border,bottom_border=bottom_border)
        barcode = encoder(text,options=options)
        temp = tempfile.NamedTemporaryFile(suffix=suffix)
        barcode.save(temp.name)
        self.content_type = mimetypes.guess_type(temp.name)[0]
        return temp.read()
        