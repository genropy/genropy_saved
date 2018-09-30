#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.pdf import PdfService


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
            input_file = open(input_path, 'rb')
            memory_file = StringIO(input_file.read())
            open_files.append(memory_file)
            input_file.close()
            input_pdf = PdfFileReader(memory_file)
            for page in input_pdf.pages:
                output_pdf.addPage(page)
        output_file = open(output_filepath, 'wb')
        output_pdf.write(output_file)
        output_file.close()
        for input_file in open_files:
            input_file.close()