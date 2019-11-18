#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builtins import str
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrdict import dictExtract
try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    print('Missing pygments. Please do pip install pygments')


import sys
import os


class SourceViewer(BaseComponent):
    css_requires = 'gnrcomponents/source_viewer/source_viewer,gnrcomponents/source_viewer/pygmentcss/friendly'
    py_requires = 'gnrcomponents/doc_handler/doc_handler:DocHandler'
    js_requires = 'source_viewer'
    source_viewer_rebuild = True

    def source_viewer_root(self,root):
        drawer_cb = getattr(self,'source_viewer_open',None)
        drawer = drawer_cb() if drawer_cb else 'close'
        if drawer is False:
            return
        return root.value.contentPane(region='right',drawer=drawer,
                        drawer_background='red',drawer_top='21px',drawer_label='<div class="source_viewer_drawerlabel">Code</div>',
                       drawer_width='43px',drawer_left='-40px',drawer_height='21px',
                       drawer_border='0px',
                       width='550px',overflow='hidden',
                       splitter=True,border_left='1px solid #efefef',
                       background='white')

    def onMain_sourceView(self):
        page = self.pageSource()
        _gnrRoot = self.pageSource('_gnrRoot')
        sourceViewer = getattr(self,'source_viewer_customroot',self.source_viewer_root)(_gnrRoot)
        if sourceViewer is None:
            return
        frame = sourceViewer.framePane('sourceViewerFrame',_class='source_viewer',datapath='gnr.source_viewer')
        if self._call_kwargs.get('_source_toolbar','t')=='t' \
            and not self._call_kwargs.get('_source_viewer','').startswith('stack'):
            bar = frame.top.slotToolbar('2,sb,*,readOnlyEditor,dataInspector,2',height='20px')
            if getattr(self,'source_viewer_addButton',True):
                sb = bar.sb.stackButtons(stackNodeId='source_viewer_stack')
                self.source_viewer_addFileMenu(sb.div('<div class="multibutton_caption">+</div>',_class='multibutton'))
            else:
                bar.attributes.update(toolbar=False,background='#efefef')
                bar.sb.div()
            if self.source_viewer_edit_allowed():
                bar.readOnlyEditor.div(_class='source_viewer_readonly').checkbox(value='^.readOnly',
                                        label='ReadOnly',default_value=True,
                                        disabled='^.changed_editor')
            else:
                bar.readOnlyEditor.div()
        sc = frame.center.stackContainer(nodeId='source_viewer_stack')
        frame.dataController("""
            var label = docname.replace(/\./g, '_').replace(/\//g, '_');
            if(sc._value.getNode(label)){
                return;
            }
            var l = docname.split('/');
            var title = l[l.length-1];
            sc._('ContentPane',label,{title:title,datapath:'.page_'+sc._value.len(),
                                        remote:remotemethod,remote_docname:docname,overflow:'hidden',
                                        closable:true})
            """,docname='^.new_source_viewer_page',sc=sc,remotemethod=self.source_viewer_content)
        pane = sc.contentPane(title='Main',datapath='.main',overflow='hidden')
        docname = '%s.py' %os.path.splitext(sys.modules[self.__module__].__file__)[0]
        cmkwargs = dictExtract(self._call_kwargs,'cm_')
        codemirror_config = {}
        if cmkwargs:
            for k,v in cmkwargs.items():
                codemirror_config['config_%s' %k] = v
        pane.remote(self.source_viewer_content,docname=docname,codemirror_config=codemirror_config)
        sourceViewer.addToDocumentation()
        if self.source_viewer_rebuild:
            page.dataController("""genro.src.updatePageSource('_pageRoot')""",
                        subscribe_rebuildPage=True,_delay=100)

    def source_viewer_edit_allowed(self):
        return self.site.remote_edit

    def source_viewer_addFileMenu(self,pane):
        b = Bag()
        for k,pkgobj in list(self.application.packages.items()):
            b.setItem(k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))

        
        pane.data('.directories',b)
        pane.menu(action='FIRE .new_source_viewer_page = $1.abs_path;', modifiers='*', storepath='.directories', _class='smallmenu')

    @public_method
    def save_source_code(self,sourceCode=None,docname=None,save_as=None):
        sourceCode=str(sourceCode)
        if not self.source_viewer_edit_allowed():
            raise Exception('Not Allowed to write source code')
        try:
            compile('%s\n'%sourceCode, 'dummy', 'exec')
            if not save_as:
                sys.modules.pop(os.path.splitext(docname)[0].replace(os.path.sep, '_').replace('.', '_'),None)
                self.__writesource(sourceCode,docname)
                return 'OK'
            else:
                save_as = save_as.strip().replace(' ','_')
                if not save_as.endswith('.py'):
                    save_as = '%s.py' %save_as
                filepath = os.path.join(os.path.dirname(docname),save_as)
                self.__writesource(sourceCode,filepath)
                return dict(newpath=filepath)

        except SyntaxError as e:
            return dict(lineno=e.lineno,msg=e.msg,offset=e.offset)

    def __writesource(self,sourceCode,docname):
        if self.source_viewer_edit_allowed():
            with open(docname,'w') as f:
                f.write(sourceCode)

    def __readsource(self,docname):
        if not os.path.exists(docname):
            return
        with open(docname,'r') as f:
            return f.read()



    @public_method
    def source_viewer_rst2html(self,rstdoc=None,**kwargs):
        return self.site.getService('rst2html')(rstdoc,**kwargs)

    @public_method
    def source_viewer_content(self,pane,docname=None,**kwargs):
        center = pane.framePane('sourcePane_%s' %docname.replace('/','_').replace('.','_'),region='center',_class='viewer_box selectable')
        source = self.__readsource(docname)
        self.source_viewer_editor(center,source=source)
        pane.data('.docname',docname)
        pane.dataRpc('dummy',self.save_source_code,docname='=.docname',
                        subscribe_sourceCodeUpdate=True,
                        sourceCode='=.source',_if='sourceCode && _source_changed',
                        _source_changed='=.changed_editor',
                        _onResult="""if(result=='OK'){
                                            SET .source_oldvalue = kwargs.sourceCode;
                                            genro.publish('rebuildPage');
                                        }else if(result.newpath){
                                            if(genro.mainGenroWindow){
                                                var treeMenuPath = genro.parentIframeSourceNode?genro.parentIframeSourceNode.attr.treeMenuPath:null;
                                                if(treeMenuPath){
                                                    treeMenuPath = treeMenuPath.split('.');
                                                    var l = result.newpath.split('/');
                                                    treeMenuPath.pop();
                                                    treeMenuPath.push(l[l.length-1].replace('.py',''));
                                                    fullpath = treeMenuPath.join('.');
                                                }
                                                genro.dom.windowMessage(genro.mainGenroWindow,{topic:'refreshApplicationMenu',selectPath:fullpath});
                                            }
                                        }
                                        else{
                                            FIRE .error = result;
                                        }""")



    def source_viewer_editor(self,frame,source=None):
        if self.source_viewer_edit_allowed():
            bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
            bar.fpath.div('^.docname',font_size='9px')
            commandbar = frame.top.slotBar(',*,savebtn,revertbtn,5',childname='commandbar',toolbar=True,background='#efefef')
            commandbar.savebtn.slotButton('Save',iconClass='iconbox save',
                                _class='source_viewer_button',
                                action='PUBLISH sourceCodeUpdate={save_as:filename || false}',
                                filename='',
                                ask=dict(title='Save as',askOn='Shift',
                                        fields=[dict(name='filename',lbl='Name',validate_case='l')]))
            commandbar.revertbtn.slotButton('Revert',iconClass='iconbox revert',_class='source_viewer_button',
                                action='SET .source = _oldval',
                                _oldval='=.source_oldvalue')
            
            frame.dataController("""SET .changed_editor = currval!=oldval;
                                genro.dom.setClass(bar,"changed_editor",currval!=oldval);""",
                            currval='^.source',
                            oldval='^.source_oldvalue',bar=commandbar)
        frame.data('.source',source)
        frame.data('.source_oldvalue',source)
        codemirrorkw = dict(
            config_mode='python',config_lineNumbers=True,
            config_indentUnit=4,config_keyMap='softTab',
        )
    
        codemirrorkw.update(self._call_kwargs.get('codemirror_config'))
        cm = frame.center.contentPane(overflow='hidden').codemirror(value='^.source',
                                height='100%',
                                readOnly=not self.source_viewer_edit_allowed() or '^gnr.source_viewer.readOnly',
                                **codemirrorkw)
        
        frame.dataController("""
            var cm = cmNode.externalWidget;
            var lineno = error.lineno-1;
            var offset = error.offset-1;
            var ch_start = error.offset>1?error.offset-1:error.offset;
            var ch_end = error.offset;
            cm.scrollIntoView({line:lineno,ch:ch_start});
            var tm = cm.doc.markText({line:lineno,ch:ch_start},{line:lineno, ch:ch_end},
                            {clearOnEnter:true,className:'source_viewer_error'});
            genro.dlg.floatingMessage(cmNode.getParentNode(),{messageType:'error',
                        message:error.msg,onClosedCb:function(){
                    tm.clear();
                }})

            """,error='^.error',cmNode=cm)

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

                                        },500);
                                    
                                """,
                                dockButton=True,editable=True)

    def source_viewer_docName(self,ext=None):
        m = sys.modules[self.__module__]
        return '%s.%s' %(os.path.splitext(m.__file__)[0],ext)


        

