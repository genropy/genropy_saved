# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
try:
    from gnr.pdf.gnrrml import GnrPdf
    
    class GnrWebPDF(GnrPdf):
        def getPdf(self, table, record, filename=None, folder=None):
            record = self.db.table(table).recordAs(record, mode='bag')
            self.filename = filename or self.getFilename(record)
            self.filePath = self.page.temporaryDocument(folder, self.filename)
            self.fileUrl = self.page.temporaryDocumentUrl(folder, self.filename)
            self.createStory(record)
except ImportError:
    class GnrWebPDF(object):
        """TODO"""
        def getPdf(self, *args, **kwargs):
            pass
            
def plain_redirect (page, params):
    """Return the following string::
    
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
        <html lang="en">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <script>
                    window.location = '%s?%s';
                </script>
            </head>
            <body>
            </body>
        </html>
    
    where in place of the first ``%s`` goes the *page* parameter
    and in the second ``%s`` goes the *params* parameter.
    
    :param page: TODO
    :param params: TODO"""
    return """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
    <html lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <script>
                window.location = '%s?%s';
        </script>
        </head>
        <body>
        </body>
        </html>
""" % (page, params)