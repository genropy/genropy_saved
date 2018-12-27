from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
BASELANGUAGE = 'IT'

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
    documentation = False
    py_requires='gnrcomponents/filepicker:FilePicker'
    def onMain_docHandler(self):
        page = self.pageSource()
        page.script("""genro.docHandler = {
                getDocumentationPages:function(){
                    var b = genro.getData('gnr.doc.main.pages');
                    return b?b.deepCopy():new gnr.GnrBag();
                }
            }""")
        if self.documentation:
            page.addToDocumentation()



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
        code = code or 'main'
        cssurl = self.site.getStaticUrl('rsrc:common','gnrcomponents','source_viewer','doceditor.css')
        form = pane.frameForm(frameCode='docFrame_%s' %code,store='document',datapath='gnr.doc.%s' %code)
        form.store.handler('load',rpcmethod=self.de_loadStoreFromFile,defaultCb="""
            return {
            title:kw._pages.getItem(kw._current+'?caption')
            };""",_pages='=.pages',_current='=.current')
        form.store.handler('save',rpcmethod=self.de_saveStoreFile,stripLoadedValue=True)
        form.dataController("""
            var fm = genro.getParentGenro().framedIndexManager;
            fm.callOnCurrentIframe(null,'publish',[{'topic':'docUpdated'}]);

            """,formsubscribe_onSaved=True)
        slots = '5,docSelector,*'
        if self.de_isDocWriter():
            slots= '%s,imgPick,10,labelTooltip,revertbtn,savebtn,docsemaphore,5,stackButtons,5' %slots
        bar = form.top.slotToolbar(slots,height='20px')
        pagedocpars = self.documentation
        if pagedocpars == 'auto':
            pagedocpars = dict(title='Main')
        if pagedocpars is not True:
            bar.addToDocumentation(key='__page__',**pagedocpars)
        bar.docSelector.multiButton(value='^.current',items='^.pages',showAlways=True)
        if self.de_isDocWriter():
            fb = bar.labelTooltip.div(hidden='^#FORM.selectedPage?=#v!="editor"').div(_class='iconbox tag').tooltipPane().formbuilder(cols=1,border_spacing='3px')
            fb.textbox(value='^.record.title',lbl='Title',validate_onAccept="""
                if(userChange){
                    var pages = GET .pages;
                    var current = GET .current;
                    pages.getNode(current).updAttributes({caption:value});
                }
                """)
            bar.revertbtn.slotButton('!!Revert',action="""this.form.reload();""",
                            hidden='^#FORM.selectedPage?=#v!="editor"',
                            iconClass='iconbox revert')
            bar.savebtn.slotButton('!!Save',action="""this.form.save();""",
                            hidden='^#FORM.selectedPage?=#v!="editor"',
                            iconClass='iconbox save')
            bar.imgPick.slotButton(hidden='^#FORM.selectedPage?=#v!="editor"',iconClass='iconbox note',action='FIRE #FORM.showImagesPicker')
            bar.docsemaphore.div(_class='fh_semaphore',hidden='^#FORM.selectedPage?=#v!="editor"')
        sc = form.center.stackContainer(overflow='hidden',selectedPage='^#FORM.selectedPage')
        viewer = sc.contentPane(pageName='viewer',title='!!View',iconTitle='icnBottomViewer',overflow='hidden',datapath='.record')
        viewer.dataController("""
                            var attr = pages.getNode(current).attr;
                            var filepath = attr.filepath;
                            var imagespath = attr.imagespath;
                            this.form.load({destPkey:filepath,modifiers:'Shift'});
                            SET #FORM.imgFolders = imagespath;
                            """,
                            current='^#FORM.current',pages='=#FORM.pages',_if='current')
        iframepars = dict(border=0,height='100%',width='100%')
        iframepars.update(kwargs)
        iframe = viewer.htmliframe(
                            shield=True,
                            onCreated="""
                            var cssurl = '%s?nocache='+new Date();
                            var e = document.createElement("link");
                            e.href = cssurl;
                            e.type = "text/css";
                            e.rel = "stylesheet";
                            e.media = "screen";
                            widget.contentWindow.document.head.appendChild(e);
                            """ %cssurl,**iframepars)
        iframe.dataController('iframe.domNode.contentWindow.document.body.innerHTML = previewHTML',
                                previewHTML='^.body',iframe=iframe)
        iframe.dataController('iframe.domNode.contentWindow.document.head.innerHTML = head',
                                head='^.head',iframe=iframe)
        editorpane = sc.contentPane(pageName='editor',datapath='.record',title='!!Edit',iconTitle='icnBottomEditor',overflow='hidden')
        palette = editorpane.imgPickerPalette(code=code,folders='^#FORM.imgFolders',dockTo='dummyDock',externalSnapshot=True)
        palette.dataController("this.getParentWidget('floatingPane').show()",_fired='^#FORM.showImagesPicker');
        editorpane.ckeditor(value='^.body',config_contentsCss=cssurl,toolbar='standard') 
        return form

    @public_method
    def de_loadStoreFromFile(self,path,default_title=None,**kwargs):
        html= ''
        title=''
        head = ''
        storeNode = self.site.storageNode(path)
        if storeNode.exists:
            with storeNode.open(mode='r') as f:
                result = f.read()
                m = re.search("<body>(.*)</body>", result, re.I | re.S)
                if m:
                    html = m.group(1)
                m = re.search("<title>(.*)</title>", result, re.I | re.S)

                if m:
                    title = m.group(1)
                m = re.search("<head>(.*)</head>", result, re.I | re.S)
                if m:
                    head = m.group(1)
        return Bag(content=Bag(body=html,title=title or default_title,head=head))
            

    @public_method
    def de_saveStoreFile(self,path=None,data=None,**kwargs):
        spath = os.path.split(path)
        title = data['title'] or spath[1]
        dest = self.site.storageNode(path, autocreate=-1)
        with dest.open(mode='wb') as f:
            f.write(PAGEHTML %(title,data['body']))

    @struct_method
    def de_addToDocumentation(self,pane,title=None,filepath=None,code=None,key=None,doctype=None,language=None,**kwargs):
        filepath = self.de_documentPath(filepath=filepath,doctype=doctype,language=language)
        code = code or 'main'
        key = key or os.path.splitext(os.path.split(filepath)[1])[0]
        commonpath = os.path.join(filepath.split(os.path.sep,1)[0],'doc','images')
        caption=self.de_caption_from_module(filepath) or title or self.pagename.capitalize().replace('_',' ')
        pane.data('gnr.doc.%s.pages.%s' %(code,key),None,
                    caption=caption,
                    filepath=filepath,
                    imagespath=','.join(['%s:%s' %(os.path.join(os.path.dirname(filepath),'images'),caption.replace('!!','')),'%s:Common' %(commonpath)]))


    def de_documentPath(self,filepath=None,doctype=None,language=None,asUrl=False):
        output = self.site.getStaticUrl if asUrl else os.path.join
        language = language or self.language
        doctype = doctype or 'html'
        webpagespath = self.site.storageNode('pkg:%s' %self.package.name,'webpages').internal_path
        m = sys.modules[self.__module__]
        basename =  os.path.splitext(m.__file__.replace(webpagespath,''))[0][1:]
        fileargs = []
        if not filepath:
            fileargs = ['pkg:%s' %self.package.name,'doc','*lang*',doctype,'webpages','%s.%s' %(basename,doctype)]
        elif ':' in filepath:
            fileargs = [filepath]
        elif filepath.startswith('/'):
            filepath = filepath[1:]
            fileargs = ['pkg:%s' %self.package.name,'doc','*lang*',doctype,filepath]
        else:
            fileargs = ['pkg:%s' %self.package.name,'doc','*lang*',doctype,'webpages',
                                        os.path.dirname(basename),filepath]
        fpath = '/'.join(fileargs)
        if not self.site.storageNode(fpath.replace('*lang*',language)).exists:
            language = BASELANGUAGE
        outNode = self.site.storageNode(fpath.replace('*lang*',language))
        return outNode.url() if asUrl else outNode.fullpath


    def de_isDocWriter(self):
        return self.application.checkResourcePermission('_DOC_,doc_%s' %self.package.name, self.userTags)

    def de_caption_from_module(self,filepath):
        if os.path.isfile(filepath):
            with open(filepath,'r') as r:
                html = r.read()
                m = re.search("<title>(.*)</title>", html, re.I | re.S)
                if m:
                    return m.group(1)

class DocumentationPage(DocHandler):
    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        root.addToDocumentation()
        cssurl = self.site.getStaticUrl('rsrc:common','gnrcomponents','source_viewer','doceditor.css')
        iframepars = dict(border=0,height='100%',width='100%')
        url = self.de_documentPath(asUrl=True)
        root.data('main.src',url)
        root.dataController('SET main.src = currurl+"?nocache="+genro.getCounter();',
                        subscribe_docUpdated=True,currurl=url)
        root.iframe(src='^main.src',shield=True,
                        onLoad="""
                            var cssurl = '%s';
                            var e = document.createElement("link");
                            e.href = cssurl;
                            e.type = "text/css";
                            e.rel = "stylesheet";
                            e.media = "screen";
                            window.document.head.appendChild(e);
                            """ %cssurl,
                            **iframepars)

    
    def source_viewer_open(self):
        return False

