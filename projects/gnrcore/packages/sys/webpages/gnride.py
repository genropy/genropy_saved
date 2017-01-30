 # -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.app.gnrconfig import getGenroRoot
import os
import sys

class GnrCustomWebPage(object):
    js_requires='gnride'
    pdb_ignore=True
    def main(self,root,**kwargs):
        with self.connectionStore() as store:
            gnride_page_id = store.getItem('_dev.gnride_page_id')
            if gnride_page_id:
                self.clientPublish(page_id=gnride_page_id,topic='closePage')
                store.setItem('_dev.gnride_page_id',self.page_id)
            else:
                store.setItem('_dev.gnride_page_id',self.page_id)
        root.attributes.update(overflow='hidden')
        bc = root.borderContainer(datapath='main')
        bc.dataController("gnride.start()",_onStart=True)
        self.drawerPane(bc.framePane(frameCode='drawer',region='left',width='250px',splitter=True,drawer=True,background='rgba(230, 230, 230, 1)'))
        self.dbstructPane(bc.framePane(frameCode='dbstruct',region='right',width='250px',splitter=True,drawer='close',background='rgba(230, 230, 230, 1)'))
        center = bc.framePane(frameCode='centerStack',region='center')
        bar = center.top.slotToolbar('5,stackButtons,*,addIdeBtn,5')
        bar.addIdeBtn.slotButton('Add ide',action='gnride.newIde({ide_page:"ide_"+genro.getCounter(),isDebugger:true})')
        sc = center.center.stackContainer(selectedPage='^.#parent.ide_page',nodeId='ideStack',datapath='.instances')
        self.makeEditorStack(sc.contentPane(pageName='mainEditor',title='Main Editor',overflow='hidden',datapath='.mainEditor'),'mainEditor')
        #bc.dataController('gnride.setBreakpoint(_subscription_kwargs)',subscribe_setBreakpoint=True)
        bc.dataRpc('dummy','pdb.setBreakpoint',subscribe_setBreakpoint=True)
        bc.dataController("""
            gnride.openModuleToEditorStack(_subscription_kwargs);
            """,subscribe_openModuleToEditorStack=True)
        bc.dataController("gnride.sendCommand(cmd,pdb_id)",subscribe_debugCommand=True)
        bc.dataController("""window.focus();""",subscribe_bringToTop=True)

        
     

    @public_method
    def makeEditorStack(self,pane,frameCode=None,isDebugger=False):
        bc = pane.borderContainer()
        if isDebugger:
            self.debuggerPane(bc.framePane(frameCode='%s_debugger' %frameCode,height='400px',splitter=True,drawer=True,region='bottom'))
        frame = bc.framePane(frameCode=frameCode,region='center')
        slots = '5,stackButtons,*' if isDebugger else '5,stackButtons,*,readOnlySlot,5'
        bar = frame.top.slotToolbar(slots,height='20px')
        bar.data('.readOnly',True)
        if not isDebugger:
            bar.readOnlySlot.div().checkbox(value='^.readOnly', label='Read Only')
        stackNodeId = '%s_sc' %frameCode
        frame.center.stackContainer(nodeId=stackNodeId,selectedPage='^.selectedModule')

    def dbstructPane(self,frame):
        frame.data('main.dbstructure',self.app.dbStructure())
        frame.top.slotToolbar('*,searchOn,2',height='20px',datapath='main.dbmodel')
        pane = frame.center.contentPane(overflow='auto')
        pane.div(padding='10px').tree(nodeId='dbstructure_tree',storepath='main.dbstructure',_class='branchtree noIcon',
            hideValues=True,openOnClick=True)


    def drawerPane(self,frame):
        b = Bag()
        frame.top.slotToolbar('*,searchOn,2',height='20px',datapath='main.dir')
        for k,pkgobj in self.application.packages.items():
            b.setItem('projects.%s' %k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))
        b.setItem('genropy',DirectoryResolver(getGenroRoot(),cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption='Genropy')
        
        frame.data('.directories.root',b,nodecaption='!!Folders')
        pane = frame.center.contentPane(overflow='auto')
        pane.div(padding='10px').tree(nodeId='drawer_tree',storepath='.directories',persist=True,
                        connect_ondblclick="""var ew = dijit.getEnclosingWidget($1.target);
                                              if(ew.item && ew.item.attr.file_ext!='directory'){
                                                    genro.publish('openModuleToEditorStack',{module:ew.item.attr.abs_path})
                                              }
                                             """,_class='branchtree noIcon pdb_tree',
            hideValues=True,openOnClick=True,labelAttribute='nodecaption',font_size='')



    @public_method
    def buildEditorTab(self,pane,module=None,ide_page=None,**kwargs):
        frameCode = '%s_%s' %(ide_page,module.replace('/','_').replace('.','_'))
        frame = pane.framePane(frameCode=frameCode ,region='center',_class='viewer_box selectable')
        source = self.__readsource(module)
        breakpoints = self.pdb.getBreakpoints(module)
        pane.data('.module',module)
        bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
        bar.fpath.div('^.module',font_size='9px')
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
        frame.dataRpc('dummy',self.save_source_code,docPath='=.module',
                        subscribe_sourceCodeUpdate=True,
                        sourceCode='=.source',_if='sourceCode && _source_changed',
                        _source_changed='=.changed_editor',
                        _onResult="""if(result=='OK'){
                                            SET .source_oldvalue = kwargs.sourceCode;
                                        
                                           // genro.publish('rebuildPage');
                                        //}else if(result.newpath){
                                        //    if(genro.mainGenroWindow){
                                        //        var treeMenuPath = genro.parentIframeSourceNode?genro.parentIframeSourceNode.attr.treeMenuPath:null;
                                        //        if(treeMenuPath){
                                        //            treeMenuPath = treeMenuPath.split('.');
                                        //            var l = result.newpath.split('/');
                                        //            treeMenuPath.pop();
                                        //            treeMenuPath.push(l[l.length-1].replace('.py',''));
                                        //            fullpath = treeMenuPath.join('.');
                                        //        }
                                        //        genro.dom.windowMessage(genro.mainGenroWindow,{topic:'refreshApplicationMenu',selectPath:fullpath});
                                        //    }
                                        }
                                        else{
                                            FIRE .error = result;
                                        }""")

        cm = frame.center.contentPane(overflow='hidden').codemirror(value='^.source',
                                nodeId='%s_cm' %frameCode,
                                config_mode='python',config_lineNumbers=True,
                                config_indentUnit=4,config_keyMap='softTab',
                                config_addon='search',
                                height='100%',
                                config_gutters=["CodeMirror-linenumbers", "pdb_breakpoints"],
                                onCreated="gnride.onCreatedEditor(this);",
                                readOnly='^.#parent.#parent.readOnly',
                                modulePath=module)
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
        bar = top.slotToolbar('5,stepover,stepin,stepout,cont,clearconsole,*')
        bar.stepover.slotButton('Step over',action='gnride.do_stepOver()')
        bar.stepin.slotButton('Step in',action='gnride.do_stepIn()')
        bar.stepout.slotButton('Step out',action='gnride.do_stepOut()')
        bar.cont.slotButton('Continue',action='gnride.do_continue()')

        bar.clearconsole.slotButton('Clear console',action='gnride.clearConsole()')

    def debuggerLeft(self,bc):
        bc=bc.borderContainer(width='250px',splitter=True,region='left',margin='2px', border='1px solid #efefef',margin_right=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Stack')
        bc.contentPane(region='center',padding='2px').tree(storepath='.stack',
                     labelAttribute='caption',_class='branchtree noIcon',autoCollapse=True,
                     connect_onClick="""level=$1.attr.level;gnride.do_level(level);""")
        
    def debuggerRight(self,bc):
        bc=bc.borderContainer(width='250px',splitter=True,region='right',margin='2px',border='1px solid #efefef',margin_left=0,rounded=4)
        paneTree=bc.contentPane(region='center')   
        tree = paneTree.treeGrid(storepath='.result',headers=True)
        tree.column('__label__',contentCb="""return this.attr.caption || this.label""",header='Variable')
        tree.column('__value__',size=300,contentCb="""var v=this.getValue();
                                                          return (v instanceof gnr.GnrBag)?'':_F(v)""",
                                                          header='Value')

    def debuggerCenter(self,bc):
        bc=bc.borderContainer(region='center',border='1px solid #efefef',margin='2px',margin_right=0,margin_left=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Output')
        center=bc.contentPane(region='center',padding='2px',border_bottom='1px solid silver',_class='selectable',overflow='auto')
        center.div(value='^.output', style='font-family:monospace; white-space:pre-wrap')
        lastline=center.div(position='relative')
        lastline.div('>>>',position='absolute',top='1px',left='0px')
        debugger_input=lastline.div(position='absolute',top='0px',left='20px',right='5px').input(value='^.command',width='100%',border='0px')
        center.dataController("""SET .output=output? output+_lf+line:line;""",line='^.output_line',output='=.output')
        center.dataController("""SET .output_line=command; 
                                 if (command[0]=='/'){
                                    command=command.slice(1)
                                 }else if(command[0]!='!'){
                                     command='!'+command;
                                 }
                                 gnride.sendCommand(command);
                                 SET .command=null;
                                 debugger_input.domNode.focus();
                                 """,command='^.command',debugger_input=debugger_input,_if='command')
        
       #bottom=bc.contentPane(region='bottom',padding='2px',splitter=True)
       #fb = bottom.div(margin_right='20px').formbuilder(cols=2,width='100%')
       #fb.textBox(lbl='Command',value='^.command',onEnter='FIRE .sendCommand',width='100%',padding='2px')
       #fb.button('Send', fire='.sendCommand')
        

    def debuggerBottom(self,bottom):
        pass


    def onClosePage(self):
        """TODO"""
        with self.connectionStore() as store:
            if store.getItem('_dev.gnride_page_id')==self.page_id:
                store.popNode('_dev.gnride_page_id')

     