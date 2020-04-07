#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool
#from code39 import Code39Encoder
from pystrich.code128 import Code128Encoder
from pystrich.datamatrix import DataMatrixEncoder
from pystrich.qrcode import QRCodeEncoder
from pystrich.ean13 import EAN13Encoder
from PIL import Image
import tempfile
import mimetypes
from io import BytesIO
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
        suffix = suffix or '.png'
        temp = tempfile.NamedTemporaryFile(suffix=suffix)
        self.content_type = mimetypes.guess_type(temp.name)[0]
        if encoder and text:
            for k,v in options.items():
                if k in ('height','label_border','bottom_border','ttf_fontsize'):
                    options[k] = int(v)
            barcode = encoder(text,options=options)
            barcode.save(temp)
        else:
            image = Image.new('RGB',(1,1))
            image.save(temp, format=suffix[1:])
        temp.seek(0)
        result = temp.read()
        temp.close()
        return result
        