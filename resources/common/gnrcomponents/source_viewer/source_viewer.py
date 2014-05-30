from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from inspect import getsource
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
                        doc='=gnr.source_viewer.documentation')
        page.dataRpc('dummy',self.save_source_code,subscribe_sourceCodeUpdate=True,
                        sourceCode='=gnr.source_viewer.source',_if='sourceCode && _source_changed',
                        _source_changed='=gnr.source_viewer.changed_editor',
                        _onResult="""
                            SET gnr.source_viewer.source_oldvalue = kwargs.sourceCode;
                            genro.publish('rebuidPage');
                            """)
        page.dataController("""var newp = genro.rpc.remoteCall('main',this.startArgs, 'bag');
                            var n = genro.nodeById('source_viewer_root');
                            n.freeze();
                            var cc = newp._value.getNodeByAttr('nodeId','source_viewer_root')._value;
                            n.setValue(cc);
                            n.unfreeze();""",subscribe_rebuidPage=True,_delay=5000)
        self.source_viewer_sourceDocPalette(page)
        return frame.center.contentPane(nodeId='source_viewer_root')

    @public_method
    def save_source_documentation(self,doc=None,**kwargs):
        b = Bag()
        b['content'] = doc
        b['date'] = self.workdate
        b['user'] = self.user
        b.toXml(self.source_viewer_docName('xml'))

    @public_method
    def save_source_code(self,sourceCode=None):
        if not (self.site.remote_edit and self.isDeveloper()):
            raise Exception('Not Allowed to write source code')
        fname = self.source_viewer_docName('py')
        with open(fname,'w') as f:
            f.write(sourceCode)


    @public_method
    def source_viewer_content(self,pane,**kwargs):
        bc = pane.borderContainer(height='100%',_class='selectable')
        top = bc.framePane(region='top',splitter=True,height='200px',
                        _class='viewer_box')
        center = bc.framePane('sourcePane',region='center',_class='viewer_box')
        m = sys.modules[self.__module__]
        source = getsource(m)
        if self.site.remote_edit and self.isDeveloper():
            self.source_viewer_editor(center,source=source)
        else:
            self.source_viewer_html(center,source=source)
        top.top.slotBar('5,vtitle,*',_class='viewer_box_title',vtitle='Documentation')
        top.center.contentPane(overflow='auto').div('^gnr.source_viewer.documentation',connect_ondblclick='PUBLISH editSourceDoc;',
                            min_height='30px',padding='5px')
        docxml = self.source_viewer_docName('xml')
        if os.path.exists(docxml):
            b = Bag(docxml)
            bc.data('gnr.source_viewer.documentation',b['content'])

    def source_viewer_editor(self,frame,source=None):
        bar = frame.top.slotBar('5,vtitle,*,savebtn,revertbtn,5,readOnlyEditor,5',
                                _class='viewer_box_title',vtitle='Source')
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
                                readOnly='^gnr.source_viewer.readOnly')

    def source_viewer_html(self,frame,source=None):
        frame.top.slotBar('5,vtitle,*',_class='viewer_box_title',vtitle='Source')
        source = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
        frame.center.contentPane(overflow='auto').div(source,_class='codehilite',width='100%')

    def source_viewer_docName(self,ext=None):
        m = sys.modules[self.__module__]
        return '%s.%s' %(os.path.splitext(m.__file__)[0],ext)

    def source_viewer_sourceDocPalette(self,pane):
        palette = pane.palettePane(paletteCode='_docSource',dockTo='dummyDock',
                                    height='500px',width='600px',
                                    title='!!Source DOcumentation')
        frame = palette.framePane(frameCode='_docEditorFrame')
        frame.center.contentPane(overflow='hidden').ckEditor(value='^gnr.source_viewer.documentation' ,toolbar='simple')
        bar = frame.bottom.slotBar('*,saveDoc,5',_class='slotbar_dialog_footer')
        bar.saveDoc.slotButton('!!Save',action='PUBLISH sourceDocUpdate;')
        return frame

