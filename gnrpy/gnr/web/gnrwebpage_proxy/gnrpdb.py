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
        self.debuggerCommands(bc.framePane('pdbCommands',region='bottom',splitter=True,height='250px',datapath='.debugger'))
        
    def debuggerCommands(self,frame):
        self.debuggerTop(frame.top)
        self.debuggerLeft(frame.left)
        self.debuggerRight(frame.right)
       # self.debuggerBottom(frame.bottom)
        self.debuggerCenter(frame.center)
        
    def debuggerTop(self,top):
        bar = top.slotToolbar('5,stepover,stepin,stepout,cont,*,stackmenu,5')
        bar.stepover.slotButton('Step over',action='genro.pdb.do_stepOver()')
        bar.stepin.slotButton('Step in',action='genro.pdb.do_stepIn()')
        bar.stepout.slotButton('Step out',action='genro.pdb.do_stepOut()')
        bar.cont.slotButton('Continue',action='genro.pdb.do_continue()')
        bar.stackmenu.dropDownButton('Stack').menu(storepath='_dev.pdb.stackMenu',action='genro.pdb.onSelectStackMenu($1)')
        
    def debuggerLeft(self,pane):
        bc=pane.borderContainer(width='250px',splitter=True)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Stack')
        bc.contentPane(region='center',padding='2px').tree(storepath='_dev.pdb.stack',
                     labelAttribute='caption',_class='branchtree noIcon')
        
    def debuggerRight(self,pane):
        bc=pane.borderContainer(width='250px',splitter=True)
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Current')
        bc.contentPane(region='center',padding='2px').tree(storepath='_dev.pdb.result',
                 labelAttribute='caption',_class='branchtree noIcon')

    def debuggerCenter(self,pane):
        bc=pane.borderContainer(border='1px solid silver',border_top='0px')
        bc.contentPane(region='top',background='#666',color='white',font_size='.8em',text_align='center',padding='2px').div('Output')
        center=bc.contentPane(region='center',padding='2px',border_bottom='1px solid silver',)
        center.div('^.output', style='font-family:monospace; white-space:pre;')
        bottom=bc.contentPane(region='bottom',padding='2px',splitter=True)
        fb = bottom.formbuilder(cols=2)
        fb.textBox(lbl='Command',value='^.command',onEnter='FIRE .sendCommand')
        #fb.textBox(lbl='Command',value='^.command', connect_onkeyup="""
        #                              var target = $1.target;
        #                              var value = $1.target.value;
        #                              var key = $1.keyCode;
        #                              if(key==13){
        #                                 var cmd = value.replace(_lf,"");
        #                                 genro.pdb.sendCommand(cmd);
        #                                 $1.target.value = null;
        #                              }""")
    
        fb.button('Send', fire='.sendCommand')
        fb.dataController('genro.pdb.sendCommand(command);SET .command=null;',command='=.command',
                        _fired='^.sendCommand')
        

    
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
        envelope=Bag(dict(command='pdb_out',data=data))
        return 'B64:%s'%base64.b64encode(envelope.toXml(unresolved=True))

    def getStackBag(self,frame):
        result = Bag()
        for frame,lineno in self.stack:
            framebag = self.frameAsBag(frame, lineno)
            module=framebag['filename']
            lineno=framebag['lineno']
            functionName=framebag['functionName']
            level = len(result)
            key = 'r_%i' %level
            caption = '%s - %s [%i])' % (os.path.basename(module),functionName,lineno)
            result.setItem(key,framebag,caption= caption,level=level)
        return result
        
    def print_stack_entry(self, frame_lineno, prompt_prefix=None):
        print >>self.stdout,self.format_stack_entry(frame_lineno)
            
    def format_stack_entry(self, frame_lineno, lprefix=': '):
        frame, lineno = frame_lineno
        result = Bag()
        result['current'] = self.frameAsBag(frame,lineno)
        result['stack'] = self.getStackBag(frame)
        result['watches'] = self.getWatches(frame)
        return self.makeEnvelope(result)

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




