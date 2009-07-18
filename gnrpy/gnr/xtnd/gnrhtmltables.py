#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy web - see LICENSE for details
# module gnrstandardpages : Genro Web standard pages methods
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
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
"""
Created by Giovanni Porcari and Francesco Cavazzana on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""

import zipfile
import StringIO
import datetime

from gnr.core import gnrstring

from decimal import Decimal


class TableBuilder(object):
    def __init__(self, page, source=None, title='', tableclass='', thead='', row_template='', row_cb=None, skin='gnr_blue', 
                excel_nobr=None,
                header='', footer='', filename=None, tot_cb=None, row_template_totals=None, 
                locale=None, row_formatDict=None, row_maskDict=None,
                **kwargs):
        self.defaultFormats = {long:'#,##0', int:'#,##0', float:'#,##0.00', Decimal:'#,##0.00'}
        self.page = page # weakref was better ???
        self.source = source
        self.title = title
        self.tableclass = tableclass
        self.thead = thead
        self.row_template = row_template
        self.row_cb = row_cb
        self.skin = skin
        self.header = header
        self.footer = footer
        self.filename = filename
        self.tot_cb = tot_cb
        self.row_template_totals = row_template_totals
        self.locale = locale or page.locale
        self.row_formatDict = row_formatDict or {}
        self.row_maskDict = row_maskDict or {}
        self.kwargs = kwargs
        self.excel_nobr = excel_nobr
        
        self.response = self.page.response
        self.req = self.page.request
        self._counter = 0
        
    def _get_counter(self):
        self._counter = self._counter + 1
        return self._counter 
    counter = property(_get_counter)
        
    def sendFile(self, filename, mimetype, ext, content):
        content = content.encode('utf-8')
        filename = filename.replace(' ','_').replace('/','-').replace(':','-').encode('utf-8')
        if len(content) < 200000:
            self.response.content_type = mimetype
            self.response.add_header("Content-Disposition", "attachment; filename=%s.%s" % (filename, ext))
        else:
            self.response.content_type = 'application/zip'
            self.response.add_header("Content-Disposition", "attachment; filename=%s.zip" % filename)
            zipresult = StringIO.StringIO()
            zip = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
            zipstring = zipfile.ZipInfo('%s.%s' % (filename, ext), datetime.datetime.now().timetuple()[:6])
            zipstring.compress_type = zipfile.ZIP_DEFLATED
            zip.writestr(zipstring, content)
            zip.close()
            content = zipresult.getvalue()
            zipresult.close()
        self.response.add_header("Content-Length", str(len(content)))
        self.response.write(content)
        
    def requestWrite(self, html):
        self.response.write(html.encode('utf-8'))

    def fromList(self):
        yield '<thead>\n%s\n</thead><tbody>' % self.thead
        for row in self.source:
            yield self.buildTableRow(row)

    def fromServerCursor(self, n):
        cursor, serverfetch = self.source.serverfetch(n)
        description = cursor.description
        fields = [x[0] for x in description if x[0] !='pkey']
        thead = self.thead or '<tr>%s</tr>' % '\n'.join(['<th>%s</th>' %  self.source.tblstruct.columns.get(field,field).name_short for field in fields])
        self.row_template = self.row_template or '<tr value="$pkey" class="$odd_even">%s</tr>' % '\n'.join(['<td>$%s</td>' % field for field in fields])
        yield '<thead>\n%s\n</thead><tbody>' % thead
        
        rownum = 0
        for rows in serverfetch:
            result = [self.buildTableRow(row) for row in rows]
            rownum = rownum + len(rows)
            if result:
                yield '\n'.join(result)
        cursor.close() ## MIKI
                    
    def buildTableRow(self, row, totals=False):
        return self.templateReplaceRow(self.prepareTableRow(row), totals=totals)


    def templateReplaceRow(self, row, totals=False):
        if not row: return ''
        if totals or row.get('_gnr_tbl_footer'):
            row_template = '<tfoot>%s</tfoot>' % (self.row_template_totals or self.row_template)
        else:
            row_template = self.row_template
        return gnrstring.templateReplace(row_template, row, safeMode=True)# per debug

    def prepareTableRow(self, row, totals=False, excel=False, excel_nobr=False):
        row = dict(row)
        pkey = row.pop('pkey', None)
        i = self.counter
        if self.row_cb:
            # you can return a new row object or modify the current one: 
            # row is the actual db cursor, so maybe mutable or not
            row = self.row_cb(pkey, row, i) or row
        if not row: # if row_cb clean row object skip the whole row
            self._counter = self._counter - 1
            return ''
        
        for k,v in row.items():
            row[k] = gnrstring.toText(v, locale=self.locale, format=self.getColumnFormat(k, v), mask=self.row_maskDict.get(k)) or '&nbsp;'
            
        row['pkey'] = pkey or ''
        row['odd_even'] = 'odd_row' * (i % 2) or 'even_row'
        return row

    def getColumnFormat(self, k, v):
        return self.row_formatDict.get(k) or self.defaultFormats.get(type(v))
    
class StringTableBuilder(TableBuilder):
    def doTable(self):
        html = []
        openpage = gnrstring.templateReplace('<table class="full_page $tableclass" id="maintable">', dict(tableclass=self.tableclass))
        html.append(openpage)
        
        
        if hasattr(self.source, 'serverfetch'):
            rowsource = self.fromServerCursor(50)
        else:
            rowsource = self.fromList()
            
        html.extend(rowsource)
        
        html.append('</tbody>')
        if self.tot_cb:
            html.append(self.buildTableRow(self.tot_cb(), totals=True))
            
        html.append('</table>')
        return '\n'.join(html)


class PageTableBuilder(TableBuilder):
    def doTable(self):
        self.response.content_type = 'text/html'
        
        self.requestWrite(self.openPage())
        
        if hasattr(self.source, 'serverfetch'):
            rowsource = self.fromServerCursor(5)
        else:
            rowsource = self.fromList()
            
        for html in rowsource:
            self.requestWrite(html)
        self.requestWrite('</tbody>')
        if self.tot_cb:
            self.requestWrite(self.buildTableRow(self.tot_cb(), totals=True))
            
        self.requestWrite(self.closePage())

    def openPage(self):
        html="""
    <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <style type="text/css">    
                $all_css
            </style>
            
            <script type="text/javascript">
                var genro = window.parent.genro;
            </script>
            <title>$title</title>
        </head>
        <body class="$bodyclasses tableWindow">
            $header
            <table class="full_page $tableclass" id="maintable">
            """
        all_css = []
        self.page.theme = getattr(self.page,'theme','tundra')
        styles = self.page.get_css_genro()
        print_styles = styles.pop('print', [])

        for cssmedia, cssnames  in styles.items():
            for cssname in cssnames:
                all_css.append('@import url("%s") %s;' % (cssname, cssmedia))
        
        for cssname in print_styles:
            all_css.append('@import url("%s") print;' % (cssname, ))

        
        cssname = self.page.getResourceUri('html_tables/html_tables','css')
        all_css.append('@import url("%s") %s;' % (cssname, 'all'))
        
        cssname = self.page.getResourceUri('html_tables/html_tables_print','css')
        all_css.append('@import url("%s") %s;' % (cssname, 'print'))
        
        for cssname in self.page.get_css_requires():
            all_css.append('@import url("%s");' % cssname)
        
        html = gnrstring.templateReplace(html, dict(all_css='\n'.join(all_css), 
                                                    bodyclasses = self.page.get_bodyclasses(),
                                                    title=self.title, header=self.header, 
                                                    tableclass=self.tableclass))
        return html
        
    def closePage(self):
        html = """
            </table>
            %s
        </body>
    </html>"""
        return html % self.footer
        

class ExcelTableBuilder(TableBuilder):
    def doTable(self):
        if hasattr(self.source, 'serverfetch'):
            rowsource = self.fromServerCursor(50)
        else:
            rowsource = self.fromList()
            
        result = list(rowsource)
        result.append('</tbody>')
        if self.tot_cb:
            result.append(self.buildTableRow(self.tot_cb(), totals=True))
            
        result = self.templatePageExcel() % (self.header, '\n'.join(result), self.footer)
        result = result.replace('<br />','')
        
        filename = self.filename or self.req.uri.split('/')[-1]
        self.sendFile(filename, 'application/vnd.ms-excel', 'xls', result)
        
    def buildTableRow(self, row, totals=False):
        row = self.prepareTableRow(row)
        if not row: return ''
        if self.excel_nobr:
            for k,v in row.items():
                if '\n' in v or '<br />' in v.lower():
                    row[k] = v.replace('\n',' ').replace('<br />', ' ')
        return self.templateReplaceRow(row)

    
    def templatePageExcel(self):
        return """
    <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <style type="text/css" title="text/css">
                <!--
                body{background-color: transparent;}
                table{background-color: transparent;}
                -->
            </style>
        </head>
        <body>
            %s
            <table border='1px'>
                %s
            </table>
            %s
        </body>
    </html>
        """
    
def tablePage(page, source=None, title='', tableclass='', thead='', row_template='', row_cb=None, skin='gnr_blue', 
                excel=None,
                header='', footer='', filename=None, tot_cb=None, row_template_totals=None, 
                locale=None, row_formats=None,
                **kwargs):
    if excel:
        factory = ExcelTableBuilder
    else:
        factory = PageTableBuilder
    builder = factory(page, source=source, title=title, tableclass=tableclass, thead=thead, row_template=row_template, 
                           row_cb=row_cb, skin=skin, 
                           header=header, footer=footer, filename=filename, tot_cb=tot_cb, row_template_totals=row_template_totals, 
                           locale=locale, row_formats=row_formats,
                           **kwargs)
    return builder.doTable()

def tableHtml(page, source=None, title='', tableclass='', thead='', row_template='', row_cb=None, skin='gnr_blue', 
                excel=None,
                header='', footer='', filename=None, tot_cb=None, row_template_totals=None, 
                locale=None, row_formats=None,
                **kwargs):
    if excel:
        factory = ExcelTableBuilder
    else:
        factory = StringTableBuilder
    builder = factory(page, source=source, title=title, tableclass=tableclass, thead=thead, row_template=row_template, 
                           row_cb=row_cb, skin=skin, 
                           header=header, footer=footer, filename=filename, tot_cb=tot_cb, row_template_totals=row_template_totals, 
                           locale=locale, row_formats=row_formats,
                           **kwargs)
    return builder.doTable()


class RowFormatter(object):
    def __init__(self, locale, colformats=None, typeformats=None, colmasks=None, emptyValue='&nbsp;'):
        self.locale = locale
        self.colformats = colformats or {}
        self.colmasks = colmasks or {}
        self.typeformats = {int:'#,##0', long:'#,##0', float:'#,##0.00', Decimal:'#,##0.00'}
        if typeformats:
            self.typeformats.update(typeformats)
        self.emptyValue = emptyValue
        
    def __call__(self, row):
        result = {}
        for k,v in row.items():
            result[k] = gnrstring.toText(v, locale = self.locale, 
                                            format = self.colformats.get(k) or self.typeformats.get(type(v)), 
                                            mask = self.colmasks.get(k)
                                        ) or self.emptyValue
        return result
        
        
class RowOddEven(object):
    def __init__(self):
        self.i = 0
    
    def __call__(self, row):
        self.i += 1
        return {'odd_even': 'odd_row' * (self.i % 2) or 'even_row'}
