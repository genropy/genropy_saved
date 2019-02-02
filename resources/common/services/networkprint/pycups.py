#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
from __future__ import print_function
from builtins import str
from builtins import object
try:
    import cups

    HAS_CUPS = True
except ImportError:
    HAS_CUPS = False

from gnr.core.gnrbag import Bag

from gnr.lib.services.networkprint import NetworkPrintService

class PrinterConnection(object):
    def __init__(self,parent,printer_name=None, printerParams=None, **kwargs):
        self.parent = parent
        printerParams = printerParams or {}
        self.orientation = printerParams.get('orientation')
        printerParams = printerParams or Bag()
        self.cups_connection = cups.Connection()
        self.printer_name = printer_name
        printer_media = []
        for media_option in ('paper', 'tray', 'source'):
            media_value = printerParams['printer_options'] and printerParams['printer_options'].pop(media_option)
            if media_value:
                printer_media.append(media_value)
        self.printer_options = printerParams['printer_options'] or {}
        if printer_media:
            self.printer_options['media'] = str(','.join(printer_media))

    def printFiles(self, file_list, jobname='GenroPrint', storeFolder=None, outputFilePath=None):
        pdf_list = self.parent.autoConvertFiles(file_list, storeFolder, orientation=self.orientation)
        self.cups_connection.printFiles(self.printer_name, pdf_list, jobname, self.printer_options)


class Service(NetworkPrintService):

    def getPrinterConnection(self, printer_name=None, printerParams=None, **kwargs):
        return PrinterConnection(self,printer_name=printer_name,printerParams=printerParams,**kwargs)

    def getPrinters(self):
        """TODO"""

        printersBag = Bag()
        if HAS_CUPS:
            cups_connection = cups.Connection()
            for printer_name, printer in list(cups_connection.getPrinters().items()):
                printer.update(dict(name=printer_name))
                printersBag.setItem('%s.%s' % (printer['printer-location'], printer_name.replace(':','_')), None, printer)
        else:
            print('pyCups is not installed')
        return printersBag
        
    def getPrinterAttributes(self, printer_name):
        """TODO
        
        :param printer_name: TODO"""
        cups_connection = cups.Connection()
        printer_attributes = cups_connection.getPrinterAttributes(printer_name)
        attributesBag = Bag()
        for i, (media, description) in enumerate(self.paper_size.items()):
            if media in printer_attributes['media-supported']:
                attributesBag.setItem('paper_supported.%i' % i, None, id=media, caption=description)
        for i, (tray, description) in enumerate(self.paper_tray.items()):
            if tray in printer_attributes['media-supported']:
                attributesBag.setItem('tray_supported.%i' % i, None, id=tray, caption=description)
        return attributesBag