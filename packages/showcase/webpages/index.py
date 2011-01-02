#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Examples & Tutorials """

from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os

class GnrCustomWebPage(object):
    css_requires = 'index'
    # js_requires='ckeditor/ckeditor'

    def main(self, root, **kwargs):
        rootBC = root.borderContainer(_class='mainindex', **kwargs)
        self.pageController(rootBC)
        self.left_menu(rootBC.contentPane(region='left', width='230px', splitter=True, _class='leftpane'))
        self.top(rootBC.borderContainer(region='top', height='30px', _class='top_pane'))
        center = rootBC.borderContainer(region='center')
        buttons = center.contentPane(region='bottom', height='36px', _class='centerfooter').div(position='absolute',
                                                                                                right='20px', top='2px')

        buttons.button('Page', action='SET stack_selected=0')
        buttons.button('Source', action='SET stack_selected=1', disabled=False)
        buttons.button('Documentation', action='SET stack_selected=2', disabled=False)

        sc = center.stackContainer(region='center', selected='^stack_selected')
        sc.contentPane(overflow='hidden').iframe(height='100%', width='100%', border='0', src='^iframe.selected_page')
        sc.contentPane(overflow='auto', background_color='#ededed').div(value='^demo.current.source')
        self.docPane(sc)

    def pageController(self, root):
        """The data controller on the page"""
        root.dataFormula("demo.current.relpath", "page?page:'index.py'", _onStart=True, page='^iframe.selected_page')
        root.dataRpc("demo.current.name", "demoCurrentName", _onStart=True, relpath='^demo.current.relpath')
        #root.dataController('SET stack_selected = 0', _fired='^demo.current.name') # OPTIONAL: with this line the iFrame is ALWAYS opened on "Page"        
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
        leftpane.span("TestGarden > ")
        leftpane.span().a('^demo.current.relpath', href='^demo.current.relpath', color='white')

    def docPane(self, parent):
        doc = parent.contentPane(overflow='auto', _class='docpane', datapath='demo.doc.description')
        doc.div('Introduction', _class='doclabel')
        doc.div('^.introduction', _class='demodoc intro', connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Abstract', _class='doclabel')
        doc.div('^.abstract', _class='demodoc abstract', connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Widget Children', _class='doclabel')
        doc.div('^.children', _class='demodoc', connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Params', _class='doclabel')
        doc.div('^.params', _class='demodoc', connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Link', _class='doclabel')
        doc.div(_class='demodoc').a("Click here for Dojo's documentation", href='^demo.doc.description.link')
        parent.dataRpc('result', 'saveDocumentation', _doSave='^doSave', docbag='=demo.doc',
                       currpath='=demo.current.syspath', _onResult='genro.wdgById("doc_edit").hide();')
        parent.dataRpc('demo.doc', 'getDocFile', currpath='^demo.current.syspath',
                       _if='currpath', _ext='=selected.ext')
        self.editorDialog(parent)

    def rpc_saveDocumentation(self, docbag, currpath):
        if docbag and currpath:
            docpath, ext = os.path.splitext(currpath)
            docpath = '%s.xdoc' % docpath
            docpath = docpath.split('/')
            filename = docpath.pop()
            docpath.append('_doc')
            docpath.append(filename)
            docpath = '/'.join(docpath)
            docbag.toXml(docpath, autocreate=True)
            return 'ok'
        else:
            return 'error'

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

    def editorDialog(self, pane):
        dlg = pane.dialog(nodeId='doc_edit', title='Edit documentation', _class='edit_dlg')
        fb = dlg.formbuilder(cols=1, border_spacing='3px', font_size='8pt', datapath='demo.doc.description')
        fb.simpleTextarea(value='^.introduction', lbl='Introduction', lbl_vertical_align='top')
        fb.simpleTextarea(value='^.abstract', lbl='Abstract', lbl_vertical_align='top')
        fb.simpleTextarea(value='^.children', lbl='Children', lbl_vertical_align='top')
        fb.simpleTextarea(value='^.params', lbl='Params', lbl_vertical_align='top')
        fb.button('Save', action='FIRE doSave=true')

    ######################### server side operation #########################

    def diskDirectory(self):
        pages = Bag(self.site.sitemap['showcase'])
        for k in pages.keys():
            if hasattr(pages[k], '_htraverse'):
                pages[k].sort()
            #print pages
        #self.setPath(pages)
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