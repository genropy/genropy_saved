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


    def __call__(self, text=None, mode='code128',suffix='.png', **options):
        """ The options hash currently supports three options:
             * ttf_font: absolute path to a truetype font file used to render the label
             * ttf_fontsize: the size the label is drawn in
             * label_border: number of pixels space between the barcode and the label
             * bottom_border: number of pixels space between the label and the bottom border
             * height: height of the image in pixels 
        """
        encoder = encoders.get(mode)
        if not encoder:
            return
        for k,v in options.items():
            if k in ('height','label_border','bottom_border','ttf_fontsize'):
                options[k] = int(v)
        barcode = encoder(text,options=options)
        temp = tempfile.NamedTemporaryFile(suffix=suffix)
        barcode.save(temp.name)
        self.content_type = mimetypes.guess_type(temp.name)[0]
        return temp.read()
        