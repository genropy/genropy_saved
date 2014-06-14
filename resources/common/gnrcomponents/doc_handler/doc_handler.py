from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

import sys
import re
import os

PAGEHTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%s</title>
<meta name="author" content="GenroPy">
</head>
<body>
    %s
</body>
</html>
"""

class DocHandler(BaseComponent):

    def de_documentPath(self,storeKey=None,folderpath=None,doctype=None,language=None):
        language = language or self.language
        if not folderpath:
            m = sys.modules[self.__module__]
            folderpath = os.path.splitext(os.path.split(m.__file__)[1])[0]
        return self.site.getStaticPath('pkg:%s' %self.package.name,'doc',language,doctype,folderpath,'%s.%s' %(storeKey,doctype),autocreate=-1)

    @struct_method
    def de_documentElement(self,pane,storeKey=None,folderpath=None,doctype='html',editAllowed=None,**kwargs):
        controller = self.pageController(datapath='_doc.content.%s' %storeKey)
        controller.dataRpc('.loaded',self.de_loadStoreFromFile,folderpath=folderpath,doctype=doctype,storeKey=storeKey,
                        language='=gnr.language',_onBuilt=True,
                    _onResult="""if(result){SET .current = result;}""",**{'subscribe_%s_loadfile' %storeKey:True})
        controller.dataRpc('dummy',self.de_saveStoreFile,folderpath=folderpath,doctype=doctype,storeKey=storeKey,
                        language='=gnr.language',
                        data='=.current',**{'subscribe_%s_savefile' %storeKey:True})
        pane.attributes.update(overflow='hidden')
        cssurl = self.site.getStaticUrl('rsrc:common','gnrcomponents','source_viewer','doceditor.css')
        iframepars = dict(border=0,height='100%',width='100%')
        iframepars.update(kwargs)
        iframe = pane.htmliframe(
                            shield=True,
                            onCreated="""
                            var cssurl = '%s';
                            var e = document.createElement("link");
                            e.href = cssurl;
                            e.type = "text/css";
                            e.rel = "stylesheet";
                            e.media = "screen";
                            widget.contentWindow.document.head.appendChild(e);
                            widget.contentWindow.ondblclick = function(){
                                genro.publish('documentElementEdit',{storeKey:'%s'});
                            }
                            """ %(cssurl,storeKey),**iframepars)
        controller.dataController('iframe.domNode.contentWindow.document.body.innerHTML = previewHTML',
                                previewHTML='^.current',iframe=iframe)
        if editAllowed:
            self.de_createDocEditorPalette(storeKey,cssurl=cssurl)

    def de_createDocEditorPalette(self,storeKey,cssurl=None):
        page = self.pageSource()
        palette = page.palettePane(paletteCode='de_docEditorPalette',dockTo='dummyDock',
                                    height='500px',width='600px',
                                    title='!!Documentation')
        form = palette.frameForm(frameCode='de_docEditorForm',store='memory',store_locationpath='_doc.content.%s' %storeKey,
                                store_autoSave=50,
                                datapath='.form')
        pane = form.center.contentPane(datapath='.record',overflow='hidden')
        pane.ckeditor(value='^.current',config_contentsCss=cssurl,
                        toolbar='standard') 
        pane.dataController("""this.form.load();""",subscribe_documentElementEdit=True)
        pane.dataController("this.getParentWidget('floatingPane').show();",formsubscribe_onLoaded=True)
        pane.dataController("""this.getParentWidget('floatingPane').hide();""",formsubscribe_onDismissed=True)
        bar = form.bottom.slotBar('revertbtn,*,cancel,savebtn,10',_class='slotbar_dialog_footer')
        bar.revertbtn.slotButton('!!Revert',action="""SET .record.current = _loaded; this.form.save();""",
                            disabled='==_current==_loaded',
                            _current='^.record.current',_loaded='=.record.loaded',_delay=100)
        bar.cancel.button('!!Cancel',action='this.form.abort();')
        bar.savebtn.button('!!Save',action="""this.form.save();
                                              this.form.abort();
                                              genro.publish(storeKey+'_savefile');""",
                                    storeKey=storeKey)

    @struct_method
    def de_docFrame(self,pane,code=None,storeKey=None,title=None,**kwargs):
        frameCode = code
        storeKey = storeKey or code
        frame = pane.framePane(frameCode=frameCode,**kwargs)
        bar = frame.top.slotToolbar('*,edit,5')
        bar.edit.slotButton('Edit',iconClass='iconbox pencil',
                            action="""genro.publish('documentElementEdit',{storeKey:storeKey});""",
                            storeKey=storeKey,hidden=not self.de_isDocWriter())
        sc = frame.center.stackContainer()
        sc.documentElement(storeKey=storeKey,doctype='html',editAllowed=self.de_isDocWriter())
        return frame

    @struct_method
    def de_docFrameMulti(self,pane,code=None,**kwargs):
        cssurl = self.site.getStaticUrl('rsrc:common','gnrcomponents','source_viewer','doceditor.css')
        form = pane.frameForm(frameCode='docFrame_%s' %code,store='document',datapath='gnr.doc.%s' %code)
        form.store.handler('load',rpcmethod=self.de_loadStoreFromFile,defaultCb="""
            return {
            title:kw._pages.getItem(kw._current+'?caption')
            };""",_pages='=.pages',_current='=.current')
        #rpc.addDeferredCb("""(!doctitle){
        #        SET .record.title = pages.getItem(current+'?caption');
        #    } 
        #    """,pages='=.pages',current='=.current',doctitle='=.record.title')
        form.store.handler('save',rpcmethod=self.de_saveStoreFile)
        slots = '5,docSelector,*'
        if self.de_isDocWriter():
            slots= '%s,labelTooltip,revertbtn,savebtn,docsemaphore,5,stackButtons,5' %slots
        bar = form.top.slotToolbar(slots)
        bar.docSelector.multiButton(value='^.current',storepath='.pages')
        if self.de_isDocWriter():
            fb = bar.labelTooltip.div(_class='dijitButtonNode',hidden='^#FORM.selectedPage?=#v!="editor"').div(_class='iconbox tag').tooltipPane().formbuilder(cols=1,border_spacing='3px')
            fb.textbox(value='^.record.title',lbl='Title')
            fb.dataController("""
                pages.setItem(current+'.?caption',newtitle);
                """,current='=.current',pages='=.pages',newtitle='^.record.title')
            bar.revertbtn.slotButton('!!Revert',action="""this.form.reload();""",
                            hidden='^#FORM.selectedPage?=#v!="editor"',
                            iconClass='iconbox revert')
            bar.savebtn.slotButton('!!Save',action="""this.form.save();""",
                            hidden='^#FORM.selectedPage?=#v!="editor"',
                            iconClass='iconbox save')
            bar.docsemaphore.div(_class='fh_semaphore',hidden='^#FORM.selectedPage?=#v!="editor"')
        sc = form.center.stackContainer(overflow='hidden',selectedPage='^#FORM.selectedPage')
        viewer = sc.contentPane(pageName='viewer',title='!!View',overflow='hidden',datapath='.record')
        viewer.dataController("""var filepath = pages.getNode(current).attr.filepath;
                            this.form.load({destPkey:filepath})
                            """,
                            current='^#FORM.current',pages='=#FORM.pages',_onBuilt=True,_delay=1)
        iframepars = dict(border=0,height='100%',width='100%')
        iframepars.update(kwargs)
        iframe = viewer.htmliframe(
                            shield=True,
                            onCreated="""
                            var cssurl = '%s';
                            var e = document.createElement("link");
                            e.href = cssurl;
                            e.type = "text/css";
                            e.rel = "stylesheet";
                            e.media = "screen";
                            widget.contentWindow.document.head.appendChild(e);
                            """ %cssurl,**iframepars)
        iframe.dataController('iframe.domNode.contentWindow.document.body.innerHTML = previewHTML',
                                previewHTML='^.body',iframe=iframe)
        editorpane = sc.contentPane(pageName='editor',datapath='.record',title='!!Edit',overflow='hidden')
        editorpane.ckeditor(value='^.body',config_contentsCss=cssurl,toolbar='standard') 
        return form

    @public_method
    def de_loadStoreFromFile(self,path,default_title=None,**kwargs):
        html= ''
        title=''
        if os.path.exists(path):
            with open(path,'r') as f:
                result = f.read()
                m = re.search("<body>(.*)</body>", result, re.I | re.S)
                if m:
                    html = m.group(1)
                m = re.search("<title>(.*)</title>", result, re.I | re.S)
                if m:
                    title = m.group(1)
        return Bag(content=Bag(body=html,title=title or default_title))
            

    @public_method
    def de_saveStoreFile(self,path=None,data=None,**kwargs):
        title = data['title'] or os.path.split(path)[1]
        with open(path,'w') as f:
            f.write(PAGEHTML %(title,data['body']))

    def de_isDocWriter(self):
        return self.application.checkResourcePermission('_DOC_,doc_%s' %self.package.name, self.userTags)

class DocumentationPage(DocHandler):
    def main_root(self,root,**kwargs):
        bc = root.borderContainer(height='100%')
        editAllowed = self.application.checkResourcePermission('_DOC_,doc_%s' %self.package.name, self.userTags)

        bc.contentPane(region='center').documentElement(storeKey='main',folderpath=None,doctype='html',
                                                        max_width='800px',margin='10px',
                                                        editAllowed=editAllowed)

    def de_documentPath(self,storeKey=None,folderpath=None,doctype=None,language=None):
        m = sys.modules[self.__module__]
        folderpath = os.path.split(m.__file__)[0].split(os.sep)
        idx = folderpath.index('webpages') +1
        folderpath = folderpath[idx:]
        folderpath.append('%s.%s' %(os.path.splitext(self.filename)[0],doctype))
        return self.site.getStaticPath('pkg:%s' %self.package.name,'doc',self.language,doctype,*folderpath,autocreate=-1)
