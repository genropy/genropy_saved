# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver
import os
import sys

class GnrCustomWebPage(object):

    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        bc = root.borderContainer(design='sidebar',datapath='main')
        self.drawerPane(bc.framePane(frameCode='drawer',region='left',width='250px',splitter=True,drawer=True,background='rgba(230, 230, 230, 1)'))

        frame = bc.framePane(frameCode='editingPages',datapath='main',selectedPage='^.selectedPage',region='center')
        bar = frame.top.slotToolbar('5,stackButtons,*,readOnlySlot,5',height='20px')
        bar.data('main.readOnly',True)
        bar.readOnlySlot.div().checkbox(value='^main.readOnly', label='Read Only')
        sc = frame.center.stackContainer(nodeId='codeEditor',selectedPage='^.selectedModule')
        #sc.contentPane(title='fooo')
        bar.dataController("""
            if(abs_path in sc.widget.gnrPageDict){
                return
            }
            var label = abs_path.replace(/\./g, '_').replace(/\//g, '_');
            sc._('ContentPane',label,{title:nodecaption,datapath:'.page_'+sc._value.len(),
                                        overflow:'hidden',
                                        pageName:abs_path,closable:true
                                        })._('ContentPane',{remote:remotemethod,remote_docPath:abs_path,overflow:'hidden'})
            SET .selectedModule = abs_path;
            """,sc=sc,remotemethod=self.buildEditorTab,editorName='codeEditor',
            subscribe_openEditorPage=True)


    def drawerPane(self,frame):
        b = Bag()
        frame.top.slotToolbar('*,searchOn,2',height='20px')
        for k,pkgobj in self.application.packages.items():
            b.setItem(k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))

        
        frame.data('.directories.root',b,nodecaption='Project')
        pane = frame.center.contentPane(overflow='auto')
        pane.div(padding='10px').tree(nodeId='drawer_tree',storepath='.directories',
                        connect_ondblclick="""var ew = dijit.getEnclosingWidget($1.target);
                                              console.log('ew',ew)
                                              if(ew.item && ew.item.attr.file_ext!='directory'){
                                                    genro.publish('openEditorPage',ew.item.attr)
                                              }
                                             """,_class='branchtree noIcon',
            hideValues=True,openOnClick=True,labelAttribute='nodecaption',font_size='')

    @public_method
    def buildEditorTab(self,pane,docPath=None,**kwargs):

        frameCode = docPath.replace('/','_').replace('.','_')
        frame = pane.framePane(frameCode=frameCode ,region='center',_class='viewer_box selectable')
        source = self.__readsource(docPath)
        pane.data('.docPath',docPath)
        bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
        bar.fpath.div('^.docPath',font_size='9px')
        frame.data('.source',source)
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
                                readOnly='^main.readOnly')

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
