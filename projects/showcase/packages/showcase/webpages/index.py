#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2011 Softwell. All rights reserved.

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os

class GnrCustomWebPage(object):
    css_requires = 'index'
    rnd = 10
    
    def main(self, root, **kwargs):
        root.dataController("SET gnr.windowTitle = my_title + ' - Showcase';", my_title='^demo.current.name')
        rootBC = root.borderContainer(**kwargs)
        self.pageController(rootBC)
        self.left_menu(rootBC.contentPane(region='left', splitter=True, _class='leftpane', rounded=self.rnd))
        self.top(rootBC.borderContainer(region='top', _class='top_pane', rounded=self.rnd))
        center = rootBC.borderContainer(region='center', _class='center_pane', rounded=self.rnd)
        
        sc = center.stackContainer(region='center', selected='^stack_selected')
        sc.contentPane(overflow='hidden').iframe(height='100%', width='100%', border=0, src='^iframe.selected_page')
        sc.contentPane(overflow='auto', background_color='#ededed').div(value='^demo.current.source')
        
    def pageController(self, root):
        root.dataFormula('demo.current.relpath', "page?page:'index.py'", page='^iframe.selected_page', _onStart=True)
        root.dataRpc('demo.current.name', self.demoCurrentName, relpath='^demo.current.relpath', _onStart=True)
        root.dataRpc('demo.current.syspath', self.fileSysPath, relpath='^demo.current.relpath')
        root.dataRpc('demo.current.source', self.getSourceFile, syspath='^demo.current.syspath')
        
    def left_menu(self, pane):
        pane.data('menubag', self.diskDirectory())
        pane.tree(storepath='menubag', hideValues=True, inspect='shift', labelAttribute='name',
                  isTree=False, selected_path='tree.current_path', selected_name='tree.name')
        pane.dataController("""if (current_path){SET iframe.selected_page=current_path;}""",
                               current_path="^tree.current_path")
                               
    def top(self, bc):
        leftpane = bc.contentPane(overflow='hidden', region='left', style='font-size:20px;', margin_top='2px')
        leftpane.span("TestGarden > ", color='white', margin_left='15px')
        leftpane.span().a('^demo.current.relpath', href='^demo.current.relpath', color='white')
        buttons = bc.span(float='right',style='font-size:13px;')
        buttons.slotButton('Show page', action='SET stack_selected=0', iconClass='iconbox list')
        buttons.slotButton('Show code', action='SET stack_selected=1', margin_right='10px', iconClass='iconbox document')
        
####### server side operation #######
    
    def diskDirectory(self):
        pages = Bag(self.site.sitemap['showcase'])
        for k in pages.keys():
            if hasattr(pages[k], '_htraverse'):
                pages[k].sort()
        return pages
        
    @public_method
    def fileSysPath(self, relpath=None):
        if not relpath:
            return ''
        basedir = __file__.strip('/').split('/')[:-1]
        basedir = u'/' + '/'.join(basedir)
        sys_path = os.path.join(basedir, relpath)
        return sys_path
        
    @public_method
    def getSourceFile(self, syspath=None, **kwargs):
        if not syspath:
            return '<div>error: relpath missing</div>'
        if os.path.isdir(syspath):
            return '<div>isdir</div>'
        result = self.utils.readFile(syspath)
        code = unicode(result)
        parsed = highlight(code, PythonLexer(), HtmlFormatter(linenos='table'))
        return parsed
        
    @public_method
    def demoCurrentName(self, relpath=None):
        name = relpath.split('/')[-1]
        return name