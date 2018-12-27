#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

import os
from gnr.core.gnrlang import GnrException
from gnr.lib.services import GnrBaseService

class PrintHandlerError(GnrException):
    pass
    
class NetworkPrintService(GnrBaseService):
    """TODO"""
    paper_size = {
        'A4': '!!A4',
        'Legal': '!!Legal',
        'A4Small': '!!A4 with margins',
        'COM10': '!!COM10',
        'DL': '!!DL',
        'Letter': '!!Letter',
        'ISOB5': 'ISOB5',
        'JISB5': 'JISB5',
        'LetterSmall': 'LetterSmall',
        'LegalSmall': 'LegalSmall'
    }
    paper_tray = {
        'MultiPurpose': '!!MultiPurpose',
        'Transparency': '!!Transparency',
        'Upper': '!!Upper',
        'Lower': '!!Lower',
        'LargeCapacity': '!!LargeCapacity'
    }
    
    def __init__(self, parent, **kwargs):
        self.parent = parent

    def getPrinterConnection(self, printer_name=None, printerParams=None, **kwargs):
        pass

    def printFiles(self, file_list, jobname='GenroPrint', storeFolder=None, outputFilePath=None):
        pass

    def getPrinters(self):
        pass
        
    def getPrinterAttributes(self, printer_name):
        pass

    def autoConvertFiles(self, files, storeFolder, orientation=None):
        """TODO
        
        :param files: TODO
        :param storeFolder: TODO
        :param orientation: TODO"""
        resultList = []
        converter = self.parent.getService('htmltopdf').htmlToPdf
        for filename in files:
            baseName, ext = os.path.splitext(os.path.basename(filename))
            if ext.lower() == '.html':
                resultList.append(converter(filename, storeFolder, orientation=orientation))
            elif ext.lower() == '.pdf':
                resultList.append(filename)
            else:
                raise PrintHandlerError('not pdf file')
        return resultList


  