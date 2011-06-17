#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os

class GnrCustomWebPage(object):
    css_requires = 'index'
    
    def main(self, root, **kwargs):
        rootBC = root.borderContainer(_class='mainindex', **kwargs)
        self.pageController(rootBC)
        self.left_menu(rootBC.contentPane(region='left', width='230px', splitter=True, _class='leftpane'))
        self.top(rootBC.borderContainer(region='top', height='30px', _class='top_pane'))
        center = rootBC.borderContainer(region='center')
        
        sc = center.stackContainer(region='center', selected='^stack_selected')
        sc.contentPane(overflow='hidden').iframe(height='100%', width='100%', border='0', src='^iframe.selected_page')
        sc.contentPane(overflow='auto', background_color='#ededed').div(value='^demo.current.source')
        
    def pageController(self, root):
        """The data controller on the page"""
        root.dataFormula("demo.current.relpath", "page?page:'index.py'", _onStart=True, page='^iframe.selected_page')
        root.dataRpc("demo.current.name", "demoCurrentName", _onStart=True, relpath='^demo.current.relpath')
        root.dataRpc('demo.current.syspath', 'fileSysPath', relpath='^demo.current.relpath')
        root.dataRpc('demo.current.source', 'getSourceFile', syspath='^demo.current.syspath')
        
    def left_menu(self, pane):
        pane.data('menubag', self.diskDirectory())
        pane.tree(storepath='menubag', hideValues=True, inspect='shift', labelAttribute='name',
                  isTree=False, selected_path='tree.current_path', selected_name='tree.name')
        pane.dataController("""if (current_path){SET iframe.selected_page=current_path;}""",
                            current_path="^tree.current_path")
                            
    def top(self, bc):
        leftpane = bc.contentPane(overflow='hidden', region='left', style='font-size:20px;')
        leftpane.span("TestGarden > ",color='white')
        leftpane.span().a('^demo.current.relpath', href='^demo.current.relpath', color='white')
        buttons = bc.span(float='right',style='font-size:13px;')
        buttons.button('Page',rounded=10,action='SET stack_selected=0')
        buttons.button('Source',rounded=10,action='SET stack_selected=1')
        
    def rpc_getDocFile(self, currpath):
        docpath = currpath.split('/')
        filename = docpath.pop()
        docpath.append('_doc')
        docpath.append(filename.replace('.py', '.xdoc'))
        docpath = '/'.join(docpath)
        result = Bag()
        if os.path.isfile(docpath):
            result = Bag(docpath)
        return result
        
    ######################### server side operation #########################
        
    def diskDirectory(self):
        pages = Bag(self.site.sitemap['showcase'])
        for k in pages.keys():
            if hasattr(pages[k], '_htraverse'):
                pages[k].sort()
        return pages
        
    def setPath(self, bag, parent=''):
        for node in bag:
            print node
            if node.attr.get('path'):
                continue
            if parent:
                node.attr['path'] = '%s/%s' % (parent, node.label)
            else:
                node.attr['path'] = node.label
            self.setPath(node.value, node.attr['path'])
            
    def getUserMenu(self):
        result = self.application.config['menu']
        return result
        
    def rpc_fileSysPath(self, relpath=None):
        if not relpath:
            return ''
        basedir = __file__.strip('/').split('/')[:-1]
        basedir = u'/' + '/'.join(basedir)
        sys_path = os.path.join(basedir, relpath)
        return sys_path
        
    def rpc_getSourceFile(self, syspath=None, **kwargs):
        if not syspath:
            return '<div>error: relpath missing</div>'
        if os.path.isdir(syspath):
            return '<div>isdir</div>'
        result = self.utils.readFile(syspath)
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter
        
        code = unicode(result)
        parsed = highlight(code, PythonLexer(), HtmlFormatter(linenos='table'))
        return parsed
        
    def rpc_demoCurrentName(self, relpath=None):
        name = relpath.split('/')[-1]
        return name