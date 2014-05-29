from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from pygments import highlight
from inspect import getsource
import sys
import os
from pygments.lexers import PythonLexer,XmlLexer
from pygments.formatters import HtmlFormatter

class SourceViewer(BaseComponent):
    css_requires = 'pygmentcss/friendly,source_viewer'

    def rootWidget(self,root,**kwargs):
        frame = root.framePane(frameCode='sandbox',_class='sandbox',**kwargs)
        bar = frame.right.slotBar('0,sourceBox,0',width='400px',sourceBox_height='100%',
                        closable='close',splitter=True,border_left='1px solid #666')
        sourceBox = bar.sourceBox.div(height='100%',width='100%',position='relative',_class='source_viewer',
                        ).div(position='absolute',top='0',
                        right='0',bottom='0',left='0')
        sourceBox.remote(self.source_viewer_content)
        frame.dataController("""genro.wdgById('_docSource_floating').show();""",
                            subscribe_editSourceDoc=True)
        frame.dataRpc('dummy',self.save_source_documentation,subscribe_sourceDocUpdate=True,
                        doc='=source_doc.content')
        self.src_sourceDocPalette(frame)
        return frame

    @public_method
    def save_source_documentation(self,doc=None,**kwargs):
        b = Bag()
        b['content'] = doc
        b['date'] = self.workdate
        b['user'] = self.user
        b.toXml(self.xmlDocName())

    @public_method
    def source_viewer_content(self,pane,**kwargs):
        bc = pane.borderContainer(height='100%',_class='selectable')
        top = bc.borderContainer(region='top',splitter=True,height='200px',
                        _class='viewer_box')
        top.contentPane(region='top').div('Documentation',_class='viewer_box_title')
        top.contentPane(region='center',overflow='auto').div('^source_doc.content',connect_ondblclick='PUBLISH editSourceDoc;',
                            min_height='30px',padding='5px')
        m = sys.modules[self.__module__]
        source = getsource(m)
        source = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
        center = bc.borderContainer(region='center',_class='viewer_box')
        center.contentPane(region='top').div('Source',_class='viewer_box_title')
        center.contentPane(region='center',overflow='auto').div(source,_class='codehilite',width='100%')
        docxml = self.xmlDocName()
        if os.path.exists(docxml):
            b = Bag(docxml)
            bc.data('source_doc.content',b['content'])

    def xmlDocName(self):
        m = sys.modules[self.__module__]
        return '%s.xml' %os.path.splitext(m.__file__)[0]

    def src_sourceDocPalette(self,pane):
        palette = pane.palettePane(paletteCode='_docSource',dockTo='dummyDock',
                                    height='500px',width='600px',
                                    title='!!Source DOcumentation')
        frame = palette.framePane(frameCode='_docEditorFrame')
        frame.center.contentPane(overflow='hidden').ckEditor(value='^source_doc.content' ,toolbar='simple')
        bar = frame.bottom.slotBar('*,saveDoc,5',_class='slotbar_dialog_footer')
        bar.saveDoc.slotButton('!!Save',action='PUBLISH sourceDocUpdate;')
        return frame


