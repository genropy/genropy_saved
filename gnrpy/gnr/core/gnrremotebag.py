
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
    class_prefix = 'M_'
    def __init__(self,name,parent=None):
        self.name = name
        self.parent = parent
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

    def unregister(self,name=None):
        pass

    def registeringName(self):
        return '%s_%s'%(self.parent.registeringName(), self.memberName()) 

    def memberName(self):
        return '%s%s'%(self.class_prefix, self.name)
class RemoteBagServerBase(object):
    def __init__(self,name = None,parent=None):
        self.store = dict()
        self.identifiers = dict()        
        self.name = name
        self.parent = parent
        print parent
        if parent is not None:
            self.daemon = parent.daemon

    def registeringName(self):
        if self.parent is not None:
            return '%s_%s'%(self.parent.registeringName(), self.memberName()) 
        else:
            return self.memberName()

    def memberName(self):
        return '%s%s'%(self.class_prefix, self.name)

    def keys(self):
        return self.store.keys()

    def getUri(self,name):
        if not name in self.identifiers:
            child = self.child_factory(name,parent=self)
            self.identifiers[name] = self.daemon.register(child, child.registeringName())
            self.store[name] = child
        return self.identifiers[name]

    def unregister(self,name=None):
        member = self.store.get(name)
        if not member:
            return
        for child_name in member.keys():
            member.unregister(child_name)
        self.daemon.unregister(member)
        self.store.pop(name) 
        self.identifiers.pop(name)

    def __len__(self):
        return len(self.store)


class RemoteBagRegister(RemoteBagServerBase):
    class_prefix = 'R_'
    child_factory = RemoteBagInstance

class RemoteBagSpace(RemoteBagServerBase):
    class_prefix = 'S_'
    child_factory = RemoteBagRegister
        
class RemoteBagServer(RemoteBagServerBase):
    class_prefix = ''
    child_factory = RemoteBagSpace

    def start(self,host=None,port=None,hmac_key=None,
                      debug=False,compression=False,timeout=None,
                      multiplex=False,polltimeout=None):
        
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        
        port=port or PYRO_PORT
        host=host or PYRO_HOST
        hmac_key=hmac_key or PYRO_HMAC_KEY
        Pyro4.config.HMAC_KEY = str(hmac_key)
        if compression:
            Pyro4.config.COMPRESSION = True
        if multiplex:
            Pyro4.config.SERVERTYPE = "multiplex"
        if timeout:
            Pyro4.config.TIMEOUT = timeout
        if polltimeout:
            Pyro4.config.POLLTIMEOUT = timeout
        self.daemon = Pyro4.Daemon(host=host,port=int(port))
        self.main_uri = self.daemon.register(self,'RemoteBagServer')
        print "uri=",self.main_uri
        self.daemon.requestLoop()

    def memberName(self):
        return 'REMOTEBAG'


#------------------------------- CLIENT SIDE ---------------------------

class RemoteBag(object):
    def __init__(self,uri=None,parent=None,rootpath=None):
        self.proxy=Pyro4.Proxy(uri) if uri else None
        self.parent=parent
        self.rootpath=rootpath

    def chunk(self,path):
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
    @wrapper 
    def __contains__(self,*args,**kwargs):
        return self.proxy.__contains__(*args,**kwargs)
    @wrapper 
    def __eq__(self,*args,**kwargs):
        return self.proxy.__eq__(*args,**kwargs)

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

class RemoteBagClientBase(object):
    def __init__(self,uri):
        self.proxy=Pyro4.Proxy(uri)

    def __getitem__(self,name):
        uri =  self.proxy.getUri(name)
        return self.factory(uri)

    def keys(self):
        return self.proxy.keys()

    def __len__(self):
        return self.proxy.__len__()

class RemoteBagClientRegister(RemoteBagClientBase):
    factory = RemoteBag

class RemoteBagClientSpace(RemoteBagClientBase):
    factory = RemoteBagClientRegister


class RemoteBagClient(RemoteBagClientBase):
    factory = RemoteBagClientSpace

    def __init__(self,uri=None,port=None,host=None,hmac_key=None):
        host = host or PYRO_HOST
        port = port or PYRO_PORT
        hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        Pyro4.config.HMAC_KEY = hmac_key
        Pyro4.config.SERIALIZER = 'pickle'
        uri = uri or 'PYRO:RemoteBagServer@%s:%i' %(host,port)
        self.proxy=Pyro4.Proxy(uri)

        
    def __call__(self,name):
        return self[name]
      
#------------------------------- TEST SIDE ---------------------------



def test_simple():
    client = RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    space = client['pippo']
    register = space['pluto']
    test_bag = register['test_simple']
    test_bag['foo'] = 23
    assert test_bag['foo']==23, 'broken'
    print len(test_bag)
    print test_bag
    print 'OK'



def test_chunk():
    client = RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    space = client['cip']
    register = space['ciop']
    dati = register['dati']
    dati['persone.p1.nome'] = 'Mario'
    dati['persone.p1.cognome'] = 'Rossi'
    dati['persone.p1.eta'] = 40

    dati['persone.p2.nome'] = 'Luigi'
    dati['persone.p2.cognome'] = 'Bianchi'
    dati['persone.p2.eta'] = 30
    print dati
    z=dati.getItem('persone')
    print z.asString()
    p1 = dati.chunk('persone.p1')
    print p1.asString()
   #print p1['nome']
   #p1['nome'] = 'Mariotto'
   #assert p1['nome'] == bag['dati.persone.p1.nome'], 'test fallito'
    print 'OK'
def test_client():
    client= RemoteBagClient(host=PYRO_HOST,port=PYRO_PORT)
    space = client['frillo']
    register = space['frullo']
    mybag = register['dati']
    
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
    test_chunk()