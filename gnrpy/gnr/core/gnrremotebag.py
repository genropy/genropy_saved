
# # -*- coding: UTF-8 -*-
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


def wrapper(func):
        def decore(self,*args,**kwargs):
            if self.rootpath:
                kwargs['_pyrosubbag'] = self.rootpath
            return func(self,*args,**kwargs)
        return decore

#------------------------------- SERVER SIDE ---------------------------
class RemoteBagInstance(object):
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
        self.start()

    def start(self):
        Pyro4.config.HMAC_KEY = self.hmac_key
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        self.daemon = Pyro4.Daemon(host=self.host,port=self.port)
        self.main_uri = self.daemon.register(self,'RemoteBagServer')
        print "uri=",self.main_uri
        self.daemon.requestLoop()

    def store_get(self,name):
        if not name in self.uridict:
            newbag = RemoteBagInstance()
            self.uridict[name] = self.daemon.register(newbag,'remotebag_%s'%name)
            self.stores[name] = newbag
        return self.uridict[name]
    
    def store_remove(self,name):
        if name in self.stores:
            self.daemon.unregister(self.stores[name])
            self.stores.pop(name) 
            self.uridict.pop(name) 
        
    def store_list(self):
        return self.stores.keys()

class RemoteBag(object):
    def __init__(self,uri=None,parent=None,rootpath=None):
        self.proxy=Pyro4.Proxy(uri) if uri else None
        self.parent=parent
        self.rootpath=rootpath

    def subBag(self,path):
        return RemoteBag(parent=self,rootpath=path)
        
    @wrapper
    def __str__(self):
        return self.proxy.asString()
        
    @wrapper 
    def __getitem__(self,*args,**kwargs):
        return self.proxy.__getitem__(*args,**kwargs)
        
    @wrapper 
    def __setitem__(self,*args,**kwargs):
        return self.proxy.__setitem__(*args,**kwargs)
    
    @wrapper 
    def __len__(self,*args,**kwargs):
        return self.proxy.__len__(*args,**kwargs)
        
        
    def __getattr__(self,name):
        if not hasattr(Bag,name):
            raise AttributeError("RemoteBag has no attribute '%s'" % name)
        if self.proxy:
            return getattr(self.proxy,name)
        h = getattr(self.parent.proxy,name) 
        if not callable(h):
            return h
        def decore(*args,**kwargs):
            kwargs['_pyrosubbag'] = self.rootpath
            return h(*args,**kwargs)
        return decore

class RemoteBagClient(object):
    def __init__(self,uri=None,port=None,host=None,hmac_key=None):
        host = host or PYRO_HOST
        port = port or PYRO_PORT
        hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        Pyro4.config.HMAC_KEY = hmac_key
        Pyro4.config.SERIALIZER = 'pickle'
        uri = uri or 'PYRO:RemoteBagServer@%s:%i' %(host,port)
        self.proxy=Pyro4.Proxy(uri)
        
    def __call__(self,name):
        uri= self.proxy.store_get(name)
        return RemoteBag(uri=uri)
        
    def stores(self):
        return self.proxy.store_list()

    def remove(self,name):
        return self.proxy.store_remove(name)
        
def test_simple():
    rbc = RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    test_bag = rbc('test_simple')
    test_bag['foo'] = 23
    assert test_bag['foo']==23, 'broken'
    print len(test_bag)
    print 'OK'

def test_subBag():
    rbc = RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    bag = rbc('test_subBag')
    bag['dati.persone.p1.nome'] = 'Mario'
    bag['dati.persone.p1.cognome'] = 'Rossi'
    bag['dati.persone.p1.eta'] = 40

    bag['dati.persone.p2.nome'] = 'Luigi'
    bag['dati.persone.p2.cognome'] = 'Bianchi'
    bag['dati.persone.p2.eta'] = 30
    print bag
    z=bag.getItem('dati.persone')
    print z.asString()
    p1 = bag.subBag('dati.persone.p1')
    print p1.asString()
   #print p1['nome']
   #p1['nome'] = 'Mariotto'
   #assert p1['nome'] == bag['dati.persone.p1.nome'], 'test fallito'
    print 'OK'
def test_client():
    client= RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    mybag=client('mybag')
    mybag['data.people.p1.name']='John'
    mybag['data.people.p1.surname']='Brown'
    mybag['data.people.p1.age']=36
    mybag['data.people.p2.name']='Mary'
    mybag['data.people.p2.surname']='Smith'
    mybag['data.people.p2.age']=29
    m=mybag.getItem('data')
    print 'data.people.p1.name',m

        
if __name__=="__main__":
    test_simple()
    test_client()
    test_subBag()