# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver
import os
import sys

class GnrCustomWebPage(object):
    js_requires='gnride'
    pdb_ignore=True
    def main(self,root,*args,**kwargs):
        root.attributes.update(overflow='hidden')
        debugger_drawer='close'
        if self._call_args:
            self.dest_page_id,self.dest_pdb_id=self._call_args
            debug_data=Bag(self.pdb.loadDebugDataFromConnection(self.dest_page_id,self.dest_pdb_id))
            root.data('debug_data',debug_data)
            debugger_drawer=True
            root.dataController("""
            genro.pdb.onDebugStep(debug_data);
            var current = debug_data.getItem('current');
            var module=current.getItem('filename')
            var lineno=current.getItem('lineno')
            genro.publish('openEditorPage',{module:module})
            """,_onStart=True,debug_data='=debug_data')
            
        bc = root.borderContainer(datapath='main')
        self.drawerPane(bc.framePane(frameCode='drawer',region='left',width='250px',splitter=True,drawer=True,background='rgba(230, 230, 230, 1)'))
        self.dbstructPane(bc.framePane(frameCode='dbstruct',region='right',width='250px',splitter=True,drawer='close',background='rgba(230, 230, 230, 1)'))

        frame = bc.framePane(frameCode='editingPages',datapath='main',selectedPage='^.selectedPage',region='center')
        bar = frame.top.slotToolbar('5,stackButtons,*,readOnlySlot,5',height='20px')
        bar.data('main.readOnly',True)
        bar.readOnlySlot.div().checkbox(value='^main.readOnly', label='Read Only')
        sc = frame.center.stackContainer(nodeId='codeEditor',selectedPage='^.selectedModule')
        bar.dataRpc('dummy','pdb.setConnectionBreakpoint',
                subscribe_setBreakpoint=True,
                #httpMethod='WSK'
                )
        bar.dataController("""
            if(module in sc.widget.gnrPageDict){
                SET .selectedModule = module;
                return
            }
            var label = module.replace(/\./g, '_').replace(/\//g, '_');
            var l = module.split('/');
            var title = l[l.length-1];
            sc._('ContentPane',label,{title:title,datapath:'.page_'+sc._value.len(),
                                        overflow:'hidden',
                                        pageName:module,closable:true
                                        })._('ContentPane',{remote:remotemethod,remote_docPath:module,overflow:'hidden'})
            SET .selectedModule = module;
            """,sc=sc,remotemethod=self.buildEditorTab,editorName='codeEditor',
            subscribe_openEditorPage=True)
            
        self.debuggerPane(bc.framePane(frameCode='pdbDebugger',height='400px',splitter=True,drawer=debugger_drawer,region='bottom'))


    def dbstructPane(self,frame):
        frame.data('main.dbstructure',self.app.dbStructure())
        frame.top.slotToolbar('*,searchOn,2',height='20px')
        pane = frame.center.contentPane(overflow='auto')
        pane.div(padding='10px').tree(nodeId='dbstructure_tree',storepath='main.dbstructure',_class='branchtree noIcon',
            hideValues=True,openOnClick=True)


    def drawerPane(self,frame):
        b = Bag()
        frame.top.slotToolbar('*,searchOn,2',height='20px')
        for k,pkgobj in self.application.packages.items():
            b.setItem(k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))

        
        frame.data('.directories.root',b,nodecaption='Project')
        pane = frame.center.contentPane(overflow='auto')
        pane.div(padding='10px').tree(nodeId='drawer_tree',storepath='.directories',persist=True,
                        connect_ondblclick="""var ew = dijit.getEnclosingWidget($1.target);
                                              console.log('ew',ew)
                                              if(ew.item && ew.item.attr.file_ext!='directory'){
                                                    genro.publish('openEditorPage',{module:ew.item.attr.abs_path})
                                              }
                                             """,_class='branchtree noIcon',
            hideValues=True,openOnClick=True,labelAttribute='nodecaption',font_size='')



    @public_method
    def buildEditorTab(self,pane,docPath=None,**kwargs):

        frameCode = docPath.replace('/','_').replace('.','_')
        frame = pane.framePane(frameCode=frameCode ,region='center',_class='viewer_box selectable')
        source = self.__readsource(docPath)
        breakpoints = self.pdb.getBreakpoints(docPath)
        pane.data('.docPath',docPath)
        bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
        bar.fpath.div('^.docPath',font_size='9px')
        frame.data('.source',source)
        frame.data('.breakpoints',breakpoints)

        commandbar = frame.top.slotBar(',*,savebtn,revertbtn,5',childname='commandbar',toolbar=True,background='#efefef')
        commandbar.savebtn.slotButton('Save',iconClass='iconbox save',
                                _class='source_viewer_button',
                                visible='^.changed_editor',
                                action='PUBLISH sourceCodeUpdate={save_as:filename || false}',
                                filename='',
                                ask=dict(title='Save as',askOn='Shift',
                                        fields=[dict(name='filename',lbl='Name',validate_case='l')]))
        commandbar.revertbtn.slotButton('Revert',iconClass='iconbox revert',_class='source_viewer_button',
                                action='SET .source = _oldval',
                                visible='^.changed_editor',
                                _oldval='=.source_oldvalue')

        frame.data('.source',source)
        frame.data('.source_oldvalue',source)
        frame.dataController("""SET .changed_editor = currval!=oldval;
                                genro.dom.setClass(bar,"changed_editor",currval!=oldval);""",
                            currval='^.source',
                            oldval='^.source_oldvalue',bar=commandbar,_onBuilt=True)
        frame.dataRpc('dummy',self.save_source_code,docPath='=.docPath',
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

        cm = frame.center.contentPane(overflow='hidden').codemirror(value='^.source',
                                nodeId='%s_cm' %frameCode,
                                config_mode='python',config_lineNumbers=True,
                                config_indentUnit=4,config_keyMap='softTab',
                                height='100%',
                                config_gutters=["CodeMirror-linenumbers", "pdb_breakpoints"],
                                onCreated="gnride.onCreatedEditor(this);",
                                readOnly='^main.readOnly',
                                modulePath=docPath)
        frame.dataController("""
            var cm = cm.externalWidget;
            cm.clearGutter('pdb_breakpoints');
            if(breakpoints){
                breakpoints.forEach(function(n){
                    console.log(n.attr)
                    var line_cm = n.attr.line -1;
                    cm.setGutterMarker(line_cm, "pdb_breakpoints",cm.gnrMakeMarker(n.attr.condition));
                });
            }
   
            """,breakpoints='^.breakpoints',cm=cm,_fired='^.editorCompleted')

    def __readsource(self,docPath):
        if not os.path.exists(docPath):
            return
        with open(docPath,'r') as f:
            return f.read()

    @public_method
    def save_source_code(self,sourceCode=None,docPath=None,save_as=None):
        sourceCode=str(sourceCode)
        if not self.source_viewer_edit_allowed():
            raise Exception('Not Allowed to write source code')
        try:
            compile('%s\n'%sourceCode, 'dummy', 'exec')
            if not save_as:
                sys.modules.pop(os.path.splitext(docPath)[0].replace(os.path.sep, '_').replace('.', '_'),None)
                self.__writesource(sourceCode,docPath)
                return 'OK'
            else:
                save_as = save_as.strip().replace(' ','_')
                if not save_as.endswith('.py'):
                    save_as = '%s.py' %save_as
                filepath = os.path.join(os.path.dirname(docPath),save_as)
                self.__writesource(sourceCode,filepath)
                return dict(newpath=filepath)

        except SyntaxError,e:
            return dict(lineno=e.lineno,msg=e.msg,offset=e.offset)

    def __writesource(self,sourceCode,docPath):
        if self.source_viewer_edit_allowed():
            with open(docPath,'w') as f:
                f.write(sourceCode)


    def source_viewer_edit_allowed(self):
        return self.site.remote_edit



        
    def debuggerPane(self,frame):
        bc =  frame.center.borderContainer()
        self.debuggerTop(frame.top)
        self.debuggerLeft(bc)
        self.debuggerRight(bc)
        self.debuggerBottom(bc)
        self.debuggerCenter(bc)
        
    def debuggerTop(self,top):
        bar = top.slotToolbar('5,stepover,stepin,stepout,cont,*')
        bar.stepover.slotButton('Step over',action='genro.pdb.do_stepOver()')
        bar.stepin.slotButton('Step in',action='genro.pdb.do_stepIn()')
        bar.stepout.slotButton('Step out',action='genro.pdb.do_stepOut()')
        bar.cont.slotButton('Continue',action='genro.pdb.do_continue()')
        
    def debuggerLeft(self,bc):
        bc=bc.borderContainer(width='250px',splitter=True,region='left',margin='2px', border='1px solid #efefef',margin_right=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Stack')
        bc.contentPane(region='center',padding='2px').tree(storepath='_dev.pdb.stack',
                     labelAttribute='caption',_class='branchtree noIcon',autoCollapse=True,
                     connect_onClick="""level=$1.attr.level;genro.pdb.do_level(level) """)
        
    def debuggerRight(self,bc):
        bc=bc.borderContainer(width='250px',splitter=True,region='right',margin='2px',border='1px solid #efefef',margin_left=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Current')
        paneTree=bc.contentPane(region='center',padding='2px')
       #paneTree.tree(storepath='_dev.pdb.result',openOnClick=True,autoCollapse=True,
       #         labelAttribute='caption',_class='branchtree noIcon',hideValues=True)
       #         
        tree = paneTree.treeGrid(storepath='_dev.pdb.result',noHeaders=True)
        tree.column('__label__',contentCb="""return this.attr.caption || this.label""",
                      background='#888',color='white')
                                                          
        tree.column('__value__',size='85%',contentCb="""var v=this.getValue();
                                                          return (v instanceof gnr.GnrBag)?'':_F(v)""")

    def debuggerCenter(self,bc):
        bc=bc.borderContainer(region='center',border='1px solid #efefef',margin='2px',margin_right=0,margin_left=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Output')
        center=bc.contentPane(region='center',padding='2px',border_bottom='1px solid silver')
        center.div(value='^.output', style='font-family:monospace; white-space:pre-wrap')
        lastline=center.div(position='relative')
        lastline.div('>>>',position='absolute',top='1px',left='0px')
        debugger_input=lastline.div(position='absolute',top='0px',left='20px',right='5px').input(value='^.command',width='100%',border='0px')
        center.dataController("""SET .output=output? output+_lf+line:line;""",line='^_dev.pdb.debugger.output_line',output='=.output')
        center.dataController("""SET _dev.pdb.debugger.output_line=command; 
                                 if (command.startsWith('/')){
                                    command=command.slice(1)
                                 }else if(!command.startsWith('!')){
                                     command='!'+command;
                                 }
                                 genro.pdb.sendCommand(command);
                                 SET .command=null;
                                 debugger_input.domNode.focus();
                                 """,command='^.command',debugger_input=debugger_input,_if='command')
        
       #bottom=bc.contentPane(region='bottom',padding='2px',splitter=True)
       #fb = bottom.div(margin_right='20px').formbuilder(cols=2,width='100%')
       #fb.textBox(lbl='Command',value='^.command',onEnter='FIRE .sendCommand',width='100%',padding='2px')
       #fb.button('Send', fire='.sendCommand')
        

    def debuggerBottom(self,bottom):
        pass
     
        
    def set_trace(self):
        debugger = GnrPdb(instance_name=self.page.site.site_name, page_id=self.page.page_id)
        try:
            debugger.set_trace(sys._getframe().f_back)
        except Exception,e:
            traceback.print_exc()
