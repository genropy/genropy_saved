#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-


from gnr.lib.services.pdf import PdfService

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader
    from io import BytesIO

    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

class Service(PdfService):

    def joinPdf(self, pdf_list, output_filepath):
        """TODO
        :param pdf_list: TODO
        :param output_filepath: TODO"""
        
        if not HAS_PYPDF:
            raise self.parent.exception('Missing pyPdf in this installation')
        output_pdf = PdfFileWriter()
        open_files = []
        out_sn = self.parent.storageNode(output_filepath)
        if len(pdf_list)==1:
            input_node = self.parent.storageNode(pdf_list[0])
            input_node.copy(out_sn)
            return
        for input_path in pdf_list:
            input_node = self.parent.storageNode(input_path)
            with input_node.open() as input_file:
                memory_file = BytesIO(input_file.read())
                open_files.append(memory_file)
            input_pdf = PdfFileReader(memory_file)
            for page in input_pdf.pages:
                output_pdf.addPage(page)
        with out_sn.open(mode='wb') as output_file:
            output_pdf.write(output_file)
        for open_file in open_files:
            open_file.close()