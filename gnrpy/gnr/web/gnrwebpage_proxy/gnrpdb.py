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
                                    mainModule=mainModule,readOnly=True,dataInspector=False,datapath='.editor',**kwargs)
        self.debuggerCommands(bc.framePane('pdbCommands',region='bottom',splitter=True,height='250px',datapath='.debugger'))


    def debuggerCommands(self,frame):
        self.debuggerTop(frame.top)
        self.debuggerLeft(frame.left)
        self.debuggerRight(frame.right)
        self.debuggerBottom(frame.bottom)
        self.debuggerCenter(frame.center)
        
    def debuggerTop(self,top):
        bar = top.slotToolbar('5,stepover,stepin,stepout,*')
        bar.stepover.slotButton('Step over')
        bar.stepin.slotButton('Step in')
        bar.stepout.slotButton('Step out')
        
    def debuggerLeft(self,left):
        pane=left.contentPane(width='120px',border_right='1px solid silver',splitter=True)
        pane.tree(storepath='_dev.pdb.output')
        
    def debuggerRight(self,right):
        pane=right.contentPane(width='120px',border_left='1px solid silver',splitter=True)
        pane.div('watches')
        
    def debuggerCenter(self,center):
        center.div('^.output', style='font-family:monospace; white-space:pre;')

        
    def debuggerBottom(self,bottom):
        pane=bottom.contentPane(height='40px',border_top='1px solid silver',splitter=True)
        
        fb = pane.formbuilder(cols=2)
        fb.textBox(lbl='Command',value='^.command', 
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
        
    def set_trace(self):
        self.debugger = GnrPdb(instance_name=self.page.site.site_name, page_id=self.page.page_id)
        try:
            print 'TRYING'
            self.debugger.set_trace(sys._getframe().f_back)
        except Exception,e:
            print '###### ERRORE',str(e)
            traceback.print_exc()


class GnrPdb(pdb.Pdb):
    
    def __init__(self, instance_name=None, page_id=None, completekey='tab', skip=None):
        self.page_id = page_id
        self.socket_path = os.path.join(gnrConfigPath(), 'sockets', '%s_debug.tornado'%instance_name)
        iostream = self.get_iostream()
        pdb.Pdb.__init__(self,completekey=completekey, skip=skip, stdin=iostream, stdout=iostream)
        
    def get_iostream(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        self.sock.sendall('\0%s\n'%self.page_id)
        return self.sock.makefile('rw')
        
    def makeEnvelope(self,data):
        envelope=Bag(dict(command='set',data=Bag(dict(path='_dev.pdb.output',data=data))))
        envelope=Bag(dict(command='pdb_out',data=data))

        return 'B64:%s'%base64.b64encode(envelope.toXml(unresolved=True))
        
    def print_stack_entry(self, frame_lineno, prompt_prefix=None):
        print >>self.stdout, self.format_stack_entry(frame_lineno)
            
    def format_stack_entry(self, frame_lineno, lprefix=': '):
        import repr
        frame, lineno = frame_lineno
        filename = self.canonic(frame.f_code.co_filename)
        result=Bag(lineno=lineno,filename=filename,functionName=frame.f_code.co_name or '"<lambda>"')
        result['locals']=Bag(dict(frame.f_locals))
        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            result['return']=repr.repr(rv)
        return self.makeEnvelope(result)



