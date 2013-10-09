# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbag : an advanced data storage system
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA



import Pyro4
from gnr.core.gnrbag import Bag

PYRO_HOST = 'localhost'
PYRO_PORT = 40004
PYRO_HMAC_KEY = 'supersecretkey'

class RemoteBagStore(object):
    def __init__(self):
        self.store=Bag()
        
    def __getattr__(self,name):
        store = self.store
        if not hasattr(store,name):
            raise AttributeError("PyroBag has no attribute '%s'" % name)
        h = getattr(store,name)
        if not callable(h):
            return h
        def decore(*args,**kwargs):
            if '_pyrosubbag' in kwargs:
                _pyrosubbag = kwargs.pop('_pyrosubbag')
                substore = store.getItem(_pyrosubbag)
                subh = getattr(substore,name)
                if not subh:
                    raise AttributeError("PyroSubBag at %s has no attribute '%s'" % (_pyrosubbag,name))
                else:
                    return subh(*args,**kwargs)
            else:
                return h(*args,**kwargs)
        return decore
        
class RemoteBagServer(object):
    def __init__(self,host=None,port=None,hmac_key=None):
        self.stores = dict()
        self.uridict= dict()
        self.host = host or PYRO_HOST
        self.port = port or PYRO_PORT
        self.hmac_key =  str(hmac_key or PYRO_HMAC_KEY)
        self.run()

    def run(self):
        Pyro4.config.HMAC_KEY = self.hmac_key
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        self.daemon = Pyro4.Daemon(host=self.host,port=self.port)
        self.main_uri = self.daemon.register(self,'RemoteBagServer')
        print "uri=",self.main_uri
        self.daemon.requestLoop()

    def remoteBag(self,name):
        if not name in self.uridict:
            newbag = RemoteBagStore()
            self.uridict[name] = self.daemon.register(newbag,name)
            self.stores[name] = newbag
        return self.uridict[name]
    
       
class RemoteSubBag():
    def __init__(self,parent,rootpath):
        self.parent = parent
        self.rootpath = rootpath

    def __getattr__(self,name):
        if not hasattr(Bag,name):
            raise AttributeError("RemoteBag has no attribute '%s'" % name)
        h = getattr(self.parent.proxy,name) 
        if not callable(h):
            return h
        def decore(*args,**kwargs):
            kwargs['_pyrosubbag'] = self.rootpath
            return h(*args,**kwargs)
        return decore

class RemoteBagProxy():
    def __init__(self,uri):
        self.proxy=Pyro4.Proxy(uri)

    def subBag(self,subpath):
        return RemoteSubBag(self,subpath)
    
    def __getattr__(self,name):
        if not hasattr(Bag,name):
            raise AttributeError("RemoteBag has no attribute '%s'" % name)
        return getattr(self.proxy,name)

class RemoteBagClient(object):
    def __init__(self,uri=None,port=None,host=None,hmac_key=None):
        host = host or PYRO_HOST
        port = port or PYRO_PORT
        hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        Pyro4.config.HMAC_KEY = hmac_key
        uri = uri or 'PYRO:RemoteBagServer@%s:%i' %(host,port)
        self.proxy=Pyro4.Proxy(uri)
        
    def remoteBag(self,name):
        uri= self.proxy.remoteBag(name)
        return RemoteBagProxy(uri)
        
def main():
    remotebag = RemoteBagServer()
    remotebag.run()


if __name__=="__main__":
    main()