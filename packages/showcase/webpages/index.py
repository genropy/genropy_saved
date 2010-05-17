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
        pane.span().a('^demo.current.relpath',href='^demo.current.relpath',color='#dfcfa4')        
        
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
        sc.contentPane(overflow='auto',background_color='white').div(value='^demo.current.source')
        self.docPane(sc.borderContainer(region='center'))
        
    def docPane(self,bc):
        toolbar="""[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   '/',
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""
        
        top=bc.contentPane(height='100%',region='top',splitter=False)
        top.ckeditor(value='^demo.current.docdata',nodeId='editor',config_toolbar='Basic',
        config_uiColor= '#9AB8F3', toolbar=toolbar,height='700px')
        top.button('Save',fire='save.doc')

    def pageController(self,root):
        """The data controller on the page"""
        root.data('panel',0)
        root.dataFormula('aux.title',"'Showcase'"
                          ,_if='doctitle==null',
                          doctitle='^demo.current.doc.description.short',
                          _else='doctitle',_init=True)
        root.dataFormula("demo.current.relpath", "page?page:'index.py'",_onStart=True,page='^iframe.selected_page')
        root.dataRpc("demo.current.name", "currentDemoName",_onStart=True,relpath='^demo.current.relpath')
        root.dataScript('demo.current.name',"if(p){return p;}else{return 'index.py';}",
                         p='^iframe.selected_page',_fired='^gnr.onStart')
        root.dataScript('dummy','SET panel = 0', _fired='^demo.current.name')
        root.dataRpc('demo.current.syspath','fileSysPath',relpath='^demo.current.relpath')
        root.dataRpc('demo.current.source','getSourceFile',syspath='^demo.current.syspath')
        #root.dataRpc('demo.current.doc','getDocFile',abspage='^iframe.current_path')
        root.dataRpc('demo.current.docdata','getDocData',syspath='^demo.current.syspath')
        root.dataRpc('funcEdited','saveDocData',_fired='^save.doc',data='^demo.current.docdata',syspath="^demo.current.syspath",name='^demo.current.name')

    def editorDialog(self,pane):
        """docstring for categoryDialog"""
        dlg = pane.dialog(nodeId='doc_edit',title='Edit documentation',_class='edit_dlg')
        fb = dlg.formbuilder(cols=1,border_spacing='3px',font_size='8pt',datapath='demo.current.doc.description')
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

    def rpc_fileSysPath(self,relpath=None):
        if not relpath:
            return ''
        basedir = __file__.strip('/').split('/')[:-1]
        basedir =u'/'+'/'.join(basedir)
        sys_path = os.path.join(basedir,relpath)
        return sys_path
                         
    def rpc_getSourceFile(self,syspath=None,**kwargs):
        if not syspath:
            return '<div>error: relpath missing</div>'
        try:
            result=self.utils.readFile(syspath)
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter
            code = unicode(result)
            parsed = highlight(code, PythonLexer(), HtmlFormatter())
            return parsed
        except:
            return '<div>error: %s</div>'  %syspath

    def rpc_currentDemoName(self,relpath=None):
        name=relpath.split('/')[-1]
        return name

    def rpc_getDocData(self,syspath):
        tbl = self.db.table('showcase.function')
        func = tbl.query(where='path=:func_path',func_path=syspath).fetch()
        if func:
            return func[0]['data']
        return ''

    def rpc_saveDocData(self,data='',syspath='',name=''):
        tbl = self.db.table('showcase.function')
        func = tbl.query(where='path=:func_path',func_path=syspath).fetch()
        pkey=None
        if func:
            func[0]['doc']=data
            pkey = func[0]['id']
        else:
            try:
                pkey = tbl.newPkeyValue()
                tbl.insert(dict(id=pkey,name=name,doc=data,path=syspath))
            except:
                return None
        self.db.commit()
        return pkey
