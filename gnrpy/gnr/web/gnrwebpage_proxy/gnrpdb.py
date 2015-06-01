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
        bc = pane.borderContainer()
        self.page.codeEditor.mainPane(bc.contentPane(region='center',overflow='hidden'),editorName='pdbEditor',
                                    mainModule=True,readOnly=True,dataInspector=False,datapath='.editor',
                                    onSelectedPage="""if($1.selected==true){
                                        genro.pdb.onSelectedEditorPage($1.page);
                                    }""",**kwargs)
        self.debuggerCommands(bc.framePane('pdbCommands',region='bottom',height='250px',datapath='.debugger'))
        
    def debuggerCommands(self,frame):
        bc =  frame.center.borderContainer()
        self.debuggerTop(frame.top)
        self.debuggerLeft(bc)
        self.debuggerRight(bc)
       # self.debuggerBottom(frame.bottom)
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
                     labelAttribute='caption',_class='branchtree noIcon',autoCollapse=True)
        
    def debuggerRight(self,bc):
        bc=bc.borderContainer(width='250px',splitter=True,region='right',margin='2px',border='1px solid #efefef',margin_left=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Current')
        bc.contentPane(region='center',padding='2px').tree(storepath='_dev.pdb.result',openOnClick=True,autoCollapse=True,
                 labelAttribute='caption',_class='branchtree noIcon',hideValues='*')

    def debuggerCenter(self,bc):
        bc=bc.borderContainer(region='center',border='1px solid #efefef',margin='2px',margin_right=0,margin_left=0,rounded=4)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Output')
        center=bc.contentPane(region='center',padding='2px',border_bottom='1px solid silver')
        center.div(value='^.output', style='font-family:monospace; white-space:pre')
        lastline=center.div(position='relative')
        lastline.div('>>>',position='absolute',top='1px',left='0px')
        debugger_input=lastline.div(position='absolute',top='0px',left='20px',right='5px').input(value='^.command',width='100%',border='0px')
        center.dataController("""SET .output=output? output+_lf+line:line;""",line='^_dev.pdb.debugger.output_line',output='=.output')
        center.dataController("""SET _dev.pdb.debugger.output_line=command; 
                                 command='!'+command;
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


    def onPageStart(self):
        breakpoints = self.page.pageStore().getItem('_pdb.breakpoints')
        bp = 0
        if breakpoints:
            debugger = GnrPdb(instance_name=self.page.site.site_name, page_id=self.page.page_id)
            for modulebag in breakpoints.values():
                for module,line,condition in modulebag.digest('#a.module,#a.line,#a.condition'):
                    bp +=1
                    debugger.set_break(filename=module,lineno=line,cond=condition)
            if bp:
                debugger.start_debug(sys._getframe().f_back)


class GnrPdb(pdb.Pdb):
    
    def __init__(self, instance_name=None, page_id=None, completekey='tab', skip=None):
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
        return 'B64:%s'%base64.b64encode(envelope.toXml())

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




