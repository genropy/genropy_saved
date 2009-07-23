import cups
import os.path
from subprocess import call
from pyPdf import PdfFileWriter, PdfFileReader
from gnr.core.gnrbag import Bag, DirectoryResolver

class PrinterConnection(object):
    
    def __init__(self, parent, printer_name=None, printerParams=None, **kwargs):
        self.parent = parent
        if printer_name == 'PDF':
            self.initPdf(printerParams, **kwargs)
        else:
            self.initPrinter(printer_name, printerParams, **kwargs)
        
    def initPdf(self, zipped=True, printerParams=None, **kwargs):
        self.zipped=zipped
        self.printAgent = self.printPdf
        
    def printPdf(self,pdf_list, jobname):
        if self.zipped:
            return #crea un archivio zip dei files
        else:
            output_pdf = PdfFileWriter()
            for input_path in file_list:
                with open(input_path,'rb') as input_file:
                    input_pdf = PdfFileReader(input_file)
                    for page in input_pdf.pages:
                        output_pdf.addPage(page)
            with open(output_path,'wb') as output_file:
                output_file.output(output_pdf)
            return output_file
            
    def printCups(self,pdf_list, jobname):
        self.connection.printFiles(self.printer_name, pdf_list, jobname, self.printer_options)
         
    def initPrinter(self, printer_name=None, printerParams=None, **kwargs):
        printerParams = printerParams or {}
        self.connection = cups.Connection()
        self.printer_name = printer_name
        printer_media=[]
        for media_option in ('paper','tray','source'):
            media_value = printerParams['printer_options'] and printerParams['printer_options'].pop(media_option)
            if media_value:
                printer_media.append(media_value)
        self.printer_options = printerParams['printer_options'] or {}
        if printer_media:
            self.printer_options['media'] = str(','.join(printer_media))
        self.printAgent = self.printCups
            
    def printFiles(self, file_list, jobname='GenroPrint', storeFolder=None):
        pdf_list = self.parent.autoConvertFiles(file_list,storeFolder)
        self.printAgent(pdf_list, jobname)
        
class PrintHandler(object):
    paper_size = {
            'A4': '!!A4',
            'Legal':'!!Legal',
            'A4Small': '!!A4 with margins',
            'COM10': '!!COM10',
            'DL':'!!DL',
            'Letter':'!!Letter',
            'ISOB5':'ISOB5',
            'JISB5':'JISB5',
            'LetterSmall':'LetterSmall',
            'LegalSmall':'LegalSmall'
            }
    paper_tray = {
            'MultiPurpose':'!!MultiPurpose',
            'Transparency':'!!Transparency',
            'Upper':'!!Upper',
            'Lower':'!!Lower',
            'LargeCapacity':'!!LargeCapacity'
            }
    
    def __init__(self, parent=None):
        self.parent= parent
        
    def htmlToPdf(self, srcPath, destPath): #srcPathList per ridurre i processi?
        if os.path.isdir(destPath):
            baseName = os.path.splitext(os.path.basename(srcPath))[0]
            destPath=os.path.join(destPath, '%s.pdf' % baseName)
        result = call(['wk2pdf',srcPath,destPath])
        if result < 0:
            raise PrintHandlerError('wk2pdf error')
            
    def autoConvertFiles(self, files, storeFolder):
        resultList = []
        for filename in files:
            baseName,ext = os.path.splitext(os.path.basename(filename))
            if ext.lower() == '.html':
                destPath=os.path.join(storeFolder, '%s.pdf' % baseName)
                result = call(['wk2pdf',filename,destPath])
                if result < 0:
                    raise PrintHandlerError('wk2pdf error')
                resultList.append(destPath)
            elif ext.lower() =='.pdf':
                resultList.append(filename)
            else:
                raise 
        return resultList
    
    def getPrinters(self):
        printersBag=Bag()
        cups_connection = cups.Connection()
        for printer_name, printer in cups_connection.getPrinters().items():
            printer.update(dict(name=printer_name))
            printersBag.setItem('%s.%s'%(printer['printer-location'],printer_name),None,printer)
        return printersBag
        
    def getPrinterAttributes(self, printer_name):
        cups_connection = cups.Connection()
        printer_attributes = cups_connection.getPrinterAttributes(printer_name)
        attributesBag = Bag()
        for i,(media,description) in enumerate(self.paper_size.items()):
            if media in printer_attributes['media-supported']:
                attributesBag.setItem('paper_supported.%i'%i,None,id=media,caption=description)
        for i,(tray,description) in enumerate(self.paper_tray.items()):
            if tray in printer_attributes['media-supported']:
                attributesBag.setItem('tray_supported.%i'%i,None,id=tray,caption=description)
        return attributesBag
        
    def getPrinterConnection(self, printer_name=None, printerParams=None,**kwargs):
        return PrinterConnection(self, printer_name=printer_name, printerParams=printerParams,**kwargs)
        
            
            
        
