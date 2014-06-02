from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


import sys
import os

class SourceViewer(BaseComponent):
    css_requires = 'gnrcomponents/source_viewer/source_viewer,gnrcomponents/source_viewer/pygmentcss/friendly'

    def rootWidget(self,root,**kwargs):
        frame = root.framePane(frameCode='sandbox',_class='sandbox',**kwargs)
        page = self.pageSource()
        bar = frame.right.slotBar('0,sourceBox,0',width='550px',sourceBox_height='100%',
                        closable='close',splitter=True,border_left='1px solid #666')
        sourceBox = bar.sourceBox.div(height='100%',width='100%',position='relative',_class='source_viewer',
                        ).div(position='absolute',top='0',
                        right='0',bottom='0',left='0')
        sourceBox.remote(self.source_viewer_content)
        page.dataController("""genro.wdgById('_docSource_floating').show();""",
                            subscribe_editSourceDoc=True)
        page.dataRpc('dummy',self.save_source_documentation,subscribe_sourceDocUpdate=True,
                        rstdoc='=gnr.source_viewer.doc.rst')
        page.dataRpc('dummy',self.save_source_code,subscribe_sourceCodeUpdate=True,
                        sourceCode='=gnr.source_viewer.source',_if='sourceCode && _source_changed',
                        _source_changed='=gnr.source_viewer.changed_editor',
                        _onResult="""if(result=='OK'){
                                            SET gnr.source_viewer.source_oldvalue = kwargs.sourceCode;
                                            genro.publish('rebuildPage');
                                        }else{
                                            genro.publish('showCodeError',result);
                                        }""")
        page.dataRpc('gnr.source_viewer.doc.html',self.source_viewer_rst2html,
                    rstdoc='^gnr.source_viewer.doc.rst',
                    _delay=500)
        page.dataController("""genro.src.updatePageSource('source_viewer_root')""",
                        subscribe_rebuildPage=True,_delay=100)
        page.dataController("""
            var node = genro.nodeById('sourceEditor');
            var cm = node.externalWidget;
            lineno = lineno-1;
            offset = offset-1;
            var ch_start = offset>1?offset-1:offset;
            var ch_end = offset;
            console.log('ch_start',ch_start,'ch_end',ch_end,'offset',offset,'lineno',lineno)
            cm.scrollIntoView({line:lineno,ch:ch_start});
            var tm = cm.doc.markText({line:lineno,ch:ch_start},{line:lineno, ch:ch_end},
                            {clearOnEnter:true,className:'source_viewer_error'});
            genro.dlg.floatingMessage(node.getParentNode(),{messageType:'error',
                        message:msg,onClosedCb:function(){
                    tm.clear();
                }})

            """,subscribe_showCodeError=True)
        self.source_viewer_sourceDocPalette(page)
        return frame.center.contentPane(nodeId='source_viewer_root')

    @public_method
    def save_source_documentation(self,rstdoc=None,**kwargs):
        self.__writesource(rstdoc,'rst')

    @public_method
    def save_source_code(self,sourceCode=None):
        sourceCode=str(sourceCode)
        if not (self.site.remote_edit and self.isDeveloper()):
            raise Exception('Not Allowed to write source code')
        try:
            compile('%s\n'%sourceCode, 'dummy', 'exec')
            self.__writesource(sourceCode,'py')
            sys.modules.pop(self.__module__)
            return 'OK'
        except SyntaxError,e:
            return dict(lineno=e.lineno,msg=e.msg,offset=e.offset)

    def __readsource(self,ext):
        fname = self.source_viewer_docName(ext)
        if not os.path.exists(fname):
            return
        with open(fname,'r') as f:
            return f.read()

    def __writesource(self,sourceCode,ext):
        fname = self.source_viewer_docName(ext)
        with open(fname,'w') as f:
            f.write(sourceCode)

    @public_method
    def source_viewer_rst2html(self,rstdoc=None,**kwargs):
        return self.site.getService('rst2html')(rstdoc,**kwargs)

    @public_method
    def source_viewer_content(self,pane,**kwargs):
        bc = pane.borderContainer(height='100%',_class='selectable')
        top = bc.framePane(region='top',splitter=True,height='200px',
                        _class='viewer_box')
        center = bc.framePane('sourcePane',region='center',_class='viewer_box')
        source = self.__readsource('py')
        if self.site.remote_edit and self.isDeveloper():
            self.source_viewer_editor(center,source=source)
        else:
            self.source_viewer_html(center,source=source)
        bar = top.top.slotToolbar('5,vtitle,*,editbtn,5',vtitle='Documentation',font_size='11px',font_weight='bold')
        bar.editbtn.slotButton('Edit',iconClass='iconbox pencil',action='PUBLISH editSourceDoc;')
        iframe = top.center.contentPane(overflow='hidden').htmliframe(height='100%',width='100%',border=0)
        bar.dataController('iframe.domNode.contentWindow.document.body.innerHTML = rendering',
                rendering='^gnr.source_viewer.doc.html',iframe=iframe)
        
        rstsource = self.__readsource('rst') or '**Documentation**'
        bc.data('gnr.source_viewer.doc.rst',rstsource)
        bc.data('gnr.source_viewer.doc.html',self.source_viewer_rst2html(rstsource))

    def source_viewer_editor(self,frame,source=None):
        bar = frame.top.slotToolbar('5,vtitle,*,savebtn,revertbtn,5,readOnlyEditor,5',vtitle='Source',font_size='11px',font_weight='bold')
        bar.savebtn.slotButton('Save',iconClass='iconbox save',
                                _class='source_viewer_button',action='PUBLISH sourceCodeUpdate')
        bar.revertbtn.slotButton('Revert',iconClass='iconbox revert',_class='source_viewer_button',
                                action='SET gnr.source_viewer.source = _oldval',
                                _oldval='=gnr.source_viewer.source_oldvalue')

        bar.readOnlyEditor.div(_class='source_viewer_readonly').checkbox(value='^gnr.source_viewer.readOnly',
                                    label='ReadOnly',default_value=True,
                                    disabled='^gnr.source_viewer.changed_editor')
        frame.data('gnr.source_viewer.source',source)
        frame.data('gnr.source_viewer.source_oldvalue',source)
        frame.dataController("""SET gnr.source_viewer.changed_editor = currval!=oldval;
                                genro.dom.setClass(bar,"changed_editor",currval!=oldval);""",
                            currval='^gnr.source_viewer.source',
                            oldval='^gnr.source_viewer.source_oldvalue',bar=bar)
        frame.center.contentPane(overflow='hidden').codemirror(value='^gnr.source_viewer.source',
                                config_mode='python',config_lineNumbers=True,
                                config_indentUnit=4,config_keyMap='softTab',
                                height='100%',
                                readOnly='^gnr.source_viewer.readOnly',nodeId='sourceEditor')

    def source_viewer_html(self,frame,source=None):
        frame.top.slotToolbar('5,vtitle,*',_claswws='viewer_box_title',vtitle='Source')
        source = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
        frame.center.contentPane(overflow='auto').div(source,_class='codehilite',width='100%')

    def source_viewer_docName(self,ext=None):
        m = sys.modules[self.__module__]
        return '%s.%s' %(os.path.splitext(m.__file__)[0],ext)


    def source_viewer_sourceDocPalette(self,pane):
        palette = pane.palettePane(paletteCode='_docSource',dockTo='dummyDock',
                                    height='500px',width='600px',
                                    title='!!Source Documentation')
        frame = palette.framePane(frameCode='_docEditorFrame')
        frame.center.contentPane(overflow='hidden',_class='source_viewer',_lazyBuild=True).codemirror(value='^gnr.source_viewer.doc.rst',
                                height='100%',config_lineNumbers=True,
                                config_mode='rst',config_keyMap='softTab')
        bar = frame.bottom.slotBar('*,saveDoc,5,saveAndClose,5',_class='slotbar_dialog_footer')
        bar.saveDoc.slotButton('!!Save',action='PUBLISH sourceDocUpdate;')
        bar.saveAndClose.slotButton('!!Save and close',action="""
            this.getParentWidget('floatingPane').hide()
            PUBLISH sourceDocUpdate;""")

        return frame