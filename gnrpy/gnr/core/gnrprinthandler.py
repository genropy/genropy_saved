try:
    import cups

    HAS_CUPS = True
except ImportError:
    HAS_CUPS = False
    
import os.path
from subprocess import call

try:
    import warnings

    warnings.filterwarnings(category=DeprecationWarning, module='pyPdf', action='ignore')
    from pyPdf import PdfFileWriter, PdfFileReader
    from cStringIO import StringIO

    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrdecorator import extract_kwargs
import sys

class PrinterConnection(GnrBaseService):
    """TODO"""
    service_name='print'
    
    def __init__(self, parent, printer_name=None, printerParams=None, **kwargs):
        self.parent = parent
        self.orientation = printerParams.pop('orientation',None)
        if printer_name == 'PDF':
            self.initPdf(printerParams=printerParams, **kwargs)
        else:
            self.initPrinter(printer_name, printerParams, **kwargs)
            
    def initPdf(self, printerParams=None, **kwargs):
        """TODO
        
        :param printerParams: TODO. """
        self.zipped = printerParams.pop('zipped')
        self.printAgent = self.printPdf
        
    def printPdf(self, pdf_list, jobname, outputFilePath=None):
        """TODO
        
        :param pdf_list: TODO
        :param jobname: TODO
        :param outputFilePath: TODO. """
        if self.zipped:
            outputFilePath += '.zip'
            self.parent.zipPdf(pdf_list, outputFilePath)
        else:
            outputFilePath += '.pdf'
            self.parent.joinPdf(pdf_list, outputFilePath)
        return os.path.basename(outputFilePath)
        
    def printCups(self, pdf_list, jobname, **kwargs):
        """TODO
        
        :param pdf_list: TODO
        :param jobname: TODO"""
        self.cups_connection.printFiles(self.printer_name, pdf_list, jobname, self.printer_options)
        
    def initPrinter(self, printer_name=None, printerParams=None, **kwargs):
        """TODO
        
        :param printer_name: TODO
        :param printerParams: TODO"""
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
        self.printAgent = self.printCups
        
    def printFiles(self, file_list, jobname='GenroPrint', storeFolder=None, outputFilePath=None):
        """TODO
        
        :param file_list: TODO
        :param job_name: TODO
        :param storeFolder: TODO
        :param outputFilePath: TODO"""
        pdf_list = self.parent.autoConvertFiles(file_list, storeFolder, orientation=self.orientation)
        return self.printAgent(pdf_list, jobname, outputFilePath=outputFilePath)
        
class PrintHandler(object):
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
        
    def __init__(self, parent=None):
        global HAS_CUPS, HAS_PYPDF
        self.hasCups = HAS_CUPS
        self.hasPyPdf = HAS_PYPDF
        self.parent = parent
    
    @extract_kwargs(pdf=True)
    def htmlToPdf(self, srcPath, destPath, orientation=None,pdf_kwargs=None): #srcPathList per ridurre i processi?
            
        """TODO
        
        :param src_path: TODO
        :param destPath: TODO
        :param orientation: TODO"""
        pdf_kwargs['orientation'] = orientation or 'Portrait'
        if not 'quiet' in pdf_kwargs:
            pdf_kwargs['quiet'] = True
        args = ['wkhtmltopdf']
        for k,v in pdf_kwargs.items():
            if v is not False and v is not None:
                args.append('--%s' %k.replace('_','-'))
                if v is not True:
                    args.append(str(v))
        if os.path.isdir(destPath):
            baseName = os.path.splitext(os.path.basename(srcPath))[0]
            destPath = os.path.join(destPath, '%s.pdf' % baseName)
        args.append(srcPath)
        args.append(destPath)
        result = call(args)

       #if sys.platform.startswith('linux'):
       #    result = call(['wkhtmltopdf', '-q', '-O', orientation, srcPath, destPath])
       #else:
       #    result = call(['wkhtmltopdf', '-q', '-O', orientation, srcPath, destPath,])
        if result < 0:
            raise PrintHandlerError('wkhtmltopdf error')
        return destPath
        
    def autoConvertFiles(self, files, storeFolder, orientation=None):
        """TODO
        
        :param files: TODO
        :param storeFolder: TODO
        :param orientation: TODO"""
        resultList = []
        for filename in files:
            baseName, ext = os.path.splitext(os.path.basename(filename))
            if ext.lower() == '.html':
                resultList.append(self.htmlToPdf(filename, storeFolder, orientation=orientation))
                
                #destPath=os.path.join(storeFolder, '%s.pdf' % baseName)
                
                #if sys.platform.startswith('linux'):
                #    result = call(['wkhtmltopdf','-q',filename,destPath])
                #else:
                #    result = call(['wkhtmltopdf','-q',filename,destPath])
                #if result < 0:
                #    raise PrintHandlerError('wkhtmltopdf error')
                #resultList.append(destPath)
            elif ext.lower() == '.pdf':
                resultList.append(filename)
            else:
                raise
        return resultList
        
    def getPrinters(self):
        """TODO"""
        printersBag = Bag()
        if self.hasCups:
            cups_connection = cups.Connection()
            for printer_name, printer in cups_connection.getPrinters().items():
                printer.update(dict(name=printer_name))
                printersBag.setItem('%s.%s' % (printer['printer-location'], printer_name.replace(':','_')), None, printer)
        else:
            print 'pyCups is not installed'
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
        
    def getPrinterConnection(self, printer_name=None, printerParams=None, **kwargs):
        """TODO
        
        :param printer_name: TODO
        :param printerParams: TODO"""
        return PrinterConnection(self, printer_name=printer_name, printerParams=printerParams, **kwargs)
        
    def joinPdf(self, pdf_list, output_filepath):
        """TODO
        
        :param pdf_list: TODO
        :param output_filepath: TODO"""
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
            
    def zipPdf(self, file_list=None, zipPath=None):
        """TODO
        
        :param file_list: TODO
        :param zipPath: TODO"""
        self.parent.zipFiles(file_list=file_list, zipPath=zipPath)
        