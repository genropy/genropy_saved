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
    # js_requires='ckeditor/ckeditor'
    def rootWidget(self,root,**kwargs):
        return root.borderContainer(_class='mainindex',**kwargs)
        
    def left_menu(self,pane):
        pane.data('menubag',self.diskDirectory())
        pane.tree(storepath='menubag',hideValues=True,inspect='shift',labelAttribute='name',isTree=False,
                    selected_path='tree.current_path')
        pane.dataFormula("iframe.selected_page", "current_path", current_path="^tree.current_path",_if='current_path')

    def main(self,rootBC,**kwargs):
        self.pageController(rootBC)
        self.left_menu(rootBC.contentPane(region='left',width='230px',splitter=True,_class='leftpane'))
        self.top(rootBC.borderContainer(region='top',height='30px',splitter=False,background_color='silver'))
        #self.top(rootBC.contentPane(region='top',height='30px',_class='header',padding='5px'))
        center = rootBC.borderContainer(region='center')
        buttons = center.contentPane(region='bottom',height='30px',_class='centerfooter').div(position='absolute',right='15px',top='2px')
        buttons.button('Page',baseClass='indexbutton',action='SET stack.selected=0')
        buttons.button('Source',baseClass='indexbutton',action='SET stack.selected=1',disabled=False) #to do
        buttons.button('Documentation',baseClass='indexbutton',action='SET stack.selected=2',disabled=False) #to do
        sc = center.stackContainer(region='center',selected='^stack.selected')
        sc.contentPane(overflow='hidden').iframe(height='100%',width='100%',border='0',src='^iframe.selected_page')
        sc.contentPane(overflow='auto',background_color='white').div(value='^demo.current.source')
        self.docPane(sc)
        self.docPaneEdit(sc.borderContainer(region='center'))

    def top(self,bc):
        leftpane = bc.contentPane(overflow='hidden',region='left',style='font-size:20px;')
        leftpane.span("TestGarden > ")
        leftpane.span().a('^demo.current.relpath',href='^demo.current.relpath',color='#dfcfa4')
        loginstack='login'
        if self.user:
            loginstack='logout'
        rightpane = bc.stackContainer(region='right',selectedPage='^loginstack')
        rightpane.dataFormula('loginstack','"%s"' %loginstack,_onStart=True)
        self.loginbox(rightpane.contentPane(pageName='login',datapath='login',width="600px"))
        self.logoutbox(rightpane.contentPane(pageName='logout'))
        
    def docPane(self,parent):
        doc=parent.contentPane(overflow='auto',_class='docpane',datapath='demo.doc.description')
        doc.div('Abstract',_class='doclabel')
        doc.div('^.full',_class='demodoc abstract',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Widget Children',_class='doclabel')
        doc.div('^.children',_class='demodoc',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Params',_class='doclabel')
        doc.div('^.params',_class='demodoc',connect_onclick='genro.wdgById("doc_edit").show()')
        doc.div('Link',_class='doclabel')
        doc.div(_class='demodoc').a("On Dojo's documentation",href='^demo.doc.description.link')
        parent.dataRpc('result','saveDocumentation',_doSave='^aux.doSave',
                      docbag='=demo.doc',currpath='=demo.current.syspath')
        parent.dataRpc('demo.doc','getDocFile',currpath='^demo.current.syspath',
                        _if='currpath',_ext='=selected.ext')
        self.editorDialog(parent)
                      
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
            docbag.toXml(docpath,autocreate=True)
            return 'ok'
        else:
            return 'error'
            
    def rpc_getDocFile(self,currpath):
        """docstring for rpc_getDocFile"""
        docpath = currpath.split('/')
        filename = docpath.pop()
        docpath.append('_doc')
        docpath.append(filename.replace('.py','.xdoc'))
        docpath = '/'.join(docpath)
        result = Bag()
        if os.path.isfile(docpath):
            result=Bag(docpath)
        return result
        
    def editorDialog(self,pane):
        """docstring for categoryDialog"""
        dlg = pane.dialog(nodeId='doc_edit',title='Edit documentation',_class='edit_dlg')
        fb = dlg.formbuilder(cols=1,border_spacing='3px',font_size='8pt',datapath='demo.doc.description')
        fb.textbox(value='^.short',lbl='Title')
        fb.simpleTextarea(value='^.full',lbl='Abstract',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.children',lbl='Children',lbl_vertical_align='top')
        fb.simpleTextarea(value='^.params',lbl='Params',lbl_vertical_align='top')
        fb.button('Save',action='FIRE aux.doSave=true')

    def docPaneEdit(self,bc):
        top=bc.contentPane(height='100%',region='top',splitter=False)
        toolbar="""[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   '/',
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""
        # top.ckeditor(value='^demo.current.docdata',nodeId='editor',config_toolbar='Basic',
        # config_uiColor= '#D1DBE4', toolbar=toolbar,height='700px')
        top.button('Save',action="FIRE pippo.doc;")
        
    def loginbox(self,pane):
        pane.dataRpc('.result', 'doLogin', login='=.form', btn='^.enter',_onResult='FIRE .afterLogin')
        pane.dataController("genro.dom.effect('bottomMsg','fadeout',{duration:3000,delay:3000});", 
                          msg='^error_msg',_if='msg')
        pane.dataController("SET loginstack='logout';SET stack.selected=3;" , message='=.result.message',
                            _if="message==''", _else="FIRE .error_msg = badUserMsg; SET .form = null;",
                             badUserMsg="!!Incorrect Login",_fired='^.afterLogin')
        fb = pane.formbuilder(cols=4,border_spacing='4px',_class='login',
                            onEnter='FIRE .enter',datapath='.form',style="float:right;")
        fb.textbox(value='^.user',ghost='User',width='10em')
        fb.textbox(value='^.password',ghost='Password',lbl_width='1em',type='password',
                 width='10em')
        fb.button('!!Login',baseClass='loginbutton',fire='login.enter')
        pane.span('^.error_msg',nodeId='bottomMsg',_class='disclaimer',style="float:right;margin:10px;")

    def logoutbox(self,pane):
        #pane.dataRecord('user','showcase.user',username='^login.result.user')
        pane.button('logout',float='right',action='genro.logout();')
        pane.div('^gnr.user',float='right',margin='10px')

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
        root.dataRpc('demo.current.docdata','getDocData',syspath='^demo.current.syspath')
        root.dataRpc('funcEdited','saveDocData',_fired='^pippo.doc',data='=demo.current.docdata',
                                        syspath="=demo.current.syspath",title='=demo.current.name')

    #----------  Rpc custom Calls ------------    
    def diskDirectory(self):         
        pages = self.site.sitemap['showcase']
        for k in pages.keys():
            if hasattr(pages[k],'_htraverse'):
                pages[k].sort()
        return pages

    def getUserMenu(self):
        result=self.application.config['menu']
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
        result=self.utils.readFile(syspath)
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter
        code = unicode(result)
        parsed = highlight(code, PythonLexer(), HtmlFormatter(linenos='table'))
        return parsed


    def rpc_currentDemoName(self,relpath=None):
        name=relpath.split('/')[-1]
        return name

    def rpc_getDocData(self,syspath):
        pass

    def rpc_saveDocData(self,data='',syspath='',title=''):
        tbl = self.db.table('showcase.document')
        #records = tbl.query(where='path=:func_path',func_path=syspath,addPkeyColumn=False,for_update=True).fetch()
        record_id=''
        tbl.batchUpdate(dict(doc=data),where='path=:func_path',func_path=syspath)
        self.db.commit()
        if title:
            try:
                pkey = tbl.newPkeyValue()
                tbl.insert(dict(id=pkey,name=title,data=data,path=syspath))
                self.db.commit()
            except:
                return None
        return record_id
