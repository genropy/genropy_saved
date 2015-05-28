#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  developer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
import sys
import datetime
from time import time
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method

class GnrWebDeveloper(GnrBaseProxy):
    def init(self, **kwargs):
        #self.db = self.page.db
        self.debug = getattr(self.page, 'debug', False)
        self._sqlDebugger = None
        self._pyDebugger = None


    @property
    def pyDebugger(self):
        if not self._pyDebugger:
            self._pyDebugger = GnrPyDebugger(self)
        return self._pyDebugger


    @property
    def sqlDebugger(self):
        if not self._sqlDebugger:
            self._sqlDebugger = GnrSqlDebugger(self)
        return self._sqlDebugger

    @property
    def db(self):
        return self.page.db


    def event_onCollectDatachanges(self):
        if self._sqlDebugger:
            self.sqlDebugger.onCollectDatachanges()


    def onDroppedMover(self,file_path=None):
        import tarfile
        f = tarfile.open(file_path)
        f.extractall(self.page.site.getStaticPath('user:temp'))        
        os.remove(file_path)
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        indexbag = Bag(indexpath)
        indexbag.getNode('movers').attr.update(imported=True)
        indexbag.toXml(indexpath)
        
    @public_method
    def loadCurrentMover(self):
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        if os.path.isfile(indexpath):
            indexbag = Bag(indexpath)
            imported = indexbag['movers?imported']
            tablesbag = indexbag['movers']
            _class = 'mover_imported' if imported else None
            for n in indexbag['records']:
                tablesbag.getNode(n.label).attr.update(pkeys=dict([(pkey,True) for pkey in n.value.keys()],_customClasses=_class))
            return tablesbag
                
    @public_method
    def importMoverLines(self,table=None,objtype=None,pkeys=None):
        databag = Bag(self.page.site.getStaticPath('user:temp','mover','data','%s_%s.xml' %(table.replace('.','_'),objtype)))
        tblobj = self.db.table(table) if objtype=='record' else self.db.table('adm.userobject')
        for pkey in pkeys.keys():
            tblobj.insertOrUpdate(databag.getItem(pkey))
        self.db.commit()
        
    @public_method
    def getMoverTableRows(self,tablerow=None,movercode=None,**kwargs):
        pkeys = tablerow['pkeys'].keys()
        table = tablerow['table']
        objtype = tablerow['objtype']
        tblobj = self.db.table(table)
        columns,mask = tblobj.rowcaptionDecode(tblobj.rowcaption)
        if columns:
            columns = ','.join(columns)
        f = tblobj.query(where='$pkey IN :pkeys',pkeys=tablerow['pkeys'].keys(),columns=columns).fetch()
        result = Bag()
        for r in f:
            result.setItem(r['pkey'],None,_pkey=r['pkey'],db_caption=tblobj.recordCaption(record=r),_customClasses='mover_db')
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        if os.path.isfile(indexpath):
            indexbag = Bag(indexpath)
            moverrows = indexbag.getItem('records.%s' %movercode)
            if not moverrows:
                return result
            for pkey in pkeys:
                rownode = moverrows.getNode(pkey)
                if rownode:
                    xml_caption=rownode.attr['caption']
                    if not pkey in result:
                        result.setItem(pkey,None,_pkey=pkey,xml_caption=xml_caption,_customClasses='mover_xml',objtype=objtype,table=tablerow['reftable'])
                    else:
                        result.getNode(pkey).attr.update(xml_caption=xml_caption,_customClasses='mover_both',objtype=objtype,table=tablerow['reftable'])
        return result

    def tarMover(self,movername='mover'):
        import tarfile
        import StringIO
        tf = StringIO.StringIO() 
        f = tarfile.open(mode = 'w:gz',fileobj=tf)
        moverpath = self.page.site.getStaticPath('user:temp','mover')
        f.add(moverpath,arcname='mover')
        f.close()     
        result = tf.getvalue()
        tf.close()
        return result
    
    @public_method
    def downloadMover(self,data=None,movername=None,**kwargs):
        self.saveCurrentMover(data=data)
        return self.tarMover(movername=movername)
    
    @public_method
    def saveCurrentMover(self,data):
        moverpath = self.page.site.getStaticPath('user:temp','mover')
        indexpath = os.path.join(moverpath,'index.xml')
        indexbag = Bag()
        if not os.path.isdir(moverpath):
            os.makedirs(moverpath)
        for movercode,table,pkeys,reftable,objtype in data.digest('#k,#a.table,#a.pkeys,#a.reftable,#a.objtype'):
            pkeys = pkeys.keys()
            databag = self.db.table(table).toXml(pkeys=pkeys,rowcaption=True,
                                                    path=os.path.join(moverpath,'data','%s.xml' %movercode))
            indexbag.setItem('movers.%s' %movercode,None,table=table,count=len(pkeys),reftable=reftable,objtype=objtype)
            indexbag.setItem('records.%s' %movercode,None,table=table)
            for n in databag:
                indexbag.setItem('records.%s.%s' %(movercode,n.label),None,pkey=n.attr['pkey'],caption=n.attr.get('caption')) 
        indexbag.toXml(indexpath,autocreate=True)
        
    def log(self, msg):
        if self.debug:
            f = file(self.logfile, 'a')
            f.write('%s -- %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))
            f.close()

    def _get_logfile(self):
        if not hasattr(self, '_logfile'):
            logdir = os.path.normpath(os.path.join(self.page.site.site_path, 'data', 'logs'))
            if not os.path.isdir(logdir):
                os.makedirs(logdir)
            self._logfile = os.path.join(logdir, 'error_%s.log' % datetime.date.today().strftime('%Y%m%d'))
        return self._logfile

    logfile = property(_get_logfile)


class GnrSqlDebugger(object):
    def __init__(self,parent):
        self.parent = parent
        self._debug_calls = Bag()

    def output(self, page, sql=None, sqlargs=None, dbtable=None, error=None,delta_time=None):
        dbtable = dbtable or '-no table-'
        kwargs=dict(sqlargs)
        kwargs.update(sqlargs)
        delta_time = int((delta_time or 0)*1000)
        if sqlargs and sql:
            formatted_sqlargs = dict([(k,'<span style="background-color:yellow;cursor:pointer;" title="%s" >%%(%s)s</span>' %(v,k)) for k,v in sqlargs.items()])
            value = sql %(formatted_sqlargs)
        if error:
            kwargs['sqlerror'] = str(error)
        self._debug_calls.addItem('%03i Table %s' % (len(self._debug_calls), dbtable.replace('.', '_')), value,_execution_time=delta_time,_time_sql=delta_time,_description=dbtable,_type='sql',
                                  **kwargs)

    def onCollectDatachanges(self):
        page = self.parent.page
        if page.debug_sql and self._debug_calls:
            path = 'gnr.debugger.main.c_%s' % page.callcounter
            attributes=dict(server_time=int((time()-page._start_time)*1000))
            call_kwargs = dict(page._call_kwargs)
            attributes['methodname'] = call_kwargs.pop('method')
            call_kwargs.pop('_lastUserEventTs',None)
            if not call_kwargs.get('_debug_info') and ('table' in call_kwargs or 'dbtable' in call_kwargs):
                call_kwargs['_debug_info'] = 'table: %s' %(call_kwargs.get('table') or call_kwargs.get('dbtable'))
            attributes['debug_info'] = call_kwargs.pop('_debug_info',None)
            #attributes['_method_parameters'] = call_kwargs
            attributes['sql_count'] = len(self._debug_calls)
            attributes['sql_total_time'] = self._debug_calls.sum('#a._time_sql')
            attributes['not_sql_time'] = attributes['server_time'] - attributes['sql_total_time']
            attributes['r_count'] = page.callcounter
            page.setInClientData(path, self._debug_calls,attributes=attributes)

class GnrPyDebugger(object):
    def __init__(self,parent):
        self.parent = parent
        self.sourceEditor = GnrSourceEditor(self.parent.page,frameName='pyDebuggerFrame',readOnly=True,dataInspector=False)
    @public_method
    def debuggerPane(self,pane):
        bc = pane.borderContainer()

        self.sourceEditor.mainPane(bc.contentPane(region='center',overflow='hidden'))
        self.debuggerCommands(bc.framePane('debuggerCommands',region='bottom',splitter=True,height='130px',datapath='.debugger'))

    def debuggerCommands(self,frame):
        bar = frame.top.slotToolbar('2,stepover,stepin,stepout,*,send,2',height='20px')
        bar.stepover.slotButton('Step over')
        bar.stepin.slotButton('Step in')
        bar.stepout.slotButton('Step out')
        #bar.send.slotButton('Send',action='alert("sending")')
        center = frame.center.contentPane()
        out_div = center.div('^.output', style='font-family:monospace; white-space:pre;')
        center.dataController("""console.log('dataController', data);            SET .output = output+_lf+data""",output='=.output',
            subscribe_fromdebugger=True)
        self.debuggerBottom(frame)
        
    def debuggerBottom(self,frame):
        bottom=frame.bottom.contentPane()
        fb = bottom.formbuilder(cols=2)
        fb.textBox(lbl='Command',value='^.command', nodeId='commandField',
                    connect_onkeyup="""
                                      var target = $1.target;
                                      var value = $1.target.value;
                                      var key = $1.keyCode;
                                      if(key==13){
                                         var cmd = value.replace(_lf,"");
                                         genro.wsk.send("debugcommand",{cmd:cmd});
                                         $1.target.value = null;
                                      }""")
    
        fb.button('Send', action='genro.wsk.send("debugcommand",{cmd:cmd}); SET .command=null;', cmd='=.command')


class GnrSourceEditor(object):
    def __init__(self,page=None,frameName=None,readOnly=True,dataInspector=False):
        self.readOnly = readOnly
        self.dataInspector = dataInspector
        self.page = page
        self.frameName = frameName
        self.stackNodeId = '%s_stack' %frameName
        self.mainDocName = '%s.py' %os.path.splitext(sys.modules[page.__module__].__file__)[0]

    def mainPane(self,parent,**kwargs):
        frame = parent.framePane(self.frameName,_class='source_viewer',margin='2px',datapath='.source_viewer')
        slots = ['2','sb','*']
        if not self.readOnly:
            slots.append('readOnlyEditor')
        if self.dataInspector:
            slots.append('dataInspector')
        slots.append('2')
        bar = frame.top.slotToolbar(','.join(slots),height='20px')
        sb = bar.sb.stackButtons(stackNodeId=self.stackNodeId)
        self.sourceFileMenu(sb.div('<div class="multibutton_caption">+</div>',_class='multibutton'))

        sc = frame.center.stackContainer(nodeId=self.stackNodeId)
        bar.dataController("""
            var label = docname.replace(/\./g, '_').replace(/\//g, '_');
            if(sc._value.getNode(label)){
                return;
            }
            var l = docname.split('/');
            var title = l[l.length-1];
            sc._('ContentPane',label,{title:title,datapath:'.page_'+sc._value.len(),
                                        remote:remotemethod,remote_docname:docname,overflow:'hidden',
                                        closable:true})
            """,docname='^.new_source_viewer_page',sc=sc,remotemethod='dev.pyDebugger.sourceEditor.buildEditorTab')
        pane = sc.contentPane(title='Main',datapath='.main',overflow='hidden')
        pane.remote('dev.pyDebugger.sourceEditor.buildEditorTab',docname=self.mainDocName)
        if not self.readOnly:
            parent.dataController("""genro.src.updatePageSource('_pageRoot')""",
                        subscribe_rebuildPage=True,_delay=100)

    def sourceFileMenu(self,pane):
        b = Bag()
        for k,pkgobj in self.page.application.packages.items():
            b.setItem(k,DirectoryResolver(pkgobj.packageFolder,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)(),caption= pkgobj.attributes.get('name_long',k))
        pane.data('.directories',b)
        pane.menu(action='FIRE .new_source_viewer_page = $1.abs_path;', modifiers='*', storepath='.directories', _class='smallmenu')

    def __readsource(self,docname):
        if not os.path.exists(docname):
            return
        with open(docname,'r') as f:
            return f.read()

    @public_method
    def buildEditorTab(self,pane,docname=None,**kwargs):
        center = pane.framePane('sourcePane_%s' %docname.replace('/','_').replace('.','_'),region='center',_class='viewer_box selectable')
        source = self.__readsource(docname)
        self.buildSourceEditor(center,source=source)
        pane.data('.docname',docname)
       #pane.dataRpc('dummy',self.save_source_code,docname='=.docname',
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



    def buildSourceEditor(self,frame,source=None):
        bar = frame.bottom.slotBar('5,fpath,*',height='18px',background='#efefef')
        bar.fpath.div('^.docname',font_size='9px')
        if not self.readOnly:
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
                                readOnly=self.readOnly)
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


