#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


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
        for input_path in pdf_list:
            input_node = StorageNode.fromPath(input_path, parent=self.parent)
            with input_node.open() as input_file:
                memory_file = StringIO(input_file.read())
                open_files.append(memory_file)
            input_pdf = PdfFileReader(memory_file)
            for page in input_pdf.pages:
                output_pdf.addPage(page)
        with StorageNode.fromPath(output_filepath, parent=self.parent).open(mode='wb') as output_file:
            output_pdf.write(output_file)
        for open_file in open_files:
            open_file.close()