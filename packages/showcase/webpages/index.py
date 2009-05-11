#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Examples & Tutorials """

#from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os

# ----- GnrWebPage subclass -----

class GnrCustomWebPage(object):    
    css_requires= 'index'
        
    def main(self, root, **kwargs):
        self.pageController(root)
        self.editorDialog(root)
        bc = root.borderContainer(margin='5px',_class='mainCont')
        top = bc.contentPane(region='top',_class='demoTitlePane').div('^aux.title')
        left = bc.borderContainer(region='left',width='20%',splitter=True,_class='bg',border_left='1px solid gray')
        client = bc.contentPane(region='center',border_right='1px solid gray')
        
        box = left.borderContainer(region='bottom',_class='bottombox',height='16ex',background_color='white')
        box.div('Demo',_class='stateButton',connect_onclick='SET panel=0')
        box.div('Documentation',_class='stateButton',connect_onclick='SET panel=1')
        box.div('Source',_class='stateButton',connect_onclick='SET panel=2')
        
        left_client = left.contentPane(region='center')
        tree = left_client.div(_class='navcont').tree(storepath='tree.#0',isTree=False,inspect='shift',
                         selected_rel_path='selected.page',selected_file_ext='selected.ext',
                         selected_abs_path='selected.abspage',selected_file_name='aux.filename')
                         
        
        
        right = client.stackContainer(sizeShare=80, _class='demoright',selected='^panel')
        demo = right.contentPane(overflow='hidden')
        demo.dataFormula('demosrc', 'dpath+"?_loc_=1"', dpath='^selected.demopath')
        demo.iframe(border='0px', width='100%', height='100%',
                      src='^demosrc')
        self.docPane(right)
        source=right.contentPane(overflow='auto',background_color='white').div(value='^demo.source',_class='linecode')
        
    def docPane(self,pane):
        doc=pane.contentPane(overflow='auto',_class='docpane',datapath='demo.doc.description')
        doc.div('Abstract',_class='doclabel')
        doc.div('^.full',_class='demodoc abstract',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Widget Children',_class='doclabel')
        doc.div('^.children',_class='demodoc',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Params',_class='doclabel')
        doc.div('^.params',_class='demodoc',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Link',_class='doclabel')
        doc.div(_class='demodoc').a("On Dojo's documentation",href='^demo.doc.description.link')

    def pageController(self,root):
        """The data controller on the page"""
        root.dataRemote('tree','diskDirectory')
        root.dataRpc('result','saveDocumentation',_doSave='^aux.doSave',_if='_doSave',
                      docbag='^demo.doc',
                      currpath='^selected.abspage')
        root.data('panel',0)
        root.dataFormula('aux.title',"'Showcase'"
                          ,_if='doctitle==null',
                          doctitle='^demo.doc.description.short',
                          _else='doctitle',_init=True)        
        root.dataScript('selected.demopath',"if(p){return p;}else{return 'about.py';}",
                         p='^selected.page',ext='^selected.ext',
                         _if='ext!="directory"',_fired='^gnr.onStart')
        root.dataScript('dummy','SET panel = 0', _fired='^selected.demopath')
        root.dataRpc('demo.source','getSourceFile',linenumbers=1,
                     demopath='^selected.demopath',_if='demopath&&_ext=="py"',_ext='=selected.ext')
        root.dataRpc('demo.doc','getDocFile',abspage='^selected.abspage',
                        _if='abspage&&_ext!="directory"',_ext='=selected.ext')
    
    def editorDialog(self,pane):
        """docstring for categoryDialog"""
        dlg = pane.dialog(nodeId='doc_edit',title='Edit documentation',_class='edit_dlg')
        fb = dlg.formbuilder(cols=1,border_spacing='3px',font_size='8pt',datapath='demo.doc.description')
        fb.textbox(value='^.short',lbl='Title')
        fb.simpleTextarea(value='^.full',lbl='Abstract',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.children',lbl='Children',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.params',lbl='Params',lbl_vertical_align='top')
        fb.button('Save',action='FIRE aux.doSave=true')
        
    def pageAddAttributes(self,node):
        attr=node.getAttr()
        if attr.get('file_ext') == 'py' :
            abs_path=node.getAttr('abs_path')
            m = gnrImport(abs_path)
            custompage = getattr(m,'GnrCustomWebPage', None)
            if custompage:
                custompage = custompage()
                attr['doc'] = custompage.__doc__
                if hasattr(custompage,'windowTitle'):
                    attr['title'] = custompage.windowTitle()
# ------------  Rpc custom Calls ------------    
    def rpc_diskDirectory(self):         
        pages =  self.utils.dirbag('',include='*.py',exclude='_*,.*,index.py,about.py')
        pages.walk(self.pageAddAttributes)
        return pages
        
    def rpc_saveDocumentation(self, docbag, currpath):
        """docstring for rpc_saveDocumentation"""
        
        if docbag and currpath:
            
            docpath, ext = os.path.splitext(currpath)
            docpath = '%s.xdoc' %docpath
            docpath = docpath.split('/')
            filename = docpath.pop()
            docpath.append('_doc')
            docpath.append(filename.replace('.py','.xdoc'))
            docpath = '/'.join(docpath)   
            docbag.toXml(docpath)
            return 'ok'
        else:
            return 'error'
            
    def rpc_getDocFile(self,abspage):
        """docstring for rpc_getDocFile"""
        docpath = abspage.split('/')
        filename = docpath.pop()
        docpath.append('_doc')
        docpath.append(filename.replace('.py','.xdoc'))
        docpath = '/'.join(docpath)
        result = Bag()
        if os.path.isfile(docpath):
            result=Bag(docpath)
        return result
        
                     
    def rpc_getSourceFile(self,demopath='',linenumbers=0,**kwargs):
        try:
            result=self.utils.readFile(demopath)
        except:
            return '<div>error: %s</error>'  %demopath
        if not linenumbers:
            return result
        lines=result.split('\n')
        result="<table border='0' cellspacing='0' cellpadding='0' >%s</table>"
        rows=[]
        for j,line in enumerate (lines):
            rows.append("<tr><td class='linenum'>%i</td><td class='linecode r%i'>%s</td></tr>" % (j+1,j%2,line))
        result = result  % '\n'.join(rows)
        return result

#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
