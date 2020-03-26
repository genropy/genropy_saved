#!/usr/bin/env python
# encoding: utf-8
#
import sys
from pdf2image import convert_from_path
from PIL import Image
import zbarlight
import requests
from backports import tempfile
from PyPDF2 import PdfFileWriter, PdfFileReader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
from datetime import date
import shutil
import os
from io import StringIO

class GnrAttachmentEventHandler(FileSystemEventHandler):
    
    def __init__(self, upload_handler=None):
        self.upload_handler = upload_handler
    
    def on_created(self, event):
        super(GnrAttachmentEventHandler, self).on_created(event)
        if not event.is_directory:
            self.upload_handler(event.src_path)
    
class ScannedFileParser(object):
    allowed_extensions = ['pdf']

    def __init__(self, input_path=None, parsed_path=None):
        self.input_path = input_path
        self.parsed_path = parsed_path

    def is_parsable(self, file_path):
        ext = os.path.splitext(file_path)[-1].replace('.','').lower()
        return ext in self.allowed_extensions

    def parse_current(self):
        for file_name in os.listdir(self.input_path):
            self.attachment_parse(os.path.join(self.input_path, file_name))

    def parse_pages(self, inputpdf):
        """ Returns a list of tuples, the first item is the qrcode, the second one 
            is the list of related pages"""
        output = []
        current_qr = None
        current_pages = []
        with tempfile.TemporaryDirectory() as tmppath:
            pages = convert_from_path(inputpdf, output_folder=tmppath)
            for page_no, page in enumerate(pages):
                print page_no
                qr_codes = zbarlight.scan_codes('qrcode', page)
                print qr_codes
                page_qr = None
                if qr_codes:
                    for qr_code in qr_codes:
                        page_qr = "http://127.0.0.1:8083/sys/call_service?service_name=upload:attachment&pkg=bpsa&tbl=contratto&pkey=pluto"
                        break
                        if qr_code.startswith('GNRATC:'):
                            page_qr = qr_code
                            break
                if page_qr:
                    print page_qr
                    print current_pages
                    if current_qr:
                        output.append((current_qr, current_pages))
                    current_pages = []
                    current_qr = page_qr
                current_pages.append(page_no)
            if current_qr:
                output.append((current_qr, current_pages))
        return output

    def pdf_pages(self, inputpdf, page_list, out_path=None):
        """"Given and input pdf outputs a pdf containing the specified pages numbers
            a StringIO is returned if no out_path is specified"""
        inputfile = PdfFileReader(open(inputpdf, "rb"))
        output = PdfFileWriter()
        for page_no in page_list:
            output.addPage(inputfile.getPage(page_no))
        if out_path:
            with open(out_path, "wb") as outputfile:
                output.write(outputfile)
        else:
            outputIO = StringIO()
            output.write(outputIO)
            outputIO.seek(0)
            return outputIO

    def upload_attachment(self, url, stream):
        stream.seek(0)
        files = dict(attachment=stream)
        r = requests.post(url, files=files)

    def attachment_parse(self, file_path):
        if not self.is_parsable(file_path): return
        documents = self.parse_pages(file_path)
        for qr, pages in documents:
            url = qr.replace('GNRATC:','')
            pdf_stream = self.pdf_pages(file_path, pages)
            self.upload_attachment(url, pdf_stream)
        self.move_file(file_path)

    def move_file(self, file_path):
        tdy = date.today
        output_parent = os.path.join(self.parsed_path, "%04i"%tdy.year, "%02i"%tdy.month, "%02i"%tdy.day)
        if not os.path.exists(output_parent):
            os.makedirs(output_parent)
        output_path = os.path.join(output_parent, os.path.basename(file_path))
        shutil.move(file_path, output_path)



def main():
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    scn_parser = ScannedFileParser(input_path=path, parsed_path=os.path.join(path,'parsed'))
    scn_parser.parse_current()
    event_handler = GnrAttachmentEventHandler(upload_handler=scn_parser.attachment_parse)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
