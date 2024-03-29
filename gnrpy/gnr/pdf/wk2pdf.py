#!/usr/bin/env python
from __future__ import print_function
from past.builtins import basestring
#from builtins import object
import sys
import signal
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkAccessManager
import optparse
import tempfile
import os

UNIT_RE = r'^([\d\.]+)(\D*)$'
HOST_PORT_RE = r'^[a-zA-Z\.]+\:[0-9]*$'
URL_RE = r'^[a-zA-Z]+\:.*'
class WK2pdf(object):
    option_defaults = {
        "disable_javascript": False,
        "dpi": -1,
        "colorMode": True,
        "resolution": False,
        "margin_bottom": '10mm',
        "margin_left": '10mm',
        "margin_right": '10mm',
        "margin_top": '10mm',
        "background": True,
        "user_style_sheet": '',
        "orientation": 'V',
        "pageSize": 'A4',
        "proxy": False,
        "quiet": True,
        "jsredirectwait": 200,
        "enable_plugins": False,
        "use_x11": False
    }
    page_sizes = {
        'A0': QPrinter.A0, 'B1': QPrinter.B1, 'A5': QPrinter.A5, 'B6': QPrinter.B6,
        'A1': QPrinter.A1, 'B2': QPrinter.B2, 'A6': QPrinter.A6, 'B7': QPrinter.B7,
        'A2': QPrinter.A2, 'B3': QPrinter.B3, 'A7': QPrinter.A7, 'B8': QPrinter.B8,
        'A3': QPrinter.A3, 'B4': QPrinter.B4, 'A8': QPrinter.A8, 'B9': QPrinter.B9,
        'A4': QPrinter.A4, 'B5': QPrinter.B5, 'A9': QPrinter.A9, 'B0': QPrinter.B0,
        'C5E': QPrinter.C5E, 'COMM10E': QPrinter.Comm10E, 'DLE': QPrinter.C5E,
        'Executive': QPrinter.Executive, 'Folio': QPrinter.Folio, 'Ledger': QPrinter.Ledger,
        'Legal': QPrinter.Legal, 'Letter': QPrinter.Letter, 'Tabloid': QPrinter.Tabloid
    }

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        self.option_defaults.update(kwargs)
        for k, v in list(self.option_defaults.items()):
            if isinstance(v, basestring):
                if k in ['margin_left', 'margin_right', 'margin_top', 'margin_bottom']:
                    v = self.parseUnitReal(v)
                if k == 'pageSize':
                    v = self.setPageSize(v)
                if k == 'orientation':
                    v = self.setOrientation(v)
            if k == 'colorMode':
                v = self.setColorMode(v)
            setattr(self, k, v)

        if len(args) < 2:
            self.app.quit(1)
            raise Exception(
                    'You need to specify atleast one input file, and exactly one output file\nUse - for stdin or stdout\n\n')
        args = list(args)
        self.out = args.pop(-1)
        self.in_ = args
        self.pageNum = 0
        self.pages = []
        self.am = QNetworkAccessManager()
        self.am.connect(self.am, SIGNAL("sslErrors(QNetworkReply*, const QList<QSslError>&)"), self.sslErrors)
        self.loading = 0
        self.quiet = True

    def guessUrlFromString(self, url):
        url = url.strip()
        host_re = re.compile(HOST_PORT_RE)
        if host_re.match(url):
            url = 'http://%s' % url
        url_re = re.compile(URL_RE)
        if url_re.match(url):
            url = QUrl(url, QUrl.TolerantMode)
            if url.isValid():
                return url
        elif os.path.isfile(url):
            return QUrl.fromLocalFile(os.path.abspath(url))
        else:
            splitted_url = url.split('.')
            if len(splitted_url) > 1:
                prefix = splitted_url[0]
                schema = prefix.lower() == 'ftp' and 'ftp' or 'http'
                return QUrl('%s://%s' % (schema, url), QUrl.TolerantMode)

    def loadDefaults(self):
        self.pageSize = QPrinter.A4
        self.orientation = QPrinter.Portrait

    def setPageSize(self, size):
        self.pageSize = self.page_sizes.get(size.upper())
        return self.pageSize

    def setOrientation(self, orientation):
        if orientation.lower() in ['l', 'landscape']:
            return QPrinter.Landscape
        return QPrinter.Portrait

    def setColorMode(self, colorMode):
        if not colorMode:
            return QPrinter.GrayScale
        return QPrinter.Color

    def parseUnitReal(self, string):
        scale = 1.0
        unit = QPrinter.Millimeter
        r = re.compile(UNIT_RE)
        parsed = r.match(string)
        if not parsed:
            return
        number = float(parsed.group(1))
        unit_text = parsed.group(2).lower()
        if unit_text in ['', 'mm', 'millimeter']:
            scale = 1.0
        elif unit_text in ['cm', 'centimeter']:
            scale = 10.0
        elif unit_text in ['m', 'meter']:
            scale = 1000.0
        elif unit_text in ['didot']:
            unit = QPrinter.Didot
        elif unit_text in ['in', 'inch']:
            unit = QPrinter.Inch
        elif unit_text in ['pc', 'pica']:
            unit = QPrinter.Pica
        elif unit_text in ['cicero']:
            unit = QPrinter.Cicero
        elif unit_text in ['px', 'pixel']:
            unit = QPrinter.DevicePixel
        elif unit_text in ['m', 'meter']:
            unit = QPrinter.Point
        elif unit in ['point', 'pt']:
            unit = QPrinter.Point
        return number * scale, unit


    def resetPages(self):
        self.pages = []
        self.pageStart = []

    def hfreplace(self, q):
        replaces = []
        #replaces.append(("[page]",pageNum))
        #replaces.append(("[toPage]",str(self.pageStart[-1])))
        #replaces.append(("[fromPage]",str(1)))
        #replaces.append(("[section]",sec[0]))
        #replaces.append(("[subsection]",sec[1]))
        #replaces.append(("[subsubsection]",sec[3]))
        #replaces.append(("[webpage]",currentPage ==-1 and "Table Of Content" or index[currentPage]))
        for tag, replace in replaces:
            q = q.replace(tag, replace)
        return q

    def newPage(self, printer, f, t, p):
        self.pageNum += 1
        painter = printer.paintEngine().painter()
        painter.save();
        painter.resetMatrix();
        h = printer.pageRect().height();
        w = printer.pageRect().width();
        # do stuff like header and footer
        painter.restore();


    def run(self):
        for in_url in self.in_:
            webpage = QWebPage()
            webpage.setNetworkAccessManager(self.am)
            webpage.connect(webpage, SIGNAL('loadProgress(int)'), self.loadProgress)
            webpage.connect(webpage, SIGNAL('loadFinished(bool)'), self.loadFinished)
            webpage.connect(webpage, SIGNAL('loadStarted()'), self.loadStarted)
            webpage.settings().setAttribute(QWebSettings.JavaEnabled, self.enable_plugins)
            webpage.settings().setAttribute(QWebSettings.JavascriptEnabled, not self.disable_javascript)
            webpage.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, False)
            webpage.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, False)
            webpage.settings().setAttribute(QWebSettings.PrintElementBackgrounds, self.background)
            webpage.settings().setAttribute(QWebSettings.PluginsEnabled, self.enable_plugins)
            if self.user_style_sheet:
                webpage.settings().setUserStyleSheetUrl(self.guessUrlFromString(self.user_style_sheet))
            url = in_url
            if url == '-':
                tmp = tempfile.NamedTemporaryFile(prefix='tmp', suffix='.html')
                tmp.write(sys.stdin.read())
                url = tmp.name
            url = self.guessUrlFromString(url)
            webpage.mainFrame().load(url)
            self.pages.append(webpage)


    def sslErrors(self, reply, error):
        reply.ignoreSslErrors()

    def printPage(self):
        if self.loading:
            return
        printer = QPrinter()
        painter = QPainter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(self.out)
        self.pageNum = 0;
        self.currentPage = 0;
        if not (self.margin_left[1] == self.margin_right[1] == self.margin_top[1] == self.margin_bottom[1]):
            raise Exception("Currently all margin units must be the same!")
        printer.setPageMargins(self.margin_left[0], self.margin_top[0], self.margin_right[0], self.margin_bottom[0],
                               self.margin_left[1])
        printer.setPageSize(self.pageSize)
        printer.setOrientation(self.orientation)
        printer.setColorMode(self.colorMode)
        if not printer.isValid():
            self.app.quit(1)
            raise Exception("Unable to write to output file")
        while len(self.pages):
            page = self.pages.pop(0)
            page.mainFrame().print_(printer)
            if self.pages:
                printer.newPage()
        self.app.quit()

    def loadFinished(self, ok):
        self.loading -= 1
        #if not ok:
        #    raise Exception("Failed loading page")
        if not self.quiet:
            print("Waiting for redirect")

        if self.loading == 0:
            QTimer.singleShot(self.jsredirectwait, self.printPage)


    def loadStarted(self):
        self.loading += 1

    def loadProgress(self, progress):
        if not self.quiet:
            print("Loading page: %02i\r" % progress)

    def exec_(self):
        return self.app.exec_()

usage = """Usage: wkhtmltopdf [OPTION]... <input file> [more input files] <output file>\nconverts htmlpages into a pdf\n"""

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = optparse.OptionParser(usage)
    parser.add_option('-n', '--disable-javascript', dest="disable_javascript", default=False, action="store_true",
                      help="Do not allow webpages to run javascript")
    parser.add_option('-d', '--dpi', dest="dpi", default=-1, help="Change the dpi explicitly")
    parser.add_option('-g', '--grayscale', dest="colorMode", default=True, action="store_false",
                      help="PDF will be generated in grayscale")
    parser.add_option('-l', '--lowquality', dest="resolution", default=False, action="store_true",
                      help="Generates lower quality pdf/ps. Useful to shrink the result document space")
    parser.add_option('-B', '--margin-bottom', dest="margin_bottom", default='10mm',
                      help="Set the page bottom margin (default 10mm)")
    parser.add_option('-L', '--margin-left', dest="margin_left", default='10mm',
                      help="Set the page left margin (default 10mm)")
    parser.add_option('-R', '--margin-right', dest="margin_right", default='10mm',
                      help="Set the page right margin (default 10mm)")
    parser.add_option('-T', '--margin-top', dest="margin_top", default='10mm',
                      help="Set the page top margin (default 10mm)")
    parser.add_option('--no-background', dest="background", default=True, action="store_false",
                      help="Do not print background")
    parser.add_option('--user-style-sheet', dest="user_style_sheet", default='',
                      help="Specify a user style sheet, to load with every page")
    parser.add_option('-O', '--orientation', dest="orientation", default='V',
                      help="Set orientation to Landscape or Portrait")
    parser.add_option('-s', '--page-size', dest="pageSize", default='A4', help="Set pape size to: A4, Letter, ect.")
    parser.add_option('-p', '--proxy', dest="proxy", default=True, action="store_false", help="Use a proxy")
    parser.add_option('-q', '--quiet', dest="quiet", default=False, action="store_true", help="Be less verbose")
    parser.add_option('--redirect-delay', dest="jsredirectwait", default=200,
                      help="Wait some miliseconds for js-redirects")
    parser.add_option('-V', '--version', dest="version", action="store_false",
                      help="Output version information an exit")
    parser.add_option('--enable-plugins', dest="enable_plugins", default=False, action="store_true",
                      help="Enable installed plugins (such as flash)")
    parser.add_option('--use-xserver', dest="use_x11", default=False, action="store_true",
                      help="Use the X server (some plugins and other stuff might not work without X11)")
    (options, args) = parser.parse_args()
    wkprinter = WK2pdf(*args, **(options.__dict__))
    wkprinter.run()
    sys.exit(wkprinter.exec_())
