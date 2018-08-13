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
from bdb import Breakpoint

class GnrPdbClient(GnrBaseProxy):
    @public_method
    def setBreakpoint(self,module=None,line=None,condition=None,evt=None):
        bpkey = '_pdb.breakpoints.%s.r_%i' %(module.replace('.','_').replace('/','_'),line)
        with self.page.connectionStore() as store:
            if evt=='del':
                store.pop(bpkey)
            else:
                store.setItem(bpkey,None,line=line,module=module,condition=condition)

    @public_method
    def getBreakpoints(self,module=None):
        bpkey = '_pdb.breakpoints'
        if module:
            bpkey = '%s.%s' %(bpkey,module.replace('.','_').replace('/','_'))
        return self.page.connectionStore().getItem(bpkey)
        

    def onPageStart(self):
        connectionStore = self.page.connectionStore()
        debugger_page_id = connectionStore.getItem('_dev.gnride_page_id')
        if not debugger_page_id or self.page.page_id==debugger_page_id:
            return
        breakpoints = connectionStore.getItem('_pdb.breakpoints')
        bp = 0
        if breakpoints:
            debugger = GnrPdb(page=self.page,instance_name=self.page.site.site_name,debugger_page_id=debugger_page_id,callcounter=self.page.callcounter,
                            methodname=self.page._call_kwargs.get('method'))
            for modulebag in breakpoints.values():
                for module,line,condition in modulebag.digest('#a.module,#a.line,#a.condition'):
                    bp +=1
                    debugger.set_break(filename=module,lineno=line,cond=condition)
            if bp:
                debugger.start_debug(sys._getframe().f_back)
            
class GnrPdb(pdb.Pdb):
    def __init__(self, page=None,instance_name=None, debugger_page_id=None, completekey='tab',callcounter=None,methodname=None, skip=None):
        self.page=page
        page.debugger=self
        self.pdb_id='D_%s' %id(self)
        self.pdb_counter=0
        self.debugger_page_id = debugger_page_id
        self.socket_path = os.path.join(page.site.site_path, 'sockets', 'debugger.sock')
        self.callcounter = callcounter
        self.methodname = methodname
        self.mybp = []
        iostream = self.get_iostream()
        pdb.Pdb.__init__(self,completekey=completekey, skip=skip, stdin=iostream, stdout=iostream)
        self.prompt = ''
        
    def get_iostream(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        self.sock.sendall('\0%s,%s\n'%(self.debugger_page_id,self.pdb_id))
        return self.sock.makefile('rw')
        
    def makeEnvelope(self,data):
        envelope=Bag(dict(command='pdb_out_bag',data=data))
        return 'B64:%s'%base64.b64encode(envelope.toXml(unresolved=True))

    def onClosePage(self):
        for bpinstance in self.mybp:
            bpinstance.deleteMe()
        self.page.wsk.sendCommandToPage(self.debugger_page_id,'close_debugger',self.pdb_id)
            
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
        result['debugged_page_id'] = self.page.page_id
        result['status'] = Bag(dict(level=self.curindex,pdb_id=self.pdb_id,
                                    module = result['current.filename'],
                                    lineno = result['current.lineno'],
                                    functionName=result['functionName'],
                                    pdb_counter=result['pdb_counter']))
        self.page.wsk.publishToClient(self.page.page_id,'debugstep',
                data=Bag(dict(current=result['current'],pdb_id=self.pdb_id,methodname=self.methodname,
                                                        functionName=result['current.functionName'],
                                                        lineno=result['current.lineno'],
                                                        debugger_page_id=self.debugger_page_id,
                                                        filename=os.path.basename(result['current.filename']),
                                                        callcounter=self.callcounter)))
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

    def set_break(self, filename, lineno, temporary=0, cond = None,
                  funcname=None):
        filename = self.canonic(filename)
        import linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        if not line:
            return 'Line %s:%d does not exist' % (filename,
                                   lineno)
        if not filename in self.breaks:
            self.breaks[filename] = []
        list = self.breaks[filename]
        if not lineno in list:
            list.append(lineno)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)
        self.mybp.append(bp)

    def clear_break(self, filename, lineno):
        filename = self.canonic(filename)
        if not filename in self.breaks:
            return 'There are no breakpoints in %s' % filename
        if lineno not in self.breaks[filename]:
            return 'There is no breakpoint at %s:%d' % (filename,
                                    lineno)
        # If there's only one bp in the list for that file,line
        # pair, then remove the breaks entry
        for bp in Breakpoint.bplist[filename, lineno][:]:
            bp.deleteMe()
            self.mybp.remove(bp)
        self._prune_breaks(filename, lineno)

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




