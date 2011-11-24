# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrstuctures : this implements the functional syntax to fill a Genro Bag
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

import weakref

from gnr.core.gnrbag import Bag, BagResolver
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrdict import GnrDict
from gnr.core import gnrstring
from gnr.core.gnrdecorator import deprecated

class GnrStructData(Bag):
    """This is a subclass of the :class:`Bag <gnr.core.gnrbag.Bag>` class that implements
    functional syntax for adding particular elements to the tree"""
    
    def makeRoot(cls, source=None, protocls=None):
        """Build the root instance for the given class and return it
        
        :param source: the filepath of the xml file
        :param protocls: the structure class"""
        if protocls:
            instance = protocls()
        else:
            instance = cls() #create an instance of cls
        if source: #load from xml file
            instance.load(source)
        instance.setBackRef()
        return instance
        
    makeRoot = classmethod(makeRoot)
        
    def backwardNodebyAttr(self, attrname, checker=None):
        """TODO
        
        :param attrname: TODO
        :param checker: TODO"""
        if checker is None:
            checker= lambda v:True
        if isinstance(checker,basestring):
            checker = lambda v:v==checker
        if self._parentNode:
            if attrname in self._parentNode.attr and checker(self._parentNode.attr[attrname])  :
                return self._parentNode
            return self._parent.backwardNodebyAttr(attrname)
        
    def _get_attaches(self):
        if self.parent == None:
            return self
        else:
            return self.parent
    
    @deprecated
    def _get_joiner(self):
        if self.parent == None:
            return self
        else:
            return self.parent
            
    _ = property(_get_joiner)
        
    def _get_root(self):
        if self.parent == None:
            return self
        else:
            return self.parent.root
            
    root = property(_get_root)
        
    def child(self, tag, childname='*_#', childcontent=None, content=None,_parentTag=None, _attributes=None,
              _returnStruct=True, _position=None, **kwargs):
        """Set a new item of the ``tag`` type into the current structure. Return the new structure
        if content is ``None``, else the parent
        
        :param tag: structure type
        :param name: structure name
        :param content: optional structure content
        :param _parentTag: TODO
        :param _attributes: TODO
        :param childname: the :ref:`childname`
        """
        where = self
        if childname and childname != '*_#':
            kwargs['_childname'] = childname
        if childcontent is None:
            childcontent = content
        if _attributes:
            kwargs.update(_attributes)
        if '_content' in kwargs:
            kwargs['content'] = kwargs.pop('_content')
        if not childname:
            childname = '*_#'
        if '.' in childname:
            namelist = childname.split('.')
            childname = namelist.pop()
            for label in namelist:
                if not label in where:
                    item = self.__class__()
                    where[label] = item
                where = where[label]
                
        childname = childname.replace('*', tag or 'notag').replace('#', str(len(where)))
        
        if childcontent is None and _returnStruct:
            childcontent = self.__class__()
            result = childcontent
        else:
            result = None
            
        if _parentTag:
            if isinstance(_parentTag, basestring):
                _parentTag = gnrstring.splitAndStrip(_parentTag, ',')
            actualParentTag = where.getAttr('', tag)
            if not actualParentTag in _parentTag:
                raise GnrStructureError('%s "%s" cannot be inserted in a %s' % (tag, childname, actualParentTag))
        if childname in where and where[childname] != '' and where[childname] is not None:
            if where.getAttr(childname, 'tag') != tag:
                raise GnrStructureError(
                        'Cannot change %s from %s to %s' % (childname, where.getAttr(childname, 'tag'), tag))
            else:
                kwargs = dict(
                        [(k, v) for k, v in kwargs.items() if v != None]) # default kwargs don't clear old attributes
                result = where[childname]
                result.attributes.update(**kwargs)
        else:
            where.setItem(childname, childcontent, tag=tag, _position=_position,_attributes=kwargs)
        return result
        
    def save(self, path):
        """Saves the structure as an XML file
        
        :param path: destination path of the saved file"""
        self.toXml(path, typeattrs=False)
        
    def load(self, path):
        """Loads the structure from an XML file
        
        :param path: path of the file to load"""
        cls = self.__class__
        b = Bag()
        b.fromXml(path, bagcls=cls, empty=cls)
        self[''] = self.merge(b)
        
class GnrStructObj(GnrObject):
    """It is a tree of :class:`GnrObjects <gnr.core.gnrlang.GnrObject>` classes that it is auto-builded starting from
    an instance of the :class:`GnrStructData` class"""
        
    def makeRoot(cls, parent, structnode, objclassdict, **kwargs):
        """Instantiate the root element
        
        :param cls: TODO
        :param parent: TODO
        :param structnode: TODO
        :param objclassdict: dictionary of the classes"""
        if isinstance(structnode, Bag):
            structnode = structnode.getNode('#0')
        tag = structnode.getAttr('tag').lower()
        if tag in objclassdict:
            return objclassdict[tag](structnode=structnode, parent=parent, objclassdict=objclassdict, **kwargs)
            
    makeRoot = classmethod(makeRoot)
            
    def __init__(self, tag=None, structnode=None, parent=None, name=None,
                 attrs=None, children=None, objclassdict=None, **kwargs):
        self.structnode = structnode
        if objclassdict:
            self.objclassdict = objclassdict
            self.rootparent = parent
            self.objdict = {}
            parent = None
        self.parent = parent
        self.children = GnrDict()
        self.childalias = {}
        self.name = name
        self.id = None
        if self.structnode:
            if not name:
                self.name = structnode.getLabel()
            self.attributes = dict(structnode.getAttr())
            children = structnode.getValue()
            self.id = structnode.getAttr('id')
            if self.id:
                self.id = self.id.replace('*', self.name)
                self.root.objdict[self.id] = self
        else:
            self.attributes = attrs or {}
            
        self.attributes.update(kwargs)
        buildChildren = self._captureChildren(children)
        self.init(**kwargs)
        if self.parent != None:
            self.parent.newChild(self)
        if children and buildChildren:
            self.buildChildren(children)
        self.afterChildrenCreation()
        
    def _captureChildren(self, children):
        return True
        
    def buildChildren(self, children):
        """TODO
        
        :param children: TODO"""
        objclassdict = self.root.objclassdict
        for child in children:
            tag = child.getAttr('tag')
            if tag == 'meta':
                self.metadata.setItem(child.label, child.value, _attributes=dict(child.attr))
            if tag:
                factory = objclassdict[tag.lower()]
                obj = factory(structnode=child, parent=self)
                self.children[obj.name.lower()] = obj
                if child.getAttr('alias'):
                    for alias in child.getAttr('alias').lower().split(','):
                        self.childalias[alias] = obj
            else:
                pass
                
    def _get_metadata(self):
        if not hasattr(self, '_metadata'):
            self._metadata = Bag()
        return self._metadata
        
    metadata = property(_get_metadata)
        
    def buildChild(self, childnode, **kwargs):
        """Build a child
        
        :param childnode: the child node"""
        objclassdict = self.root.objclassdict
        tag = childnode.getAttr('tag').lower()
        if tag in objclassdict:
            return objclassdict[tag](structnode=childnode, parent=self, **kwargs)

    def deleteChild(self, name):
        """Delete a child
        
        :param name: the child name"""
        child = self.children.pop(name)
        child.deleteChildren()
        child.onDelete()
        
    def onDelete(self):
        """Hook method on delete action"""
        pass
        
    def deleteChildren(self):
        """TODO"""
        for k in self.children.keys():
            self.deleteChild(k)
            
    def afterChildrenCreation(self):
        """Hook method after children creation"""
        pass
        
    def newChild(self, obj):
        """Hook method on creation of a new child
        
        :param obj: TODO"""
        pass
        
    def _get_root(self):
        if self.parent == None:
            return self
        else:
            return self.parent.root
            
    root = property(_get_root)
            
    def getById(self, id):
        """TODO
        
        :param id: the id of the object"""
        return self.root.objdict.get(id, None)
            
    def getItem(self, path, default=None, static=False):
        """Build a child
        
        :param path: TODO
        :param default: TODO
        :param static: TODO"""
        if path.startswith('.'):
            return self.root[path[1:]]
        if path.startswith('!'):
            return self.getById(path[1:])
        obj, label = self._htraverse(path)
        if hasattr(obj, 'get'):
            if static:
                return obj.getResolver(label, default=default)
            return obj.get(label, default)
        else:
            return default
            
    __getitem__ = getItem
        
    def get(self, name, default=None):
        """Build a child
        
        :param name: TODO
        :param default: TODO"""
        name = name.lower()
        if name in self.children:
            obj = self.children[name]
        elif name in self.childalias:
            obj = self.childalias[name]
        else:
            obj = default
            
        if isinstance(obj, BagResolver):
            return obj()
        else:
            return obj
            
    def getResolver(self, name, default=None):
        """Build a child
        
        :param name: TODO
        :param default: TODO"""
        return self.children.get(name.lower(), default=default)
        
    def _htraverse(self, pathlist, **kwargs):
        curr = self
        if isinstance(pathlist, basestring):
            pathlist = gnrstring.smartsplit(pathlist.replace('../', '#^.'), '.')
            pathlist = [x for x in pathlist if x]
            if not pathlist:
                return curr, ''
        label = pathlist.pop(0)
        while label == '#^' and pathlist:
            curr = curr.parent
            label = pathlist.pop(0)
        if not pathlist:
            return curr, label
            
        newcurr = curr.get(label)
        isbag = hasattr(newcurr, '_htraverse')
        if isbag:
            return newcurr._htraverse(pathlist)
        else:
            return newcurr, '.'.join(pathlist)
            
    def __len__(self):
        return len(self.children)
        
    def __iter__(self):
        return self.children.__iter__()
        
    def __contains__(self, name):
        return (name.lower() in self.children) or (name.lower() in self.childalias)
        
    def items(self):
        """Same of ``items`` method's dict, applied on the ``children`` attribute"""
        return self.children.items()
        
    def keys(self):
        """Same of ``keys`` method's dict, applied on the ``children`` attribute"""
        return self.children.keys()
        
    def values(self):
        """Same of ``values`` method's dict, applied on the ``children`` attribute"""
        return self.children.values()
        
    def _set_structnode(self, structnode):
        if structnode != None:
            #self.__structnode=weakref.ref(structnode)
            self.__structnode = structnode
        else:
            self.__structnode = None
            
    def _get_structnode(self):
        if self.__structnode:
            return self.__structnode
            #return self.__structnode()
            
    structnode = property(_get_structnode, _set_structnode)
        
    def _set_parent(self, parent):
        if parent != None:
            #self._parent=weakref.ref(parent)
            self._parent = parent
        else:
            self._parent = None
            
    def _get_parent(self):
        if hasattr(self, '_parent'):
            return self._parent
            
    parent = property(_get_parent, _set_parent)
        
    def init(self):
        """TODO"""
        pass
        
    def newChild(self, child):
        """TODO
        
        :param child: TODO"""
        pass
        
    def afterChildrenCreation(self):
        """TODO"""
        pass
        
    def asBag(self):
        """TODO"""
        return StructObjResolver(self)
        
class StructObjResolver(BagResolver):
    def resolverDescription(self):
        """TODO"""
        return 'tree'
        
    def init(self, obj):
        """TODO
        
        :param obj: TODO"""
        #self.obj = weakref.ref(obj)
        self.obj = obj
        self.alreadyCalled = False
        
    def expired(self):
        """TODO"""
        if self.alreadyCalled:
            #obj = self.obj()
            obj = self.obj
            if isinstance(obj, BagResolver):
                return obj.expired()
            else:
                return False
        else:
            return True
            
    def __call__(self):
        self.alreadyCalled = True
        result = Bag()
        #result.clear()
        result.obj = self.obj
        #obj = self.obj()
        obj = self.obj
        if isinstance(obj, BagResolver):
            obj = obj()
            
        for name, x in obj.items():
            if isinstance(x, GnrStructObj):
                tag = x.getTag()
                attr = {'tag': tag}
                attr.update(x.attributes)
                result.setItem(name, StructObjResolver(x), _attributes=attr)
            elif isinstance(x, Bag) or isinstance(x,
                                                  BagResolver):# attributes are lost, we should take from parent node, but it can be a structobj...
                result.setItem(name, StructObjResolver(x), tag=x.getTag())
            else:
                result.setItem(name, x, tag=x.getTag())
        return result
        
class TestStructModule(object):
    """TODO"""
    def __init__(self):
        self.struct = GnrStructData.root()
        self.structdict = {}
        self.roots = {}
        
    def buildOne(self, name, path):
        """TODO
        
        :param name: TODO
        :param path: TODO"""
        node = self.struct.getNode(path)
        self.roots[name] = GnrStructObj.root(node, self.structdict)
        
class GnrStructureError(Exception):
    pass
        
if __name__ == '__main__':
    pass