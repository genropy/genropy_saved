#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services import GnrBaseService

class PdfService(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def joinPdf(self, pdf_list, output_filepath):
        pass
