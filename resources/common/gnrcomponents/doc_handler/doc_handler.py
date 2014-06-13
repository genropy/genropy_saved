from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method

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
        if not folderpath:
            m = sys.modules[self.__module__]
            folderpath = os.path.splitext(os.path.split(m.__file__)[1])[0]
        return self.site.getStaticPath('pkg:%s' %self.package.name,'doc',language,doctype,folderpath,'%s.%s' %(storeKey,doctype),autocreate=-1)

    @public_method
    def de_loadStoreFromFile(self,storeKey=None,folderpath=None,doctype=None,language=None):
        fname = self.de_documentPath(storeKey=storeKey,folderpath=folderpath,doctype=doctype,language=language)
        if os.path.exists(fname):
            with open(fname,'r') as f:
                result = f.read()
                m = re.search("<body>(.*)</body>", result, re.I | re.S)
                if m:
                    return m.group(1)
        return ''

    @public_method
    def de_saveStoreFile(self,data=None,storeKey=None,folderpath=None,doctype=None,language=None):
        fname = self.de_documentPath(storeKey=storeKey,folderpath=folderpath,doctype=doctype,language=language)
        with open(fname,'w') as f:
            f.write(PAGEHTML %(storeKey,data))

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
        frame.center.contentPane(padding='10px').documentElement(storeKey=storeKey,doctype='html',
                                    editAllowed=self.de_isDocWriter())
        return frame

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
