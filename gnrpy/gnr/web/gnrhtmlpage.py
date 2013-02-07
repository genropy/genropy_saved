#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package            : GenroPy web - see LICENSE for details
# module gnrhtmlpage : Genro Web structures implementation
# Copyright (c)      : 2004 - 2009 Softwell sas - Milano 
# Written by         : Giovanni Porcari, Michele Bertoldi
#                      Saverio Porcari, Francesco Porcari
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
from gnr.core.gnrhtml import GnrHtmlSrc, GnrHtmlBuilder
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrstring import  splitAndStrip



class GnrHtmlDojoSrc(GnrHtmlSrc):
    html_base_NS = ['a', 'abbr', 'acronym', 'address', 'area', 'base', 'bdo', 'big', 'blockquote',
                    'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
                    'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset', 'head', 'hr', 'html',
                    'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'link', 'map', 'meta', 'noframes',
                    'noscript', 'object', 'ol', 'optgroup', 'option', 'param', 'samp', 'select', 'style',
                    'sub', 'sup', 'table', 'tbody', 'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt',
                    'ul', 'var']
                    
    gnrNS = ['layout', 'row', 'cell','chart2D']
        
    html_autocontent_NS = ['div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'td', 'li', 'b', 'i', 'small', 'strong',
                           'p', 'pre', 'q', ]
                           
    htmlNS = html_base_NS + html_autocontent_NS
        
    widgetcatalog = {'CheckBox': 'dijit.form.CheckBox',
                     'RadioButton': 'dijit.form.CheckBox',
                     'ComboBox': 'dijit.form.ComboBox',
                     'CurrencyTextBox': 'dijit.form.CurrencyTextBox',
                     'DateTextBox': 'dijit.form.DateTextBox',
                     'FilteringSelect': 'dijit.form.FilteringSelect',
                     'InlineEditBox': 'dijit.InlineEditBox',
                     'NumberSpinner': 'dijit.form.NumberSpinner',
                     'NumberTextBox': 'dijit.form.NumberTextBox',
                     'HorizontalSlider': 'dijit.form.Slider',
                     'VerticalSlider': 'dijit.form.Slider',
                     'SimpleTextarea': 'dijit.form.SimpleTextarea',
                     'MultiSelect': 'dijit.form.MultiSelect',
                     'TextBox': 'dijit.form.TextBox',
                     'TimeTextBox': 'dijit.form.TimeTextBox',
                     'ValidationTextBox': 'dijit.form.ValidationTextBox',
                     'AccordionContainer': 'dijit.layout.AccordionContainer',
                     'AccordionPane': 'dijit.layout.AccordionContainer',
                     'ContentPane': 'dijit.layout.ContentPane',
                     'BorderContainer': 'dijit.layout.BorderContainer',
                     'LayoutContainer': 'dijit.layout.LayoutContainer',
                     'SplitContainer': 'dijit.layout.SplitContainer',
                     'StackContainer': 'dijit.layout.StackContainer',
                     'TabContainer': 'dijit.layout.TabContainer',
                     'Button': 'dijit.form.Button',
                     'ToggleButton': 'dijit.form.Button',
                     'ComboButton': 'dijit.form.Button,dijit.Menu',
                     'DropDownButton': 'dijit.form.Button,dijit.Menu',
                     'Menu': 'dijit.Menu',
                     'MenuItem': 'dijit.Menu',
                     'MenuSeparator': 'dijit.Menu',
                     'PopupMenuItem': 'dijit.Menu',
                     'Toolbar': 'dijit.Toolbar',
                     'Dialog': 'dijit.Dialog',
                     'TooltipDialog': 'dijit.Dialog',
                     'ProgressBar': 'dijit.ProgressBar',
                     'TitlePane': 'dijit.TitlePane',
                     'Tooltip': 'dijit.Tooltip',
                     'ColorPalette': 'dijit.ColorPalette',
                     'Editor': 'dijit.Editor,dijit._editor.plugins.LinkDialog,dijit._editor.plugins.FontChoice,dijit._editor.plugins.TextColor'
                     ,
                     'Tree': 'dijit.Tree',
                     'FloatingPane': 'dojox.layout.FloatingPane',
                     'RadioGroup': 'dojox.layout.RadioGroup',
                     'ResizeHandle': 'dojox.layout.ResizeHandle',
                     'SizingPane': 'dojox.layout.SizingPane',
                     'FisheyeList': 'dojox.widget.FisheyeList',
                     'Loader': 'dojox.widget.Loader',
                     'Toaster': 'dojox.widget.Toaster',
                     'FileInput': 'dojox.widget.FileInput',
                     'FileInputBlind': 'dojox.widget.FileInputAuto',
                     'FileInputAuto': 'dojox.widget.FileInputAuto',
                     'ColorPicker': 'dojox.widget.ColorPicker',
                     'SortList': 'dojox.widget.SortList',
                     'TimeSpinner': 'dojox.widget.TimeSpinner',
                     'Iterator': 'dojox.widget.Iterator',
                     'Gallery': 'dojox.image.Gallery',
                     'Lightbox': 'dojox.image.Lightbox',
                     'SlideShow': 'dojox.image.SlideShow',
                     'ThumbnailPicker': 'dojox.image.ThumbnailPicker',
                     'Deck': 'dojox.presentation.Deck',
                     'Slide': 'dojox.presentation.Slide',
                     'Grid': 'dojox.grid.Grid:dojox.Grid',
                     'VirtualGrid': 'dojox.grid.VirtualGrid:dojox.VirtualGrid',
                     'Calendar': 'mywidgets.widget.Calendar,mywidgets.widget.Timezones',
                     'GoogleMap': ''

    };
    widgetNS = widgetcatalog.keys()
    gnr_dojoNS = []
    htmlNS = html_base_NS + html_autocontent_NS
    genroNameSpace = dict([(name.lower(), name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(), name) for name in gnrNS]))
    genroNameSpace.update(dict([(name.lower(), name) for name in widgetNS]))
    genroNameSpace.update(dict([(name.lower(), name) for name in gnr_dojoNS]))


class GnrHtmlPage(GnrWebPage):
    srcfactory = GnrHtmlSrc
    
    def __init__disabled_(self, site=None, request=None, response=None, request_kwargs=None, request_args=None,
                          filepath=None, packageId=None, basename=None):
        self.packageId = packageId
        self.filepath = filepath
        self.site = site
        
        self._call_args = request_args or tuple()
        self._call_kwargs = request_kwargs or {}
        self._user_login = None
        self._user = None
        
    def main(self, *args, **kwargs):
        pass

    def setCssRequires(self):
        css_import_statements_list=[]
        css_requires = getattr(self, 'css_requires', [])
        css_requires.extend([k.split('.')[0] for k in self.dynamic_css_requires.keys()])
        for css_require in css_requires:
             urls =self.getResourceExternalUriList(css_require,'css') or []
             for url in urls:
                css_import_statements_list.append('@import url("%s")' %url)
        if css_import_statements_list:
            import_statements = ';\n    '.join(css_import_statements_list)
            self.builder.head.style(import_statements + ';\n', type="text/css")

    def setJsRequires(self):
        js_requires = getattr(self, 'js_requires', [])
        js_requires.extend([k.split('.')[0] for k in self.dynamic_js_requires.keys()])
        for js_require in js_requires:
             urls =self.getResourceExternalUriList(js_require,'js',add_mtime=True) or []
             for url in urls:
                self.body.script(src=url)
        
    def gnr_css(self):
        css_genro = self.get_css_genro()
        for css_media, css_link in css_genro.items():
            import_statements = ';\n'.join(css_link)
            self.builder.head.style(import_statements + ';', type="text/css", media=css_media)

    def gnr_js(self):
        pass
            
    def rootPage(self, *args, **kwargs):
        self.builder.initializeSrc(_class=self.theme)
        self.body = self.builder.body
        kwargs = kwargs or {}
        if 'dojo_theme' in kwargs:
            self.theme = kwargs.pop('dojo_theme')
        if 'pagetemplate' in kwargs:
            self.theme = kwargs.pop('pagetemplate')
        self.setJsRequires()
        self.setCssRequires()

        
        self.main(self.body, *args, **kwargs)
        return self.builder.toHtml()
        
    def onPreIniting(self, request_args=None, request_kwargs=None):
        self.builder = GnrHtmlBuilder(srcfactory=self.srcfactory)
        

        
class GnrHtmlDojoPage(GnrHtmlPage):
    srcfactory = GnrHtmlDojoSrc
        
    def dojo(self, version=None, theme=None):
        self.dojo_static_handler = self.site.getStatic('dojo')
        theme = theme or self.theme
        version = version or self.dojo_version
        djConfig = "parseOnLoad: true, isDebug: %s, locale: '%s'" % (
        self.isDeveloper() and 'true' or 'false', self.locale)
        css_dojo = self.frontend.css_frontend(theme=theme)
        import_statements = ';\n    '.join(
                ['@import url("%s")' % self.dojo_static_handler.url(version, 'dojo', f) for f in css_dojo])
        self.body.script(src=self.dojo_static_handler.url(version, 'dojo', 'dojo', 'dojo.js'), djConfig=djConfig)
        self.builder.head.style(import_statements + ';\n', type="text/css")
            
    def finalizeDojo(self):
        widgetcatalog = GnrHtmlDojoSrc.widgetcatalog
        dojorequire = {}
        self.finalizeDojo_inner(self.builder.body, widgetcatalog, dojorequire)
        if dojorequire:
            dojorequires = ''.join(dojorequire.values())
            self.builder.body.script(dojorequires)
            
    def finalizeDojo_inner(self, src, widgetcatalog, dojorequire):
        for node in src:
            attr = node.attr
            node_value = node.value
            widget = widgetcatalog.get(attr['tag'])
            if widget:
                widget = widget.split(',')
                node.attr['dojoType'] = widget[0]
                for require in widget:
                    dojorequire[require] = '\ndojo.require("%s");' % require
                attr['tag'] = 'div'
            if node_value and isinstance(node_value, GnrHtmlSrc):
                self.finalizeDojo_inner(node_value, widgetcatalog, dojorequire)
                
    def rootPage(self, *args, **kwargs):
        self.theme = kwargs.pop('theme', None) or self.theme
        pagetemplate = kwargs.pop('pagetemplate', None)
        self.builder.initializeSrc(_class=self.theme)
        self.body = self.builder.body
        self.dojo()
        self.gnr_css()
        self.gnr_js()
        self.setJsRequires()
        self.setCssRequires()

       #if self.dynamic_css_requires:
       #    for v in self.dynamic_css_requires.values():
       #        if v:
       #            page.script('genro.dom.loadCss("%s")' %v)
       #if self.dynamic_js_requires:
       #    for v in self.dynamic_js_requires.values():
       #        if v:
       #            page.script('genro.dom.loadJs("%s")' %v)
        self.main(self.body, *args, **kwargs)
        self.finalizeDojo()
        result = self.builder.toHtml()
        #print result #commented out by Jeff
        return result