#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-


from gnr.lib.services.pdf import PdfService
from gnr.lib.services.storage import StorageNode

try:
    import warnings

    warnings.filterwarnings(category=DeprecationWarning, module='pyPdf', action='ignore')
    from pyPdf import PdfFileWriter, PdfFileReader
    from cStringIO import StringIO

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
                memory_file = StringIO(input_file.read())
                open_files.append(memory_file)
            input_pdf = PdfFileReader(memory_file)
            for page in input_pdf.pages:
                output_pdf.addPage(page)
        with out_sn.open(mode='wb') as output_file:
            output_pdf.write(output_file)
        for open_file in open_files:
            open_file.close()