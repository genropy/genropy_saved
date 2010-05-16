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
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
import os

class GnrCustomWebPage(object):    
    css_requires= 'index'
    js_requires='ckeditor/ckeditor'
    def rootWidget(self,root,**kwargs):
        return root.borderContainer(_class='mainindex',**kwargs)
        
    def left_menu(self,pane):
        pane.data('menubag',self.diskDirectory())
        pane.tree(storepath='menubag',hideValues=True,inspect='shift',labelAttribute='name',isTree=False,
                    selected_path='tree.current_path')
        pane.dataFormula("iframe.selected_page", "current_path", current_path="^tree.current_path",_if='current_path')

    def top(self,pane):
        pane.span("TestGarden > ")
        pane.span().a('^current_demo',href='^current_demo',color='#dfcfa4')
        pane.dataFormula("current_demo", "page?page:'index'",_onStart=True,page='^iframe.selected_page')
        
        
    def main(self,rootBC,**kwargs):
        self.pageController(rootBC)
        self.editorDialog(rootBC)
        self.left_menu(rootBC.contentPane(region='left',width='230px',splitter=True,_class='leftpane'))
        self.top(rootBC.contentPane(region='top',height='20px',_class='header',padding='5px'))
        center = rootBC.borderContainer(region='center')
        buttons = center.contentPane(region='bottom',height='30px',_class='centerfooter').div(position='absolute',right='15px',top='2px')
        buttons.button('Page',baseClass='indexbutton',action='SET stack.selected=0')
        buttons.button('Source',baseClass='indexbutton',action='SET stack.selected=1',disabled=False) #to do
        buttons.button('Documentation',baseClass='indexbutton',action='SET stack.selected=2',disabled=False) #to do
        sc = center.stackContainer(region='center',selected='^stack.selected')
        sc.contentPane(overflow='hidden').iframe(height='100%',width='100%',border='0',src='^iframe.selected_page')
        sc.contentPane(overflow='auto',background_color='white').div(value='^demo.source')
        self.docPane(sc.borderContainer(region='center'))
        
    def docPane(self,bc):
        bc.contentPane(region='top',height='20px',_class='header',padding='5px',background_color='black')
        center = bc.contentPane(region='center',height='100%')
        center.data('editors.cked1.disabled',True)
        toolbar="""[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   '/',
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""
        
        cbc=center.borderContainer()
        top=cbc.contentPane(height='100%',region='top',splitter=False)
        top.ckeditor(value='^editors.cked1.data',nodeId='cked1',config_toolbar='Basic',
        config_uiColor= '#9AB8F3',readOnly='^editors.cked1.disabled', toolbar=toolbar,height='700px')

    def pageController(self,root):
        """The data controller on the page"""
        #root.data('tree',self.diskDirectory())
        root.dataRpc('result','saveDocumentation',_doSave='^aux.doSave',_if='_doSave',
                      docbag='^demo.doc',
                      currpath='^selected.abspage')
        root.data('panel',0)
        root.dataFormula('aux.title',"'Showcase'"
                          ,_if='doctitle==null',
                          doctitle='^demo.doc.description.short',
                          _else='doctitle',_init=True)        
        root.dataScript('selected.demopath',"if(p){return p;}else{return 'about.py';}",
                         p='^iframe.selected_page',ext='^selected.ext',
                         _if='ext!="directory"',_fired='^gnr.onStart')
        root.dataScript('dummy','SET panel = 0', _fired='^selected.demopath')
        root.dataRpc('demo.source','getSourceFile',linenumbers=1,
                     demopath='^selected.demopath')
        root.dataRpc('demo.doc','getDocFile',abspage='^iframe.current_path')
    
    def editorDialog(self,pane):
        """docstring for categoryDialog"""
        dlg = pane.dialog(nodeId='doc_edit',title='Edit documentation',_class='edit_dlg')
        fb = dlg.formbuilder(cols=1,border_spacing='3px',font_size='8pt',datapath='demo.doc.description')
        fb.textbox(value='^.short',lbl='Title')
        fb.simpleTextarea(value='^.full',lbl='Abstract',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.children',lbl='Children',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.params',lbl='Params',lbl_vertical_align='top')
        fb.button('Save',action='FIRE aux.doSave=true')
       
    #----------  Rpc custom Calls ------------    
    def diskDirectory(self):         
        pages = self.site.sitemap['showcase']
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
            
    def getUserMenu(self):

        result=self.application.config['menu']

        return result
        
    def rpc_getDocFile(self,abspage):
        """docstring for rpc_getDocFile"""
     
        docpath = abspage.split('/')
        filename = docpath.pop()
        docpath.append('_doc')
        docpath.append('/%s.xdoc' %filename)
        docpath = '/'.join(docpath)
        print docpath

        result = Bag()
        if os.path.isfile(docpath):
            result=Bag(docpath)
        return result
        
                     
    def rpc_getSourceFile(self,demopath='',linenumbers=0,**kwargs):
        basedir = __file__.strip('/').split('/')[:-1]
        basedir =u'/'+'/'.join(basedir)
        demopath = os.path.join(basedir,demopath)
        try:
            result=self.utils.readFile(demopath)
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter
            code = unicode(result)
            parsed = highlight(code, PythonLexer(), HtmlFormatter())
            return parsed
        except:
            return '<div>error: %s</div>'  %demopath
        if not linenumbers:
            return result
        lines=result.split('\n')
        result="<table border='0' cellspacing='0' cellpadding='0' >%s</table>"
        rows=[]
        for j,line in enumerate (lines):
            rows.append("<tr><td class='linenum'>%i</td><td class='linecode r%i'>%s</td></tr>" % (j+1,j%2,line))
        result = result  % '\n'.join(rows)
        return result

