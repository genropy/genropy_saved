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
import pdb
import socket
import base64
import traceback
import repr
import thread
from time import time
from gnr.core.gnrbag import Bag,DirectoryResolver

from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method
from gnr.app.gnrconfig import gnrConfigPath



class GnrPdbClient(GnrBaseProxy):
        
    @public_method
    def debuggerPane(self,pane,mainModule=None,**kwargs):
        bc = pane.borderContainer(_class='pdb_pane')
        self.page.codeEditor.mainPane(bc.contentPane(region='center',overflow='hidden'),editorName='pdbEditor',
                                    mainModule=True,readOnly=True,dataInspector=False,datapath='.editor',
                                    onSelectedPage="""if($1.selected==true){
                                        genro.pdb.onSelectedEditorPage($1.page);
                                    }""",**kwargs)
        self.debuggerCommands(bc.framePane('pdbCommands',region='bottom',height='250px',
                               splitter=True,datapath='.debugger'))
        
    def debuggerCommands(self,frame):
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
        
    @public_method
    def setConnectionBreakpoint(self,module=None,line=None,condition=None,evt=None):
        bpkey = '_pdb.breakpoints.%s.r_%i' %(module.replace('.','_').replace('/','_'),line)
        with self.page.connectionStore() as store:
            if evt=='del':
                store.pop(bpkey)
                print 'POPPED BP FROM CONNECTION',bpkey
            else:
                store.setItem(bpkey,None,line=line,module=module,condition=condition)
                print 'STORED BP IN CONNECTION',bpkey

    @public_method
    def getBreakpoints(self,module=None):
        bpkey = '_pdb.breakpoints'
        if module:
            bpkey = '%s.%s' %(bpkey,module.replace('.','_').replace('/','_'))
        return self.page.connectionStore().getItem(bpkey)
    
    @public_method
    def saveDebugDataInConnection(self,pdb_page_id,pdb_id,data):
        bpkey = '_pdb.debugdata.%s.%s' %(pdb_page_id,pdb_id)
        with self.page.connectionStore() as store:
            store.setItem(bpkey,data)
        print 'STORED DEBUGDATA IN CONNECTION',bpkey,data
        
    @public_method
    def loadDebugDataFromConnection(self,pdb_page_id,pdb_id):
        bpkey = '_pdb.debugdata.%s.%s' %(pdb_page_id,pdb_id)
        with self.page.connectionStore() as store:
            data = store.getItem(bpkey)
        #print 'LOADED DEBUGDATA IN CONNECTION',bpkey,data
        return data
        
        
    def set_trace(self):
        debugger = GnrPdb(instance_name=self.page.site.site_name, page_id=self.page.page_id)
        try:
            debugger.set_trace(sys._getframe().f_back)
        except Exception,e:
            traceback.print_exc()


    def onPageStart(self):
        if getattr(self.page,'pdb_ignore',None):
            return
        page_breakpoints = self.page.pageStore().getItem('_pdb.breakpoints')
        
        bp = 0
        if page_breakpoints:
            debugger = GnrPdb(page=self.page,instance_name=self.page.site.site_name,
             page_id=self.page.page_id, pdb_mode='P')

            for modulebag in page_breakpoints.values():
                for module,line,condition in modulebag.digest('#a.module,#a.line,#a.condition'):
                    bp +=1
                    debugger.set_break(filename=module,lineno=line,cond=condition)
            if bp:
                debugger.start_debug(sys._getframe().f_back)
        else:
            connection_breakpoints = self.page.pdb.getBreakpoints()
            if connection_breakpoints:
                debugger = GnrPdb(page=self.page,instance_name=self.page.site.site_name,
                               page_id=self.page.page_id, pdb_mode='C')
                debugger.pdb_id=id(debugger)
                for modulebag in connection_breakpoints.values():
                    for module,line,condition in modulebag.digest('#a.module,#a.line,#a.condition'):
                        bp +=1
                        debugger.set_break(filename=module,lineno=line,cond=condition)
                if bp:
                    debugger.start_debug(sys._getframe().f_back)

class GnrPdb(pdb.Pdb):
    
    def __init__(self, page=None,instance_name=None, page_id=None, completekey='tab', skip=None,pdb_mode=None):
        self.page=page
        page.debugger=self
        self.pdb_id=id(self)
        self.pdb_mode=pdb_mode
        self.pdb_counter=0
        self.page_id = page_id
        self.socket_path = os.path.join(gnrConfigPath(), 'sockets', '%s_debug.tornado'%instance_name)
        iostream = self.get_iostream()
        pdb.Pdb.__init__(self,completekey=completekey, skip=skip, stdin=iostream, stdout=iostream)
        self.prompt = ''
        
    def get_iostream(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        self.sock.sendall('\0%s\n'%self.page_id)
        return self.sock.makefile('rw')
        
    def makeEnvelope(self,data):
        envelope=Bag(dict(command='pdb_out_bag',data=data))
        return 'B64:%s'%base64.b64encode(envelope.toXml(unresolved=True))
        #onBuildTag=self.onBuildTag))
    
    def onBuildTag(self,label=None,value=None,attributes=None):
        if not isinstance(value,Bag):
            attributes['__value__']=repr.repr(value)
        
            
    def getStackBag(self,frame):
        result = Bag()
        for frame,lineno in self.stack:
            framebag = self.frameAsBag(frame, lineno)
            module=framebag['filename']
            lineno=framebag['lineno']
            functionName=framebag['functionName']
            level = len(result)
            key = 'r_%i' %level
            caption = '<span class="pdb_caption_module">%s</span><span class="pdb_caption_function"> %s </span><span class="pdb_caption_lineno">%i</span>' % (os.path.basename(module),functionName,lineno)
           #if level == self.curindex:
           #    caption = '<span class="pdb_current_stack"> %s </span>' %caption
            caption = 'innerHTML:%s' %caption
            result.setItem(key,framebag,caption= caption,level=level,labelClass='pdb_current_stack' if level == self.curindex else None)
        return result
        
    def print_stack_entry(self, frame_lineno, prompt_prefix=None):
        print >>self.stdout,self.format_stack_entry(frame_lineno)
            
    def format_stack_entry(self, frame_lineno, lprefix=': '):
        frame, lineno = frame_lineno
        result = Bag()
        result['current'] = self.frameAsBag(frame,lineno)
        result['stack'] = self.getStackBag(frame)
        result['watches'] = self.getWatches(frame)
        result['bplist'] = self.getBreakpointList()
        result['level'] = self.curindex
        result['pdb_mode'] = self.pdb_mode
        result['pdb_id'] = self.pdb_id
        result['pdb_counter'] = self.pdb_counter
        result['status'] = Bag(dict(level=self.curindex,pdb_mode=self.pdb_mode,pdb_id=self.pdb_id,
                                    module = result['current.filename'],
                                    lineno = result['current.lineno'],
                                    functionName=result['functionName'],
                                    pdb_counter=result['pdb_counter']))
        if self.pdb_mode=='C':
            debug_data = result.toXml(unresolved=True)
            self.page.pdb.saveDebugDataInConnection(self.page_id,self.pdb_id,debug_data)
        self.pdb_counter +=1

        return self.makeEnvelope(result)

    def getBreakpointList(self):
        return Bag()

    def start_debug(self, frame=None):
        """Start debugging from `frame`.
    
        If frame is not specified, debugging starts from caller's frame.
        """
        if frame is None:
            frame = sys._getframe().f_back
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.set_continue()
        sys.settrace(self.trace_dispatch)

    def getWatches(self,frame):
        return Bag()

    def frameAsBag(self,frame,lineno):
        filename = self.canonic(frame.f_code.co_filename)
        result=Bag(lineno=lineno,filename=filename,functionName=frame.f_code.co_name or '"<lambda>"')
        result['locals']=Bag(dict(frame.f_locals))
        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            result['returnValue']=repr.repr(rv)
        return result


    def do_p(self, arg):
        print 'do_p'
        try:
            print >>self.stdout, repr(self._getval(arg))
        except:
            pass

    def do_pp(self, arg):
        print 'do_p'
        try:
            pprint.pprint(self._getval(arg), self.stdout)
        except:
            pass
    def do_level(self,level):
        level = int(level)
        print 'setting stacklevel',level
        maxlevel = len(self.stack)-1
        if not level or level>maxlevel:
            level = maxlevel
        elif level<0:
            level = 0
        self.curindex = level
        self.curframe = self.stack[self.curindex][0]
        self.curframe_locals = self.curframe.f_locals
        self.print_stack_entry(self.stack[self.curindex])
        self.lineno = None




