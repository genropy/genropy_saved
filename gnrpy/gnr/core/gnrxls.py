import xlwt
import os
from gnr.core.gnrstring import toText

class XlsWriter(object):
    """TODO"""
    def __init__(self, columns=None, coltypes=None, headers=None, filepath=None,
                 font='Times New Roman', format_float='#,##0.00', format_int='#,##0', locale=None):
        self.headers = headers
        self.columns = columns
        self.filepath = '%s.xls' % os.path.splitext(filepath)[0]
        self.workbook = xlwt.Workbook(encoding='latin-1')
        self.sheet = self.workbook.add_sheet(os.path.basename(self.filepath)[:31])
        self.coltypes = coltypes
        self.locale = locale
        
        self.float_style = xlwt.XFStyle()
        self.float_style.num_format_str = format_float
        self.int_style = xlwt.XFStyle()
        self.int_style.num_format_str = format_int
        font0 = xlwt.Font()
        font0.name = 'font'
        font0.bold = True
        
        self.hstyle = xlwt.XFStyle()
        self.hstyle.font = font0
        
        self.sheet.panes_frozen = True
        self.sheet.horz_split_pos = 1
        self.colsizes = dict()
        
    def __call__(self, data=None):
        self.writeHeaders()
        for item in data:
            row = self.rowGetter(item)
            self.writeRow(row)
        self.workbookSave()
        
    def rowGetter(self, item):
        """TODO
        
        :param item: TODO"""
        return dict(item)
        
    def writeHeaders(self):
        """TODO"""
        for c, header in enumerate(self.headers):
            self.sheet.write(0, c, header, self.hstyle)
            self.colsizes[c] = max(self.colsizes.get(c, 0), self.fitwidth(header))
        self.current_row = 0
        
    def workbookSave(self):
        """TODO"""
        self.workbook.save(self.filepath)
        
    def writeRow(self, row):
        """TODO
        
        :param row: TODO"""
        self.current_row += 1
        for c, col in enumerate(self.columns):
            value = row.get(col)
            if isinstance(value, list):
                value = ','.join([str(x != None and x or '') for x in value])
            coltype = self.coltypes.get(col)
            if coltype in ('R', 'F', 'N'):
                self.sheet.write(self.current_row, c, value, self.float_style)
            elif coltype in ('L', 'I'):
                self.sheet.write(self.current_row, c, value, self.int_style)
            else:
                value = toText(value, self.locale)
                self.sheet.write(self.current_row, c, value)
            self.colsizes[c] = max(self.colsizes.get(c, 0), self.fitwidth(value))
            
    def fitwidth(self, data, bold=False):
        """Try to autofit Arial 10
        
        :param data: TODO
        :param bold: TODO"""
        charwidths = {
            '0': 262.637, '1': 262.637, '2': 262.637, '3': 262.637, '4': 262.637, '5': 262.637, '6': 262.637,
            '7': 262.637, '8': 262.637, '9': 262.637, 'a': 262.637, 'b': 262.637, 'c': 262.637, 'd': 262.637,
            'e': 262.637, 'f': 146.015, 'g': 262.637, 'h': 262.637, 'i': 117.096, 'j': 88.178, 'k': 233.244,
            'l': 88.178, 'm': 379.259, 'n': 262.637, 'o': 262.637, 'p': 262.637, 'q': 262.637, 'r': 175.407,
            's': 233.244, 't': 117.096, 'u': 262.637, 'v': 203.852, 'w': 321.422, 'x': 203.852, 'y': 262.637,
            'z': 233.244, 'A': 321.422, 'B': 321.422, 'C': 350.341, 'D': 350.341, 'E': 321.422, 'F': 291.556,
            'G': 350.341, 'H': 321.422, 'I': 146.015, 'J': 262.637, 'K': 321.422, 'L': 262.637, 'M': 379.259,
            'N': 321.422, 'O': 350.341, 'P': 321.422, 'Q': 350.341, 'R': 321.422, 'S': 321.422, 'T': 262.637,
            'U': 321.422, 'V': 321.422, 'W': 496.356, 'X': 321.422, 'Y': 321.422, 'Z': 262.637, ' ': 146.015,
            '!': 146.015, '"': 175.407, '#': 262.637, '$': 262.637, '%': 438.044, '&': 321.422, '\'': 88.178,
            '(': 175.407, ')': 175.407, '*': 203.852, '+': 291.556, ',': 146.015, '-': 175.407, '.': 146.015,
            '/': 146.015, ':': 146.015, ';': 146.015, '<': 291.556, '=': 291.556, '>': 291.556, '?': 262.637,
            '@': 496.356, '[': 146.015, '\\': 146.015, ']': 146.015, '^': 203.852, '_': 262.637, '`': 175.407,
            '{': 175.407, '|': 146.015, '}': 175.407, '~': 291.556}
        units = 220
        for char in str(data):
            if char in charwidths:
                units += charwidths[char]
            else:
                units += charwidths['0']
        if bold:
            units *= 1.1
        return max(units, 700) # Don't go smaller than a reported width of 2
            
class XlsReader(object):
    """docstring for XlsReader"""
    def __init__(self, arg):
        self.arg = arg  