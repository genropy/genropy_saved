#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

from builtins import str
import os

from gnr.lib.services.htmltopdf import HtmlToPdfService,HtmlToPdfError

class Service(HtmlToPdfService):
    def writePdf(self,srcPath, destPath, orientation=None, page_height=None, page_width=None,
                        pdf_kwargs=None,htmlTemplate=None,bodyStyle=None,**kwargs):
        srcPath = self.parent.storageNode(srcPath, parent=self.parent)
        destPath = self.parent.storageNode(destPath, parent=self.parent)

        pdf_kwargs['orientation'] = orientation or 'Portrait'

        # D&D: qualunque cosa venga fatta con height e width, in ogni caso questi due valori
        # vengono "discarded" alle righe 34 e 35. Quindi...
        # if page_height:
        #     if pdf_kwargs['orientation'] == 'Portrait':
        #         pdf_kwargs['page_height'] = page_height
        #     else:
        #         pdf_kwargs['page_width'] = page_height
        # if page_width:
        #     if pdf_kwargs['orientation'] == 'Portrait':
        #         pdf_kwargs['page_width'] = page_width
        #     else:
        #         pdf_kwargs['page_height'] = page_width
        if not 'quiet' in pdf_kwargs:
            pdf_kwargs['quiet'] = True

        args = ['wkhtmltopdf']

        pdf_kwargs.pop('page_height', None)
        pdf_kwargs.pop('page_width', None)

        for k,v in list(pdf_kwargs.items()):
            if v is not False and v is not None and v!='':
                args.append('--%s' %k.replace('_','-'))
                if v is not True:
                    args.append(str(v))

        # We need to zoom on Windows platform. Bug?
        import platform
        if platform.system() in ['Windows','Darwin']:
            args.extend(['--zoom', '1.25'])

        if destPath.isdir:
            baseName = os.path.splitext(srcPath.basename)[0]
            destPath = destPath.child('%s.pdf' % baseName)
        args.append(srcPath)
        args.append(destPath)

        service = destPath.service
        result = service.call(args)  # wkhtmlto pdf -O Landscape fdfsdfds.html ddasda.pdf

       #if sys.platform.startswith('linux'):
       #    result = call(['wkhtmltopdf', '-q', '-O', orientation, srcPath, destPath])
       #else:
       #    result = call(['wkhtmltopdf', '-q', '-O', orientation, srcPath, destPath,])
        if result < 0:
            raise HtmlToPdfError('wkhtmltopdf error')
        return destPath.fullpath.replace('_raw_:', '')