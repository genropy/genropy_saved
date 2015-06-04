#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  developer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
import sys
import pdb
import socket
import base64
import repr
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method
from gnr.app.gnrconfig import gnrConfigPath

class GnrPdbClient(GnrBaseProxy):
    @public_method
    def setBreakpoint(self,module=None,line=None,condition=None,evt=None):
        bpkey = '_pdb.breakpoints.%s.r_%i' %(module.replace('.','_').replace('/','_'),line)
        with self.page.pageStore() as store:
            if evt=='del':
                store.pop(bpkey)
            else:
                store.setItem(bpkey,None,line=line,module=module,condition=condition)

    @public_method
    def getBreakpoints(self,module=None):
        bpkey = '_pdb.breakpoints'
        if module:
            bpkey = '%s.%s' %(bpkey,module.replace('.','_').replace('/','_'))
        return self.page.pageStore().getItem(bpkey)
        

    def onPageStart(self):
        debugger_page_id = self.page.pageStore().getItem('_pdb.debugger_page_id')
        if not debugger_page_id:
            return
        page_breakpoints = self.page.pageStore(debugger_page_id).getItem('_pdb.breakpoints')
        bp = 0
        if page_breakpoints:
            debugger = GnrPdb(page=self.page,instance_name=self.page.site.site_name,debugger_page_id=debugger_page_id,callcounter=self.page.callcounter,
                            methodname=self.page._call_kwargs.get('method'))
            for modulebag in page_breakpoints.values():
                for module,line,condition in modulebag.digest('#a.module,#a.line,#a.condition'):
                    bp +=1
                    debugger.set_break(filename=module,lineno=line,cond=condition)
            if bp:
                print 'debugger start'
                debugger.start_debug(sys._getframe().f_back)

class GnrPdb(pdb.Pdb):
    def __init__(self, page=None,instance_name=None, debugger_page_id=None, completekey='tab',callcounter=None,methodname=None, skip=None):
        self.page=page
        page.debugger=self
        self.pdb_id='D_%s' %id(self)
        self.pdb_counter=0
        self.debugger_page_id = debugger_page_id
        self.socket_path = os.path.join(gnrConfigPath(), 'sockets', '%s_debug.tornado'%instance_name)
        self.callcounter = callcounter
        self.methodname = methodname
        iostream = self.get_iostream()
        pdb.Pdb.__init__(self,completekey=completekey, skip=skip, stdin=iostream, stdout=iostream)
        self.prompt = ''
        
    def get_iostream(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        self.sock.sendall('\0%s\n'%self.debugger_page_id)
        return self.sock.makefile('rw')
        
    def makeEnvelope(self,data):
        envelope=Bag(dict(command='pdb_out_bag',data=data))
        print 'sending envelope',envelope
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
        result['pdb_id'] = self.pdb_id
        result['pdb_counter'] = self.pdb_counter
        result['callcounter'] = self.callcounter
        result['methodname'] = self.methodname
        result['status'] = Bag(dict(level=self.curindex,pdb_id=self.pdb_id,
                                    module = result['current.filename'],
                                    lineno = result['current.lineno'],
                                    functionName=result['functionName'],
                                    pdb_counter=result['pdb_counter']))
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
        try:
            print >>self.stdout, repr(self._getval(arg))
        except:
            pass

    def do_pp(self, arg):
        try:
            import pprint
            pprint.pprint(self._getval(arg), self.stdout)
        except:
            pass
    def do_level(self,level):
        level = int(level)
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




