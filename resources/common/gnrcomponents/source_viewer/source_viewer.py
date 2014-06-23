from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


import sys
import os


class SourceViewer(BaseComponent):
    css_requires = 'gnrcomponents/source_viewer/source_viewer,gnrcomponents/source_viewer/pygmentcss/friendly'
    js_requires = 'source_viewer'

    def source_viewer_open(self):
        return

    def onMain_sourceView(self):
        page = self.pageSource()
        _gnrRoot = self.pageSource('_gnrRoot')
        drawer = self.source_viewer_open() or 'close'
        sourceViewer = _gnrRoot.value.contentPane(region='right',drawer=drawer,
                        drawer_background='red',
                       drawer_width='14px',drawer_left='-14px',drawer_height='80px',drawer_margin_top='-40px',
                       drawer_border='0px',
                       width='550px',overflow='hidden',splitter=True,border_left='1px solid #efefef',
                       background='white')
        sourceViewer.contentPane(_class='source_viewer').remote(self.source_viewer_content)
        page.dataRpc('dummy',self.save_source_code,subscribe_sourceCodeUpdate=True,
                        sourceCode='=gnr.source_viewer.source',_if='sourceCode && _source_changed',
                        _source_changed='=gnr.source_viewer.changed_editor',
                        _onResult="""if(result=='OK'){
                                            SET gnr.source_viewer.source_oldvalue = kwargs.sourceCode;
                                            genro.publish('rebuildPage');
                                        }else{
                                            genro.publish('showCodeError',result);
                                        }""")
        page.dataController("""genro.src.updatePageSource('_pageRoot')""",
                        subscribe_rebuildPage=True,_delay=100)
        page.dataController("""
            var node = genro.nodeById('sourceEditor');
            var cm = node.externalWidget;
            lineno = lineno-1;
            offset = offset-1;
            var ch_start = offset>1?offset-1:offset;
            var ch_end = offset;
            cm.scrollIntoView({line:lineno,ch:ch_start});
            var tm = cm.doc.markText({line:lineno,ch:ch_start},{line:lineno, ch:ch_end},
                            {clearOnEnter:true,className:'source_viewer_error'});
            genro.dlg.floatingMessage(node.getParentNode(),{messageType:'error',
                        message:msg,onClosedCb:function(){
                    tm.clear();
                }})

            """,subscribe_showCodeError=True)
        self.source_viewer_sourceDocPalette(page)

    def source_viewer_docController(self,iframe,_onStart=None):
        rstsource = self.__readsource('rst') or '**Documentation**'
        page = self.pageSource()
        page.dataController('iframe.domNode.contentWindow.document.body.innerHTML = rendering',
                rendering='^gnr.source_viewer.doc.html',iframe=iframe,_onStart=_onStart)
        page.data('gnr.source_viewer.doc.rst',rstsource)
        page.data('gnr.source_viewer.doc.html',self.source_viewer_rst2html(rstsource))
        page.dataController("alert(page);",subscribe_showPagePalette=True)
        page.dataController("""genro.wdgById('_docSource_floating').show();""",
                            subscribe_editSourceDoc=True)
        page.dataRpc('gnr.source_viewer.doc.html',self.source_viewer_rst2html,
                    rstdoc='^gnr.source_viewer.doc.rst',
                    _delay=500)
        page.dataRpc('dummy',self.save_source_documentation,subscribe_sourceDocUpdate=True,
                        rstdoc='=gnr.source_viewer.doc.rst')

    @public_method
    def save_source_documentation(self,rstdoc=None,**kwargs):
        self.__writesource(rstdoc,'rst')

    def source_viewer_edit_allowed(self):
        return self.site.remote_edit and self.isDeveloper()

    @public_method
    def save_source_code(self,sourceCode=None):
        sourceCode=str(sourceCode)
        if not self.source_viewer_edit_allowed():
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
        if self.source_viewer_edit_allowed():
            fname = self.source_viewer_docName(ext)
            with open(fname,'w') as f:
                f.write(sourceCode)

    @public_method
    def source_viewer_rst2html(self,rstdoc=None,**kwargs):
        return self.site.getService('rst2html')(rstdoc,**kwargs)

    @public_method
    def source_viewer_content(self,pane,**kwargs):
        bc = pane.borderContainer(height='100%',_class='selectable')
        top = bc.framePane(region='top',splitter=True,height='300px',
                        _class='viewer_box')
        center = bc.framePane('sourcePane',region='center',_class='viewer_box')
        source = self.__readsource('py')
        if self.source_viewer_edit_allowed():
            self.source_viewer_editor(center,source=source)
        else:
            self.source_viewer_html(center,source=source)
        docslots = '5,vtitle,*,editbtn,5' if self.source_viewer_edit_allowed() else '5,vtitle,*'
        bar = top.top.slotToolbar(docslots,vtitle='Documentation',font_size='11px',font_weight='bold',height='20px')
        if self.source_viewer_edit_allowed():
            bar.editbtn.slotButton('Edit',iconClass='iconbox pencil',
                                action='PUBLISH editSourceDoc;')
        iframe = top.center.contentPane(overflow='hidden').htmliframe(height='100%',width='100%',border=0)
        self.source_viewer_docController(iframe)


    def source_viewer_editor(self,frame,source=None):
        bar = frame.top.slotToolbar('5,vtitle,*,savebtn,revertbtn,5,dataInspector,5,readOnlyEditor,5',vtitle='Source',font_size='11px',font_weight='bold')
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
        frame.top.slotToolbar('5,vtitle,*,dataInspector,5',vtitle='Source',font_size='11px',font_weight='bold',height='20px')
        source = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
        frame.center.contentPane(overflow='auto').div(source,_class='codehilite',width='100%')


    @struct_method
    def sv_slotbar_dataInspector(self,pane,**kwargs):
        pane.paletteTree(paletteCode='dataInspector',title='Data inspector',storepath='*D',tree_hideValues=False,
                                tree_onCreated="""
                                    var that = this;
                                    genro.src.onBuiltCall(function(){
                                            var r = {};
                                            var paths = genro.nodeById('_pageRoot')._value.walk(function(n){
                                                if(n.attr.datapath && n.attr.datapath[0]!='.'){
                                                    r[n.attr.datapath] = true;
                                                }else{
                                                for (var k in n.attr){
                                                    var attrval = n.attr[k]
                                                    if((typeof(attrval)=='string') && (attrval.length>1) &&
                                                         ((attrval[0]=='=') || (attrval[0]=='^')) &&
                                                         (attrval[0]!='.')
                                                         ){
                                                             r[attrval.slice(1).split('.')[0]]=true   
                                                    }
                                                }
                                                }
                                       
                                                },'static');
                                            var treeNodes = that.widget.rootNode.getChildren();
                                            treeNodes.forEach(function(n){
                                                    if(!(n.item.label in r)){
                                                        dojo.addClass(n.domNode,'hidden');
                                                    }
                                                })

                                        },100);
                                    
                                """,
                                dockButton=True,editable=True)

    def source_viewer_docName(self,ext=None):
        m = sys.modules[self.__module__]
        return '%s.%s' %(os.path.splitext(m.__file__)[0],ext)


    def source_viewer_sourceDocPalette(self,pane):
        palette = pane.palettePane(paletteCode='_docSource',dockTo='dummyDock',
                                    height='500px',width='600px',
                                    title='!!Source Documentation')
        frame = palette.framePane(frameCode='_docEditorFrame',_lazyBuild=True)
        frame.center.contentPane(overflow='hidden',_class='source_viewer').codemirror(value='^gnr.source_viewer.doc.rst',
                                height='100%',config_lineNumbers=True,
                                config_mode='rst',config_keyMap='softTab')
        slots = '*,saveDoc,5,saveAndClose,5'
        bar = frame.bottom.slotBar(slots,_class='slotbar_dialog_footer',height='20px')
        bar.saveDoc.slotButton('!!Save',action='PUBLISH sourceDocUpdate;')
        bar.saveAndClose.slotButton('!!Save and close',action="""
            this.getParentWidget('floatingPane').hide()
            PUBLISH sourceDocUpdate;""")

        return frame

        

