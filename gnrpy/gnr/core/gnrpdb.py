import pdb
import socket
from gnr.app.gnrconfig import gnrConfigPath
import os
from gnr.core.gnrbag import Bag
import base64
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
        
        
    def print_stack_entry(self, frame_lineno, prompt_prefix=None):
       # frame, lineno = frame_lineno
       #if frame is self.curframe:
       #    print >>self.stdout, '>',
       #else:
       #    print >>self.stdout, ' ',
        print >>self.stdout, self.format_stack_entry(frame_lineno)
    
    def format_stack_entry(self, frame_lineno, lprefix=': '):
        
        import linecache, repr
        frame, lineno = frame_lineno
        filename = self.canonic(frame.f_code.co_filename)
        s = '%s(%r)' % (filename, lineno)
        result=Bag(lineno=lineno,filename=filename,functionName=frame.f_code.co_name or '"<lambda>"')
        if frame.f_code.co_name:
            s = s + frame.f_code.co_name
        else:
            s = s + "<lambda>"
        if '__args__' in frame.f_locals:
            args = frame.f_locals['__args__']
        else:
            args = None
        result['args']=args
        if args:
            s = s + repr.repr(args)
        else:
            s = s + '()'
        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            s = s + '->'
            s = s + repr.repr(rv)
            result['return']=repr.repr(rv)
        line = linecache.getline(filename, lineno, frame.f_globals)
        if line: s = s + lprefix + line.strip()
        return 'B64:%s'%base64.b64encode(result.toXml())