import pdb
import socket
from gnr.app.gnrconfig import gnrConfigPath
import os

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
    
    