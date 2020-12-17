#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

import os
import tempfile

from gnr.core.gnrdecorator import extract_kwargs

from gnr.core.gnrlang import  GnrException


from gnr.lib.services import GnrBaseService,BaseServiceType
from gnr.lib.services.storage import StorageNode


class HtmlToPdfError(GnrException):
    pass
    

class ServiceType(BaseServiceType):
    def conf_htmltopdf(self):
        return dict(implementation='wk')


class HtmlToPdfService(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def printBodyStyle(self):
        return "font-size:12px;font-family: Arial, Verdana, sans-serif;margin-top:0;margin-bottom:0;margin-left:0;margin-right:0;-webkit-text-size-adjust:auto;"

    def standardPageHtmlTemplate(self,bodyStyle=None):
        bodyStyle = bodyStyle or self.printBodyStyle()
        head ="""<head> 
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
                    <style> 
                        .gnrlayout{position:absolute;} 
                        body{%s}
                        .letterhead_page{page-break-before:always;} 
                        .letterhead_page:first-child{page-break-before:avoid;}
                    </style>
                </head>
                     """%bodyStyle
        body = "<body>%s</body>"
        return """<html> 
                    %s 
                    %s
                 </html>""" %(head,body)

    def createTempHtmlFile(self,htmlText,htmlTemplate=None,bodyStyle=None):
        if not '<html' in htmlText:
            htmlTemplate = htmlTemplate or self.standardPageHtmlTemplate(bodyStyle)
            htmlText = htmlTemplate %htmlText
        tmp = tempfile.NamedTemporaryFile(prefix='temp', suffix='.html',delete=False)
        tmp.write(htmlText.encode())
        url = tmp.name
        tmp.close()
        return url
    

    @extract_kwargs(pdf=True)
    def htmlToPdf(self, srcPath, destPath, orientation=None, page_height=None, 
                page_width=None, pdf_kwargs=None,htmlTemplate=None,bodyStyle=None): #srcPathList per ridurre i processi?
            
        """TODO
        
        :param src_path: TODO
        :param destPath: TODO
        :param orientation: TODO"""

        if not isinstance(srcPath, StorageNode) and '<' in srcPath:
            srcPath = self.createTempHtmlFile(srcPath,htmlTemplate=htmlTemplate,bodyStyle=bodyStyle)
            self.htmlToPdf(srcPath,destPath,orientation,pdf_kwargs=pdf_kwargs)
            os.remove(srcPath)
            return
        srcNode = self.parent.storageNode(srcPath)
        destNode = self.parent.storageNode(destPath)
        pdf_pref = self.parent.getPreference('.pdf_render',pkg='sys') if self.parent else None
        #preference should be in sys.service service_parameters
        keep_html = False
        if pdf_pref:
            pdf_pref = pdf_pref.asDict(ascii=True)
            keep_html = pdf_pref.pop('keep_html', False)
            pdf_kwargs = pdf_kwargs or dict()
            pdf_pref.update(pdf_kwargs)
            pdf_kwargs = pdf_pref
        if keep_html:
            import shutil
            from datetime import datetime, date
            now = datetime.now()
            baseName = destNode.cleanbasename
            debugName = "%s_%02i_%02i_%02i.html"%(baseName, now.hour,now.minute,now.second)
            htmlfilenode = self.parent.storageNode('site:print_debug',
                date.today().isoformat(), debugName ,autocreate=-1)
            srcNode.copy(htmlfilenode)

        return self.writePdf(srcPath, destPath, orientation=orientation, page_height=page_height, 
                    page_width=page_width, pdf_kwargs=pdf_kwargs,
                    htmlTemplate=htmlTemplate,bodyStyle=bodyStyle)
        
    
    def writePdf(self,srcPath, destPath, orientation=None, page_height=None, page_width=None, 
                        pdf_kwargs=None,htmlTemplate=None,bodyStyle=None,**kwargs):
        #override
        pass

