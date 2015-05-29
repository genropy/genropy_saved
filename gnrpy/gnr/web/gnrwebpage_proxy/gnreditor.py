#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  developer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os


from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method



class GnrCodeEditor(GnrBaseProxy):
    def mainPane(self,pane,editorName=None,readOnly=True,dataInspector=False,mainModule=None,**kwargs):
        mainModule = mainModule or self.page.modulePath
        frame = pane.framePane(frameCode=editorName,_class='source_viewer',margin='2px',datapath='.source_viewer',**kwargs)
        slots = ['2','sb','*']
        if not readOnly:
            slots.append('readOnlyEditor')
        if dataInspector:
            slots.append('dataInspector')
        slots.append('2')
        bar = frame.top.slotToolbar(','.join(slots),height='20px')
        stackNodeId = '%s_stack' %editorName
        sb = bar.sb.stackButtons(stackNodeId=stackNodeId)
        self.sourceFileMenu(sb.div('<div class="multibutton_caption">+</div>',_class='multibutton'))

        sc = frame.center.stackContainer(nodeId=stackNodeId)
        bar.dataController("""
            var label = docPath.replace(/\./g, '_').replace(/\//g, '_');
            if(sc._value.getNode(label)){
                return;
            }
            var l = docPath.split('/');
            var title = l[l.length-1];
            sc._('ContentPane',label,{title:title,datapath:'.page_'+sc._value.len(),
                                        remote:remotemethod,remote_docPath:docPath,overflow:'hidden',
                                        closable:true})
            """,docPath='^.new_source_viewer_page',sc=sc,remotemethod='dev.buildEditorTab',readOnly=readOnly)
        pane = sc.contentPane(title='Main',datapath='.main',overflow='hidden')
        pane.remote('codeEditor.buildEditorTab',docPath=mainModule,readOnly=readOnly)
        if not readOnly:
            pane.dataController("""genro.src.updatePageSource('_pageRoot')""",
                        subscribe_rebuildPage=True,_delay=100)


    def sourceFileMenu(self,pane):
        b = Bag()
        for k,pkgobj in self.page.application.packages.items():
            b.setItem(k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))
        pane.data('.directories',b)
        pane.menu(action='FIRE .new_source_viewer_page = $1.abs_path;', modifiers='*', storepath='.directories', _class='smallmenu')

    def __readsource(self,docPath):
        if not os.path.exists(docPath):
            return
        with open(docPath,'r') as f:
            return f.read()

    @public_method
    def buildEditorTab(self,pane,docPath=None,readOnly=None,**kwargs):
        center = pane.framePane('sourcePane_%s' %docPath.replace('/','_').replace('.','_'),region='center',_class='viewer_box selectable')
        source = self.__readsource(docPath)
        self.buildSourceEditor(center,source=source,readOnly=readOnly)
        pane.data('.docPath',docPath)
       #pane.dataRpc('dummy',self.save_source_code,docPath='=.docPath',
       #                subscribe_sourceCodeUpdate=True,
       #                sourceCode='=.source',_if='sourceCode && _source_changed',
       #                _source_changed='=.changed_editor',
       #                _onResult="""if(result=='OK'){
       #                                    SET .source_oldvalue = kwargs.sourceCode;
       #                                    genro.publish('rebuildPage');
       #                                }else if(result.newpath){
       #                                    if(genro.mainGenroWindow){
       #                                        var treeMenuPath = genro.parentIframeSourceNode?genro.parentIframeSourceNode.attr.treeMenuPath:null;
       #                                        if(treeMenuPath){
       #                                            treeMenuPath = treeMenuPath.split('.');
       #                                            var l = result.newpath.split('/');
       #                                            treeMenuPath.pop();
       #                                            treeMenuPath.push(l[l.length-1].replace('.py',''));
       #                                            fullpath = treeMenuPath.join('.');
       #                                        }
       #                                        genro.dom.windowMessage(genro.mainGenroWindow,{topic:'refreshApplicationMenu',selectPath:fullpath});
       #                                    }
       #                                }
       #                                else{
       #                                    FIRE .error = result;
       #                                }""")



    def buildSourceEditor(self,frame,source=None,readOnly=True):
        bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
        bar.fpath.div('^.docPath',font_size='9px')
        if not readOnly:
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
            frame.data('.source_oldvalue',source)
            frame.dataController("""SET .changed_editor = currval!=oldval;
                                genro.dom.setClass(bar,"changed_editor",currval!=oldval);""",
                            currval='^.source',
                            oldval='^.source_oldvalue',bar=commandbar)

        frame.data('.source',source)
        cm = frame.center.contentPane(overflow='hidden').codemirror(value='^.source',
                                config_mode='python',config_lineNumbers=True,
                                config_indentUnit=4,config_keyMap='softTab',
                                height='100%',
                                readOnly=readOnly)
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