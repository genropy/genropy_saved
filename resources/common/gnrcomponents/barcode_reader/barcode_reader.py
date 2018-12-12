# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class BarcodeReader(BaseComponent):
    js_requires='gnrcomponents/barcode_reader/quagga.min,gnrcomponents/barcode_reader/barcode_reader'


    @struct_method
    def br_barcodeReaderTextBox(self,parent,value=None,codes=None,delay=None,sound=None,**kwargs):
        tb = parent.textBox(value=value,**kwargs)
        pane = tb.comboArrow().tooltipPane(onOpening="""
            var n = genro.nodeById('br_preview');
            BarcodeReader.start(n,n.attr._readers,n.attr._destination,n.attr._delay,n.attr._sound);
        """,
        onClosing='Quagga.stop();',modal=True)
        pane.div(height='240px',width='320px',overflow='hidden').div(nodeId='br_preview',
            _readers=codes,_destination=value.replace('^',''),
            _delay=delay,_sound=sound,zoom=.5)