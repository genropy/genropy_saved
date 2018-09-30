#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services import GnrBaseService

class PdfService(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def joinPdf(self, pdf_list, output_filepath):
        pass

    
    def zipPdf(self, file_list=None, zipPath=None):
        """TODO
        
        :param file_list: TODO
        :param zipPath: TODO"""
        self.parent.zipFiles(file_list=file_list, zipPath=zipPath)
        
    