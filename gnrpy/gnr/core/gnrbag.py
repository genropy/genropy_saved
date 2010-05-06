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

"""
The gnrbag module contains a single class intended to be used: Bag
A Bag is a generic container object, similar to a dictionary,
with some useful properties:
   
- ordered
- accessible by key
- iterable
- hierarchical    
    
A Bag can store any kind of python object with a label in an ordered list.
It can also store attributes about any value stored: bag attributes are metadata
that are an addition to the stored object without distrurbing the stored data

A Bag can be loaded and saved in some ways:
- saved to and loaded from pikle files or strings: 
the object stored in the bag must be picklable of course.
- saved to and loaded from xml files or strings with a specific syntax: 
the object stored in the bag must be strings, numbers or dates.
- loaded from a generic xml file preserving the whole hierarchical structure and 
the attributes: all values will be of type string of course.
- loaded from a generic html file: requires tidy.
    
Another class you could have to deal with is BagNode: they are Bag elements, 
basically a Bag is a list of BagNode-s.

BagNode is not intended to be instanced directly, it is used internally by Bag.
However in some cases is useful to interact with BagNode instances inside a Bag.
"""
#import weakref
import copy
import cPickle as pickle
from datetime import datetime, timedelta
import urllib,urlparse
from gnr.core import gnrstring
from gnr.core.gnrclasses import GnrClassCatalog as converter
from gnr.core.gnrlang import setCallable, GnrObject
import os.path
import logging
import time
gnrlogger = logging.getLogger('gnr.core.gnrbag')

def timer_call(time_list=[],print_time=True):
    def decore(func):
        def wrapper(*arg,**kw):
            t1 = time.time()
            res = func(*arg,**kw)
            t2 = time.time()
            if print_time:
                print '-'*80
                print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
                print 10*' '+28*'-'+'args'+28*'-'+10*' '
                print arg
                print 10*' '+27*'-'+'kwargs'+27*'-'+10*' '
                print kw or (hasattr(arg[0],'kwargs') and arg[0].kwargs)
                print '-'*80
            time_list.append((func.func_name, (t2-t1)*1000.0))
            return res
        return wrapper
    return decore

class BagNodeException(Exception):
    pass
class BagException(Exception): 
    pass
    
class BagAsXml(object): 
    def __init__(self,value):
        self.value=value
        
class BagValidationError(BagException):
    pass
   # def __init__(self, errcode, value, message):
       # self.errcode=errcode
        #self.value = str(value)
        #self.message = message
        
        
class BagDeprecatedCall(BagException):

    def __init__(self, errcode, message):
        self.errcode=errcode
        self.message = message


class BagNode(object):
    """
    BagNode is the element type which a Bag is composed of. That's why it's
    possible to say that a Bag is a collection of BagNodes. A BagNode is an 
    object that gather within itself, three main things:
    
        -label: can be only a string.
        -value: can be anything, but a BagNode. Often value is a Bag.
        -attributes: dictionary that contains node's metadata   
        
    """
    def __init__(self, parentbag, label, value=None, attr=None, resolver=None,
                validators=None,_removeNullAttributes=True):
        """
        * `parentbag`: Bag than contains the node
        * `label`: label that identifies the node
        * `value`: value of the node
        * `attr`: node's attributes
        * `resolver`: a BagResolver
        * `validators`: a dict with all validators pairs
        """
        self.label = label
        self.locked = False
        self._value = None
        self.resolver = resolver
        self.parentbag=parentbag
        self._node_subscribers={}
        self._validators = None
        self.attr = {}
        if attr:
            self.setAttr(attr, trigger = False,
                        _removeNullAttributes = _removeNullAttributes)
        if validators:
            self.setValidators(validators)
        self.setValue(value, trigger=False)
        
    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and (self.attr == other.attr):
                if self._resolver == None:
                    return self._value == other._value
                else:
                    return self._resolver == other._resolver
            else:
                return False
        except:
            return False
        
    def setValidators(self, validators):
        for k,v in validators.items():
            self.addValidator(k,v)
            
    def _get_parentbag(self):
        if self._parentbag:
            return self._parentbag
            #return self._parentbag()
        
    def _set_parentbag(self,parentbag):
        self._parentbag=None
        if parentbag != None:
            if parentbag.backref or True:
                #self._parentbag=weakref.ref(parentbag)
                self._parentbag=parentbag
                if isinstance(self._value, Bag) and parentbag.backref:
                    self._value.setBackRef(node=self, parent=parentbag)
    parentbag = property(_get_parentbag,_set_parentbag)
    
    def _get_fullpath(self):
        if not self.parentbag is None:
            fullpath=self.parentbag.fullpath
            if not fullpath is None:
                return '%s.%s' % (fullpath,self.label)
    fullpath = property(_get_fullpath)
    
    def getLabel(self):
        """
        Returns node's label
        """
        return self.label

    def setLabel(self, label):
        """
        set node's label
        """
        self.label = label
    
    def getValue(self, mode=''):
        """
        Returns the value of the BagNode.
        This method is called by the property .value
        
        * `mode`: can be one or more of:
                    - static: to get the resolver instance instead of the 
                              calculated value
                    - weak: to get a weak ref stored in the node instead of 
                            the actual object
                    
        Return: node's value
        """
        if not self._resolver == None:
            if 'static' in mode:
                return self._value
            else:
                if self._resolver.readOnly:
                    return self._resolver() # value is not saved in bag, eventually is cached by resolver or lost
                if self._resolver.expired: # check to avoid triggers if value unchanged
                    self.value = self._resolver() # this may be a deferred
                return self._value
        #if isinstance(self._value, weakref.ref) and not 'weak' in mode:
        #    return self._value()
        return self._value
    
    def setValue(self, value, trigger=True, _attributes = None,
                _updattr = None,_removeNullAttributes = True):
        """
        Set the node's value, unless the node is locked.
        This method is called by the property .value
        
        * `value`: the value to set the new bag inherits the trigger of the
                   parentbag and calls it sending an update event
        """
        if self.locked:
            raise BagNodeException("Locked node %s" % self.label)
        if isinstance(value, BagNode):
            _attributes= _attributes or {}
            _attributes.update(value.attr)
            value=value._value
        if isinstance(value,Bag):
            rootattributes = value.rootattributes
            if rootattributes:
                _attributes = dict(_attributes or {})
                _attributes.update(rootattributes)
        oldvalue=self._value
        if self._validators:
            self._value = self._validators(value, oldvalue)
        else:
            self._value = value
        trigger = trigger and (oldvalue!=self._value) # we have to check also attributes change
        evt='upd_value'
        if _attributes != None:
            evt='upd_value_attr'
            self.setAttr(_attributes, trigger = False, _updattr = _updattr,
                        _removeNullAttributes=_removeNullAttributes)
        if trigger:
            for subscriber in self._node_subscribers.values():
                subscriber (node=self, info=oldvalue, evt='upd_value')
        if self.parentbag!=None and self.parentbag.backref:
            if isinstance(value,Bag):
                value.setBackRef(node=self,parent=self.parentbag)
            if trigger:
                self.parentbag._onNodeChanged(self, [self.label], 
                                              oldvalue=oldvalue, evt=evt)

    value = property(getValue,setValue)

    def getStaticValue(self):
        """
        Get node's value in static mode
        """
        return self.getValue('static')
    
    def setStaticValue(self, value):
        """
        Set node's value in static mode
        """
        self._value = value
    staticvalue = property(getStaticValue,setStaticValue)
      
    def _set_resolver(self, resolver):
        """
        Set a resolver in the node
        """
        if not resolver is None:
            resolver.parentNode = self
        self._resolver = resolver
        
    def _get_resolver(self):
        """
        Get node's resolver
        """
        return self._resolver
    resolver = property(_get_resolver, _set_resolver)
    
    def resetResolver(self):
        self._resolver.reset()
        self.setValue(None)
    
    def getAttr(self, label=None, default=None):
        """
        this method returns the value of an attribute given it's label.
        If it doesn't exists returns a default value.
        * `label`: the label of the attribute to get.
        """
        if not label or label=='#': 
            return self.attr
        return self.attr.get(label,default)
        
    
    def getInheritedAttributes(self):
        inherited = {}
        if self.parentbag:
            if self.parentbag.parentNode:
                inherited = self.parentbag.parentNode.getInheritedAttributes()
        inherited.update(self.attr)
        return inherited
    
    def hasAttr(self, label=None, value=None):
        """
        this method check if the node has the given pair label-value
        in its attributes
        """
        if not label in self.attr: return False
        if value: return (self.attr[label] == value)
        return True
        
    def setAttr(self, attr = None, trigger = True, _updattr = True, 
                _removeNullAttributes = True,**kwargs):
        """this method receives one or more key-value couple, passed as a dict or
        as named parameters, and sets them as attributes of the node
        
        * `attr`: the dict of attributes to set into the node.
        
        """
        if not _updattr:
            self.attr.clear()
        #if self.locked:
            #raise BagNodeException("Locked node %s" % self.label)        
        if self._node_subscribers and trigger:
            oldattr=dict(self.attr)
        if attr:
            self.attr.update(attr)
        if kwargs:
            self.attr.update(kwargs)
        if _removeNullAttributes:
            [self.attr.__delitem__(k) for k,v in self.attr.items() if v == None] 
        
        if trigger:
            if self._node_subscribers:
                upd_attrs=[k for k in self.attr.keys() if (k not in oldattr.keys() or self.attr[k]!=oldattr[k])]
                for subscriber in self._node_subscribers.values():
                    subscriber(node=self, info=upd_attrs, evt='upd_attrs')
            if self.parentbag!=None and self.parentbag.backref :
                self.parentbag._onNodeChanged(self, [self.label], evt='upd_attrs')

        
    def delAttr(self, *attrToDelete):
        """this method receives one or more attributes' labels and removes them
        from the node's attributes
        """
        if isinstance(attrToDelete,basestring):
            attrToDelete=attrToDelete.split(',')
        for attr in attrToDelete:
            if attr in self.attr.keys():
                self.attr.pop(attr)
            
    def __str__(self):
        return 'BagNode : %s' % self.label
    
    def __repr__(self):
        return 'BagNode : %s at %i' % (self.label, id(self))
    
    def asTuple(self):
        return (self.label, self.value, self.attr, self.resolver)
    
    def addValidator(self, validator, parameterString):
        """
        this method set a new validator into the BagValidationList of the node.
        If there are no validators into the node then addValidator instantiate
        a new BagValidationList and append the validator to it.
        * `validator`: the type of validation to set into the list of the node.
        * `paremeterString`: the parameters for a single validation type.
        """
        if self._validators is None:
            self._validators = BagValidationList(self)
        self._validators.add(validator, parameterString)
        
    def removeValidator(self, validator):
        if not self._validators is None:
            self._validators.remove(validator)
            
    def getValidatorData(self,validator,label=None,dflt=None):
        if not self._validators is None:
            return self._validators.getdata(validator,label=label,dflt=dflt)
        
    def subscribe(self, subscriberId,callback):
        self._node_subscribers[subscriberId] = callback
        
    def unsubscribe(self, subscriberId):
        self._node_subscribers.pop(subscriberId)
        
            
#-------------------- Class Bag --------------------------------
class Bag(GnrObject):
    """
    A container object like a dictionary, but ordered.
    Nested elements can be accessed with a path of keys joined with dots.
    """
    
    #-------------------- __init__ --------------------------------
    def __init__(self, source=None):
        """ 
        A new bag can be created in various ways:
            - parsing a local file, a remote url or a text string (see fromXml)
            - converting a dictionary into a Bag 
            - passing a list or a tuple just like for the builtin dict() command
        """
        GnrObject.__init__(self)
        self._nodes = []
        self._backref = False
        self._node = None
        self._parent = None
        self._symbols = None
        self._upd_subscribers={}
        self._ins_subscribers={}
        self._del_subscribers={}
        self._modified=None
        self._rootattributes=None
        if source:
            self.fillFrom(source)
        
    def _get_parent(self):
        if self._parent:
            return self._parent
            #return self._parent()
        
    def _set_parent(self,parent):
        if parent is None:
            self._parent=None
        else:
            #self._parent=weakref.ref(parent)
            self._parent=parent
    parent = property(_get_parent,_set_parent)
    
    def _get_fullpath(self):
        if self.parent != None:
            parentFullPath = self.parent.fullpath
            if parentFullPath:
                return '%s.%s' % (self.parent.fullpath, self.parentNode.label)
            else:
                return self.parentNode.label
    fullpath = property(_get_fullpath)
    
    def _set_node(self, node):
        raise BagDeprecatedCall('Deprecated syntax','use .parentNode instead of .node')
        if node != None:
            self._parentNode = node
            #self._parentNode = weakref.ref(node)
        else:
            self._parentNode = None
        
            
    def _get_node(self):
        raise BagDeprecatedCall('Deprecated syntax','use .parentNode instead of .node')
        if self._parentNode != None:
            return self._parentNode
            #return self._parentNode()
    node = property(_get_node, _set_node)
    
    def _set_parentNode(self, node):
        if node != None:
            self._parentNode = node
            #self._parentNode = weakref.ref(node)
        else:
            self._parentNode = None
    def _get_parentNode(self):
        if self._parentNode != None:
            return self._parentNode
            #return self._parentNode()
    parentNode = property(_get_parentNode, _set_parentNode)
    
    def _get_attributes(self):
        return self.parentNode.getAttr()
    attributes= property(_get_attributes)

    def _get_rootattributes(self):
        return self._rootattributes
    def _set_rootattributes(self, attrs):
        self._rootattributes = dict(attrs)
    rootattributes = property(_get_rootattributes, _set_rootattributes)
    
    def _get_modified(self):
        return self._modified
    
    def _set_modified(self, value):
        if value==None:
            self._modified=None
            self.unsubscribe('modify__', any=True)
        else:
            if self._modified==None:
                self.subscribe('modify__', any=self._setModified)
            self._modified=value
    modified=property(_get_modified, _set_modified)
    
    def _setModified(self,**kwargs):
        self._modified=True
        
#-------------------- __contains__ --------------------------------
    def __contains__(self, what):
        """
        The "in" operator can be used to test the existence of a key in a
        bag. Also nested keys are allowed.
        * `what`: the key path to test.
        @return: a boolean value, True if the key exists in the bag, False otherwise.
        
        """
        if isinstance(what, basestring):
            return bool(self.getNode(what))
        elif isinstance(what, BagNode):
            return (what in self._nodes)
        else:
            return False
        
    #-------------------- getItem --------------------------------        
    def getItem(self, path, default=None, mode=None):
        """
        This method reimplements the list's __getitem__().
        Usually a path is a string formed by the labels of the nested items, joined by the char '.'
        but several different path notations have been implemented to offer some useful features.
        If a path segment starts with '#' is followed by a number, it means that for that level, the item
        will by identified by its index position, as a list element.
        If a path ends with '.?', function returns the item's keys.
        If at the last path-level the label contains '#', what follows the '#' is considered the key
        of an item's attribute and the function will return that attribute's value.
        If a path starts with '?' the path is interpreted as a digest.
        A path can also ba a list of keys.
        
        * `path`: the item's path
        * `default`: an optional default value, default is 'None'. 
        
        Return: the value of the given item        
        
        >>> mybag=Bag()
        >>> mybag['aa.bb.cc']=1234
        >>> mybag['aa.bb.cc']
        1234
        """
        if not path:
            return self
        if isinstance(path, basestring):
            if '?' in path:
                path, mode = path.split('?')
                if mode=='': mode='k'
        obj, label = self._htraverse(path)
        if isinstance(obj,Bag):
            return obj.get(label, default, mode=mode)
        if hasattr(obj,'get'):
            value = obj.get(label, default)
            return value
        else:
            return default
    __getitem__ = getItem
    
    
    def sort(self, pars='#k:a'):
        """
        pars None: label ascending
        pars ''
        """
        if not isinstance(pars, basestring):
            self._nodes.sort(pars)
        else:
            levels = pars.split(',')
            levels.reverse()
            for level in levels:
                if ':' in level:
                    what, mode = level.split(':')
                else:
                    what = level
                    mode = 'a'
                what = what.strip().lower()
                reverse = (not (mode.strip().lower() in ('a', 'asc', '>')))
                if what=='#k':
                    self._nodes.sort(lambda a, b: cmp(a.label.lower(), b.label.lower()), reverse=reverse)
                elif what=='#v':
                    self._nodes.sort(lambda a, b: cmp(a.value, b.value), reverse=reverse)
                elif what.startswith('#a'):
                    attrname = what[3:]
                    self._nodes.sort(lambda a, b: cmp(a.getAttr(attrname), b.getAttr(attrname)), reverse=reverse)
                else:
                    self._nodes.sort(lambda a, b: cmp(a.value[what], b.value[what]), reverse=reverse)
                
    def sum(self, what='#v'):
        if ',' in what:
            result=[]
            wlist=what.split(',')
            for w in wlist:
                result.append(sum(map(lambda n : n or 0,self.digest(w))))
            return result
        else:
            return sum(map(lambda n : n or 0,self.digest(what)))

    
    def get(self, label, default=None, mode=None):
        result = None
        currnode = None
        currvalue = None
        attrname=None
        if not label: 
            currnode = self.parentNode
            currvalue = self
        elif label=='#^':
            currnode = self.parent.parentNode
        else:
            if '?' in label:
                label,attrname=label.split('?')
            i = self._index(label)
            if i<0:
                return default
            else:
                currnode = self._nodes[i]
        if currnode: 
            if attrname:
                currvalue=currnode.getAttr(attrname)
            else:
                currvalue = currnode.getValue()
        if not mode:
            result = currvalue
        else:
            cmd = mode.lower()
            if not ':' in cmd:
                result = currnode.getAttr(mode)
            else:
                if cmd=='k:': 
                    result = currvalue.keys()
                elif cmd.startswith('d:') or cmd.startswith('digest:'):
                    result = currvalue.digest(mode.split(':')[1])
        return result 
    
    
    def _htraverse(self,  pathlist, autocreate=False, returnLastMatch=False):
        """
        this method receives a list that represents a hierarchical path and executes
        one step of the path, calling itself recursively. If autocreate mode is True,
        the method creates not existing nodes of the pathlist.
        * `pathlist`: list of nodes'labels
        @return: current node's value
        """
        curr = self
        if isinstance(pathlist,basestring):
            pathlist = gnrstring.smartsplit(pathlist.replace('../','#^.'),'.')
            pathlist = [x for x in pathlist if x]
            if not pathlist:
                return curr, ''
        label = pathlist.pop(0)
        while label=='#^' and pathlist:
            curr = curr.parent
            label = pathlist.pop(0)
        if not pathlist:
            return curr, label
        i = curr._index(label)
        if i<0:
            if autocreate:
                if label.startswith('#'):
                    raise BagException ('Not existing index in #n syntax')
                i = len(curr._nodes)
                newnode=BagNode(curr,label=label,value=curr.__class__())
                curr._nodes.append(newnode)
                if self.backref:
                    self._onNodeInserted(newnode,i)
            elif returnLastMatch:
                return self.parentNode, '.'.join([label]+pathlist)
            else:
                return None, None
        newcurrnode=curr._nodes[i]
        newcurr = newcurrnode.value #maybe a deferred
        # if deferred : 
            #return deferred.addcallback(this.getItem(path rimanente))
        isbag = hasattr(newcurr, '_htraverse')
        if autocreate and not isbag:
            newcurr = curr.__class__()
            self._nodes[i].value=newcurr
            #curr.__setValue(i,newcurr)
            isbag = True
        if isbag:
            return newcurr._htraverse(pathlist, autocreate=autocreate, returnLastMatch=returnLastMatch)
        else:
            if returnLastMatch:
                return newcurrnode,'.'.join(pathlist)
            return newcurr, '.'.join(pathlist)
    
    def __iter__(self):
        return self._nodes.__iter__()
    
    def __len__(self):
        return len(self._nodes)
    
    def __call__(self, what=None): #deprecated
        if not what :
            return self.keys()
        return self[what]
    
    #-------------------- __str__ --------------------------------
    def __str__(self, exploredNodes=None, mode='static,weak'):
        """
        This method returns a formatted representation of the bag contents.
        @return: a formatted representation of the bag contents (unicode)
        
        """
        if not exploredNodes:
            exploredNodes={}
        outlist=[]
        for idx,el in enumerate(self._nodes):
            attr='<'+' '.join(["%s='%s'" % attr for attr in el.attr.items()])+'>'
            if attr=='<>':attr=''
            try:
                value = el.getValue(mode)
            except:
                value ='****  error ****'
            if isinstance(value, Bag):
                el_id=id(el)
                outlist.append(("%s - (%s) %s: %s" % 
                                   (str(idx), value.__class__.__name__, el.label,attr)))
                if el_id in exploredNodes:
                    innerBagStr='visited at :%s' % exploredNodes[el_id]
                else:
                    exploredNodes[el_id]=el.label
                    innerBagStr='\n'.join(["    %s"%(line,)
                                for line in unicode(
                                value.__str__(exploredNodes, mode=mode)).split('\n')])
                outlist.append(innerBagStr)
            else:
                currtype=str(type(value)).split(" ")[1][1:][:-2]
                if currtype=='NoneType' : currtype='None'
                if '.' in currtype: currtype = currtype.split('.')[-1]
                if not isinstance(value,unicode):
                    if isinstance(value,basestring): 
                        value= value.decode('UTF-8','ignore')
                outlist.append(("%s - (%s) %s: %s  %s" % (str(idx), currtype,
                                el.label,unicode(value),attr)))
        return '\n'.join(outlist) 
        
    def asString(self, encoding='UTF-8', mode='weak'):
        """
        This method calls the __str__ method: 
        asString() returns an ascii encoded formatted representation of the bag.
        * `encoding`: default is 'UTF-8'
        @return: a formatted representation of the bag contents (ascii)
        
        """
        return self.__str__(mode=mode).encode(encoding,'ignore')
    
    def keys(self):
        """       
        This method returns a list containing all the keys of the Bag. 
        @return: a list containing all the keys of the Bag.        
        """
        return [x.label for x in self._nodes]
    
    def values(self):
        """
        This method returns a list containing all values of the Bag. 
        @return: a list containing all the values of the Bag.        
        """
        return [x.value for x in self._nodes]
        
    def items(self):
        """
        This method returns a list of tuples containing all key,value pairs.
        @return: a list of tuples containing all key,value pairs of the Bag.        
        """
        return [(x.label ,x.value) for x in self._nodes]
    
    def iteritems(self):
        for x in self._nodes:
            yield (x.label,x.value)
            
    def iterkeys(self):
        for x in self._nodes:
            yield x.label

    def itervalues(self):
        for x in self._nodes:
            yield x.value
            
    def digest(self, what=None, condition=None, asColumns=False):
        """
        Extracts multiple values from a Bag. It can be used with special keys
        that are applied to all the nodes. Then digest() returns a list as
        long as the Bag containing the requested values.
         
        * `what`: this param is a comma separated string of special keys.
                  Special keys are:
                  
                      - #k: the label of each node
                      - #v: the value of each node
                      - #__v: the value of each node in 'static' mode
                      - #a: the attributes of each node
                      - #a.attrname: the attribute 'attrname' of each node
                      - subpath: the value of this subpath of each node
                                 this parameter can start with a path before the list of
                                 special keys to apply the digest to a subpath of this
                                 Bag. Path and special keys are separated by ':'.
        * `condition`: set a condition for digest process
         
        """
        
        if not what:
            what = '#k,#v,#a'
        if isinstance(what,basestring):
            if ':' in what:
                where, what = what.split(':')
                obj=self[where]
            else:
                obj=self
            whatsplit=[x.strip() for x in what.split(',')]
        else:
            whatsplit = what
            obj=self
        result=[]
        nodes=obj.getNodes(condition)
        for w in whatsplit:
            if w=='#k':
                result.append([x.label for x in nodes])
            elif callable(w):
                result.append([w(x) for x in nodes])
            elif w=='#v':
                result.append([x.value for x in nodes])
            elif w.startswith('#v.'):
                w,path=w.split('.',1)
                result.append([x.value[path] for x in nodes if hasattr(x.value, 'getItem')])
            elif w=='#__v':
                result.append([x.staticvalue for x in nodes])
            elif w.startswith('#a'):
                attr=None
                if '.' in w:
                    w,attr=w.split('.',1)
                if w=='#a':
                    result.append([x.getAttr(attr) for x in nodes])
            else:
                result.append([x.value[w] for x in nodes])
        if asColumns:
            return result
        if len(result)==1:
            return result.pop()
        return zip(*result)
    
    def columns(self, cols, attrMode=False):
        if isinstance(cols, basestring):
            cols = cols.split(',')
        mode = ''
        if attrMode:
            mode = '#a.'
        what = ','.join(['%s%s' % (mode, col) for col in cols])
        return self.digest(what, asColumns=True)
        
    def has_key(self, path):
        """ 
        This method is analog to dictionary's has_key() method.
        * `path`: path of the given item.
        @return: a boolean value: True if the given item has a key, False otherwise.
        
        """
        return bool(self.getNode(path))
    
    def getNodes(self,condition=None):
        """Get the actual list of nodes contained in the Bag"""
        if not condition:
            return self._nodes
        else :
            return [n for n in self._nodes if condition (n)]
    nodes = property(getNodes)
    
    def popNode(self, path):
        obj, label = self._htraverse(path)
        if obj: 
            n = obj._pop(label)
            if n:
                return n
            
    def pop(self, path,dflt=None):
        """ 
        This method is analog to dictionary's pop() method. It pops the given item
        from the Bag; it returns the given item.
        * `path`: path of the given item.
        @return: the given item.
        """
        result = dflt
        obj, label = self._htraverse(path)
        if obj: 
            n = obj._pop(label)
            if n:
                result = n.value
        return result
        
    delItem = pop
    __delitem__=pop
    
    def _pop(self, label):
        p = self._index(label)
        if p >= 0:
            node = self._nodes.pop(p)
            if self.backref:
                self._onNodeDeleted(node, p)
            return node

#-------------------- clear --------------------------------  
    def clear(self):
        """        
        This method clears the Bag.
        """
        oldnodes=self._nodes
        self._nodes = []
        if self.backref:
            self._onNodeDeleted(oldnodes,-1)
            

    def update(self, otherbag):
        """
        this method merge a Bag into the current one.
        * `otherbag`: a Bag to merge into.
        """
        if isinstance(otherbag,dict):
            for k,v in otherbag.items():
                self.setItem(k,v)
            return
        if isinstance(otherbag, basestring):
            cls=self.__class__
            b = Bag()
            b.fromXml(otherbag, bagcls=cls, empty=cls)
            otherbag=b
        for n in otherbag:
            if n.label in self.keys():
                currNode=self.getNode(n.label)
                currNode.attr.update(n.attr)
                if n.resolver:
                    currNode.resolver=n.resolver
                    currNode.value=None
                else:
                    currNode.resolver=None
                    if isinstance(n.value, Bag):
                        if isinstance(currNode.value,Bag):
                            currNode.value.update(n.value)
                        else:
                            currNode.value=n.value
                    else:
                        currNode.value=n.value
            else:
                self.setItem(n.label, n.resolver or n.value, n.attr)
                
    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__):
                return self._nodes == other._nodes
            else:
                return False
        except:
            return False
        
    def merge(self, otherbag, upd_values=True, add_values=True, upd_attr=True, add_attr=True):
        """
        Create a new Bag by the merging of this Bag and another one.
        @param: otherbag: the Bag used for the merge.
        """
        result = Bag()
        othernodes = dict([(n.getLabel(), n) for n in otherbag._nodes])
        for node in self.nodes:
            k = node.getLabel()
            v = node.getValue()
            attr = dict(node.getAttr())
            if k in othernodes:
                onode = othernodes.pop(k)
                oattr = onode.getAttr() 
                if upd_attr and add_attr:
                    attr.update(oattr)
                elif upd_attr:
                    attr = dict([(ak, oattr.get(ak, av)) for ak,av in attr.items()])
                elif add_attr:
                    oattr = dict([(ak, av) for ak,av in oattr.items() if not ak in attr.keys()])
                    attr.update(oattr)
                ov = onode.getValue()
                if isinstance(v,Bag) and isinstance(ov, Bag):
                    v = v.merge(ov, upd_values=upd_values, add_values=add_values, upd_attr=upd_attr, add_attr=add_attr)
                elif upd_values:
                    v = ov
            result.setItem(k, v, _attributes=attr)
        if add_values:
            for k,n in othernodes.items():
                result.setItem(k, n.getValue(), _attributes=n.getAttr())
        return result
    
#-------------------- copy --------------------------------  
    def copy(self):
        """
        This method returns a copy of the Bag.
        @return: a copy of the Bag.
        
        """
        return copy.copy(self)
    
#-------------------- deepcopy ------------------------------- 
    
    def deepcopy(self):
        """
        This method returns a deep copy of the Bag.
        @return: a deep copy of the Bag.
        """
        result = Bag()
        for node in self:
            value = node.getStaticValue()
            if isinstance(value, Bag):
                value = value.deepcopy()
            result.setItem(node.label, value, dict(node.getAttr()))
        return result
    
#-------------------- getNodeByAttr --------------------------------        
    def getNodeByAttr(self, attr, value, path=None):
        """
        This method returns the first found node which has an attribute named 'attr'
        equal to 'value'. E.g. searching a node with a given 'id' in a Bag build from html.
        
        * `attr`: path of the given item. 
        * `value`: path of the given item. 
        * `path`: optional, an empty list that will be filled with the path of the found node. 
        
        Return: a BagNode with the requested attribute
        """
        bags=[]
        if path == None: path = []
        for node in self._nodes:
            if node.hasAttr(attr, value):
                path.append(node.label)
                return node
            if isinstance(node.value, Bag): bags.append(node)
            
        for node in bags:
            nl = [node.label]
            n = node.value.getNodeByAttr(attr,value,path=nl)
            if n :
                path.extend(nl)
                return n
    
    def getDeepestNode(self,path=None):
        """
        This method returns the deepest matching node in the bag and the remaining path of the path
        eg: bag.getDeepestNode('foo.bar.baz') returns 
        if 'foo.bar.baz' in bag:
            return (bag.getNode(foo.bar.baz), [])
        elif 'foo.bar' in bag:
            return (bag.getNode('foo.bar'), ['baz'])
        elif 'bar' in bag:
            return (bag.getNode(foo),['bar','baz'])
        else:
            return (None,['foo','bar','baz'])
        """
        node, tail_path = self._htraverse(path,returnLastMatch=True)
        if hasattr(node,'_htraverse'):
            node = node.getNode(tail_path)
            tail_path = ''
        if node:
            node._tail_list = []
            if tail_path:
                node._tail_list = tail_path.split('.')
            return node
        #return None
        
    def getDeepestNode_(self,path=None):
        """
        This method returns the deepest matching node in the bag and the remaining path of the path
        eg: bag.getDeepestNode('foo.bar.baz') returns 
        if 'foo.bar.baz' in bag:
            return (bag.getNode(foo.bar.baz), [])
        elif 'foo.bar' in bag:
            return (bag.getNode('foo.bar'), ['baz'])
        elif 'bar' in bag:
            return (bag.getNode(foo),['bar','baz'])
        else:
            return (None,['foo','bar','baz'])
        """
        result = self._htraverse(path,returnLastMatch=True)
        if hasattr(result[0],'_htraverse'):
            return result[0].getNode(result[1]), ''
        return result
#-------------------- getNode --------------------------------        
    def getNode(self, path=None, asTuple=False, autocreate=False, default=None):
        """
        This method returns the BagNode stored at this path.
        * `path`: path of the given item. 
        """
        if not path:
            return self.parentNode
        if isinstance(path,int):
            return self._nodes[path]
        obj, label = self._htraverse(path,autocreate=autocreate)

        if isinstance(obj,Bag):
            node=obj._getNode(label,autocreate,default)
            if asTuple:
                return (obj,node)
            return node

    def _getNode(self, label, autocreate,default):
        p = self._index(label)
        if p >= 0:
            node = self._nodes[p]
        elif autocreate:
            node = BagNode(self,label=label,value=default)
            i = len(self._nodes)
            self._nodes.append(node)
            node.parentbag=self
            if self.backref:
                self._onNodeInserted(node,i)

        else:
            node = None
        return node
        
        
    def setAttr(self, _path=None, _attributes=None, _removeNullAttributes=True,**kwargs):
        """
        This method set attributes into the node at the given path
        * `_path`: path of the target item. 
        * `_attributes`:a dict of attributes to set into the node.
        
        """
        self.getNode(_path,autocreate=True).setAttr(attr=_attributes, _removeNullAttributes=_removeNullAttributes,**kwargs)
        
    def getAttr(self, path=None, attr=None, default =None):
        """
        This method get the value of the attribute of the node at the given path
        * `path`: path of the given item. 
        * `_atts`: the label of the attribute to get. 
        """
        node =  self.getNode(path)
        if node:
            return node.getAttr(label=attr, default=default)
        else:
            return default
    
    def delAttr(self, path=None, attr=None):
        return self.getNode(path).delAttr(attr)
        
    def _pathSplit(self,path):
        """This method splits a path string it at each '.' and returns a list of
        nodes' labels and the label of the first list's element.
        * `path`: the given path.
        @return label: the first label
        @return pathlist: the list result of path splitting.
        """
        if isinstance(path,basestring):
            escape="\\."
            if escape in path:
                path=path.replace(escape,chr(1))
                pathList = path.split('.')
                pathList=[x.replace(chr(1),'.') for x in pathList]
            else:
                pathList = path.split('.')
        else:
            pathList = list(path)
            
        label = pathList.pop(0)
        return label, pathList

    def asDict(self, ascii=False, lower=False): 
        """
        This method converts a Bag in a Dictionary.
        @return: a Dictionary equivalent to the given Bag.
        
        """
        result={}
        for el in self._nodes:
            key = el.label
            if ascii: key = str(key)
            if lower: key = key.lower()
            result[key] = el.value
        return result
        
#-------------------- addItem --------------------------------
    def addItem(self, item_path, item_value, _attributes=None, _position=">",_validators=None,**kwargs):
        """
        This method adds an item to the current Bag using a path in the form
        "label1.label2...labelN"; it returns the current bag.
        If the path already exists, this method replicates the path keeping old
        values and the new value.
        Parameters:
        
        * item_path: the path of the given item.
        * item_value: the value to set.
        * _attributes: an optional parameter, it specifies the attributes
          of the value to set. Default is 'None'.
        * _position: specifies the position where to add the new item.
          It can be "<" or ">" followed by "#n" or "label". Default is append
          after last item.
        
        Return:the current bag.
        
        """
        return self.setItem(item_path, item_value, _attributes=_attributes, _position=_position, 
                                 _duplicate=True, _validators=_validators, **kwargs)
    
    #-------------------- setItem --------------------------------
    def setItem(self, item_path, item_value, _attributes=None, _position=None, _duplicate=False,
                     _updattr=False, _validators=None,_removeNullAttributes=True, **kwargs):
        """
        This method sets an item in the Bag using a path
        in the form "label1.label2...labelN".It returns the current bag.
        If the path already exists, it overwrites the value at the given path.
        Parameters:
        
        * `item_path`: the path of the given item.
        * `item_value`: the value to set.
        * `_attributes`: an optional parameter, it specified the attributes of
                         the value to set. Default is 'None'.
        * `_position`: an optional parameter, if specified the method setItem()
                       behaves like addItem(). Default is 'None'.
        * `_duplicate`: specifies if a node with an existing path overwrite
                        the value or append it.
        * `_validators`: an optional parameter, it specified the validarors of
                         the value to set. Default is 'None'.
        * `kwargs`: all remaining kwargs can be attributes AND/OR validators .
        
        Return: the current bag.
        """

        if kwargs:
            _attributes=dict(_attributes or {}) 
            _validators=dict(_validators or {}) 
            for k,v in kwargs.items():
                if k.startswith('validate_'):
                    _validators[k[9:]]=v
                else:
                    _attributes[k]=v
        if item_path == '':
            if isinstance(item_value, BagResolver):
                item_value = item_value()
            if isinstance(item_value, Bag):
                for el in item_value:
                    self.setItem(el.label, el.value, _attributes = el.attr, _updattr=_updattr)
                    if el._validators:
                        self.getNode(el.label)._validators=el._validators
            elif 'items' in dir(item_value):
                for key,v in item_value.items():self.setItem(key,v)
            return self
        else: 
            obj, label = self._htraverse(item_path, autocreate=True)
            obj._set(label, item_value, _attributes=_attributes, _position=_position,
                           _duplicate=_duplicate, _updattr=_updattr,
                           _validators = _validators,_removeNullAttributes=_removeNullAttributes)
    __setitem__ = setItem
    
    def _set(self, label, value, _attributes=None, _position=None, 
            _duplicate=False, _updattr=False, _validators=None,_removeNullAttributes=True):
        resolver = None
        if isinstance(value, BagResolver):
            resolver = value
            value = None
            if resolver.attributes:
                _attributes = dict(_attributes or ()).update(resolver.attributes)
        i = self._index(label) 
        if i<0 or _duplicate:
            if label.startswith('#'):
                raise BagException ('Not existing index in #n syntax')
            else:
                self._insertNode(BagNode(self,label=label,value=value,attr=_attributes,
                                resolver=resolver, validators=_validators,
                                _removeNullAttributes=_removeNullAttributes), _position)
        else:
            node=self._nodes[i]
            if resolver != None:
                node.resolver = resolver
            if _validators:
                node.setValidators(_validators)
            node.setValue(value, _attributes=_attributes, _updattr=_updattr,
                        _removeNullAttributes=_removeNullAttributes)
    def defineSymbol(self,**kwargs):
        """
        Define a variable and link it to a value at the specified path. The value
        linked is a BagFormula Resolver.
        * `kwargs`: a dict of symbol to define for a formula.
        """
        if self._symbols == None:
            self._symbols={}
        self._symbols.update(kwargs)
    
    def defineFormula(self,**kwargs):
        """
        Define a formula that uses defined symbols.
        * `kwargs`: a pair of key-value which rapresent the formula and the
        string that describes it.
        """
        if self._symbols== None:
            self._symbols={}
        for key,value in kwargs.items():
            self._symbols['formula:%s' % key] = value
    
    def formula(self, formula, **kwargs):
        """
        Sets a BagFormula resolver.
        * `formula`: a string that represents the expression with symbolic vars
        * `kwargs`: links between symbols and paths associated to their values
        """
        self.setBackRef()
        if self._symbols== None:
            self._symbols={}
        formula =self._symbols.get('formula:%s' % formula, formula)
        parameters=dict(self._symbols)
        parameters.update(kwargs)
        return BagFormula(formula=formula,parameters=parameters)
        
    def getResolver(self,path):
        """
        This method get the resolver of the node at the given path.
        * `path`: path of the node.
        """
        return self.getNode(path).getResolver()
    getFormula=getResolver
    
    def setResolver(self,path,resolver):    
        """
         This method set a resolver into the node at the given path.
         * `path`: path of the node.
         """   
        return self.setItem(path,None,resolver=resolver)
       
    def setBackRef(self, node=None, parent=None):
        """
         This method imposes a more strict structure to a bag.
         It make it more similar to a tree-leaf model: a Bag can have only one Parent
         and it knows has a reference to its Parent.
         
         * `node`: not required
         * `parent`: not required
         """
        if self.backref != True:
            self._backref = True
            self.parent = parent
            self.parentNode = node
            for node in self:
                node.parentbag = self #node property calls back setBackRef recursively

    def delParentRef(self):
        """
        This method set false the reference to the ParentBag of this Bag.
        """
        self.parent = None
        self._backref=False
    
    def clearBackRef(self):
        """
        This method clear all the setBackRef() assumption.
        """
        if self.backref:
            self._backref = False
            self.parent = None
            self.parentNode = None
            for node in self:
                node.parentbag = None
                value = node.staticvalue
                if isinstance(value, Bag):
                    value.clearBackRef()
                    
    def makePicklable(self):
        """
        This method make a Bag picklable.
        """
        if self.backref == True:
            self._backref = 'x'
        self.parent = None
        self.parentNode = None
        for node in self:
            node.parentbag = None
            value = node.staticvalue
            if isinstance(value, Bag):
                value.makePicklable()
                
    def restoreFromPicklable(self):
        """
        This method restore a Bag to its original form from its picklable.
        """
        if self._backref == 'x':
            self.setBackRef()
        else:
            for node in self:
                node.parentbag = None
                value = node.staticvalue
                if isinstance(value, Bag):
                    value.restoreFromPicklable()        
                    
    def _get_backref (self):
        return self._backref
    backref=property(_get_backref)
    
    def _insertNode(self, node, position):
        if not (position) or position == '>':
            n = -1
        elif position == '<':
            n = 0
        elif position[0]=='#':
            n = int(position[1:])
        else:
            if position[0] in '<>':
                position,label=position[0],position[1:]
            else:
                position,label='<',position
            if label[0]=='#':
                n = int(label[1:])
            else:
                n = self._index(label) 
            if position == '>' and n >= 0:
                n = n+1
        if n<0:
            n = len(self._nodes)
        self._nodes.insert(n,node)
        node.parentbag=self
        if self.backref:
            self._onNodeInserted(node, n)
        return n

#-------------------- index --------------------------------
    def _index(self, label):
        """
        This method returns the position of the label into the given bag. 
        It is not recursive. So it works just in the current level. 
        The label can be '#n' where n is the position. 
        The label can be '#attribute=value'.
        If the label doesn't exist it returns -1. 
        The mach is not case sensitive.
        * `label`: a not hierarchical label.
        @return: position into the bag.
        
        """
        result = -1
        if label.startswith('#'):
            if '=' in label:
                k,v = label[1:].split('=')
                if not k: k='id'
                for idx,el in enumerate(self._nodes):
                    if el.attr.get(k,None) == v:
                        result=idx
                        break
            else:
                idx = int(label[1:])
                if idx < len(self._nodes): result = idx
            
        else:
            #f=filter(lambda x: x[1].label==label, enumerate(self._nodes))
            #if len(f)>0:
                #result=f[0][0]
            for idx,el in enumerate(self._nodes):
                if el.label == label:
                    result=idx
                    break
            if result == -1:
                lowlabel = label.lower()
                for idx,el in enumerate(self._nodes):
                    if el.label.lower() == lowlabel:
                        result=idx
                        gnrlogger.warning('Case insensitive result: %s in %s' % (label, str(self.keys())))
                        break
        return result
    
#-------------------- pickle --------------------------------
    def pickle(self,destination=None,bin=True):
        """
        This method returns a pickled Bag.
        
        * `destination`: an optional parameter; it is the destination path;
                         default is 'None'.
        * `bin`: a boolean optional parameter, if set to 'False' the Bag is
                 pickled in ASCII code, if set to 'True' is pickled in binary format.
                 Default is 'True'.
         
        Return: the pickled Bag.
        
        """

        if not destination :
            return pickle.dumps(self,bin)
        if isinstance(destination,file):
            pickle.dump(self,destination,bin)
        else:
            destination=file(destination,mode='w')
            pickle.dump(self,destination,bin)
            destination.close()
            
#-------------------- unpickle --------------------------------
    def unpickle(self,source):
        """
        This method unpickles a pickled Bag.
        * `source`: the source path.
        @return: the unpickled Bag.
        
        """
        source,fromFile,mode=self._sourcePrepare(source)
        if source and mode=='pickle':
            self[:]=self._unpickle(source,fromFile)
            
    def _unpickle(self,source,fromFile):
        if fromFile:
            source = file(source,mode='r')
            result = pickle.load(source)
            source.close()
        else:
            result = pickle.loads(source)
        return result

    def setCallable(self, name, argstring=None, func='pass'):
        """
        review
        """
        setCallable(self, name, argstring=argstring, func=func)

#-------------------- toXml --------------------------------
    def toXml(self,filename=None,encoding='UTF-8',typeattrs=True,typevalue=True, unresolved=False, addBagTypeAttr=True,
              autocreate=False, jsonmode=None, jsonkey=None, translate_cb=None,self_closed_tags=None,
              omitUnknownTypes=False, catalog=None, omitRoot=False, forcedTagAttr=None,docHeader=None):
        """
        This method returns a complete standard XML version of the Bag,
        including the encoding tag <?xml version=\'1.0\' encoding=\'UTF-8\'?>
        the content of the Bag is hierarchically represented as an XML block
        sub-element of the node <GenRoBag> (see the toXmlBlock() documentation
        for more details about type representation).
        Is also possible to write the result on a file, passing the path of the file
        as the 'filename' parameter.
        
        * `filename`: an optional parameter, it is the path of the output file;
                      default value is 'None'
        * `encoding`: an optional parameter, is used to set the XML encoding;
                      default value is UTF-8.
         
        Return: an XML version of the bag.
        
            >>> mybag=Bag()
            >>> mybag['aa.bb']=4567
            >>> mybag.toXml()
            '<?xml version=\'1.0\' encoding=\'iso-8859-15\'?>
             <GenRoBag>
             <aa><bb T="L">
             4567</bb></aa></GenRoBag>'
        """
        from gnr.core.gnrbagxml import BagToXml
        return BagToXml().build(self, filename=filename, encoding=encoding,typeattrs=typeattrs,typevalue=typevalue, addBagTypeAttr=addBagTypeAttr,
                                    unresolved=unresolved,autocreate=autocreate, forcedTagAttr=forcedTagAttr,
                                    jsonmode=jsonmode,jsonkey=jsonkey, translate_cb=translate_cb, self_closed_tags=self_closed_tags,
                                    omitUnknownTypes=omitUnknownTypes, catalog=catalog, omitRoot=omitRoot,docHeader=docHeader)
        
    def fillFrom(self, source):
        """
        This method fills a void Bag from: basestring, bag, list.
        
        * `source`: the source for the Bag.
                      
        """
        if isinstance(source, basestring) :
            b = self._fromSource(*self._sourcePrepare(source))
            if not b: b = Bag()
            self._nodes[:] = b._nodes[:]
            
        elif isinstance(source, Bag) :
            self._nodes = [BagNode(self,*x.asTuple()) for x in source]
        elif isinstance(source, list) or isinstance(source, tuple) :
            if len(source)>0:
                if not (isinstance(source[0], list) or isinstance(source[0], tuple)):
                    source=[source]
                for x in source: 
                    if len(x)==3:
                        self.setItem(x[0], x[1], _attributes=x[2])
                    else:
                        self.setItem(x[0], x[1])
        elif hasattr(source,'items'):
            for key,value in source.items():
                if hasattr(value, 'items'):
                    value = Bag(value)
                self.setItem(key, value)
    
    def _fromSource(self, source, fromFile, mode):
        """
        * `source`: the source string or source URI
        * `fromFile`: flag that says if source is eventually an URI
        * `mode`: flag that means the importation mode (XML, pickle or VCARD)
        @return: a bag from unpickle or from fromXml
        
        This method receives "mode" and "fromFile" and switch between the different
        modes calling _fromXml or _unpickle
        
        """  
        if not source:
            return
                
        if mode=='xml' :  
            return self._fromXml(source,fromFile)
        elif mode=='pickle':
            return self._unpickle(source,fromFile)
        elif mode=='direct':
            return Bag((os.path.basename(source).replace('.','\.'), UrlResolver(source)))
        elif mode=='isdir':
            source=source.rstrip('/')
            return Bag((os.path.basename(source), DirectoryResolver(source)))
        elif mode == 'unknown':
            raise  BagException('invalid source: %s' % source)
        
        
        
    def _sourcePrepare(self,source):
        """
        Generate a Bag from a generic xml
        * `source`: an xml string or a path to an xml document.
        @type source: basestring
        @return: source, fromFile, mode
        "source" parameter can be either a URI (file path or URL) or a string.
        If source is a an URI the method opens and reads the identified file an sets
        the value of the flag "fromFile" to true.
        Anyway source can be a well-formed XML document, or a raw one,or even a
        pickled bag. In any of this cases the method sets the value of the flag
        "mode" to xml, vcard or pickle and returns it with "source" and "fromFile"
            
        """
        originalsource=source
        if source.startswith('<'):
            return source, False, 'xml'
        if len(source)>300:
            #if source is longer than 300 chars it cannot be a path or an URI
            return source, False, 'unknown' #it is a long not xml string
        urlparsed = urlparse.urlparse(source)
        if not urlparsed[0] or urlparsed[0]=='file':
            source = urlparsed[2]
            if os.path.exists(source):
                if os.path.isfile(source):
                    fname,fext = os.path.splitext(source)
                    fext=fext[1:]
                    if fext in ['pckl','pkl']:
                        return source, True, 'pickle'
                    elif fext in ['xml','html','xhtml','htm']:
                        return source, True, 'xml'
                    else:
                        f=file(source,mode='r')
                        sourcestart = f.read(30)
                        f.close()
                        if sourcestart.startswith('<'):
                            return source,True, 'xml' #file xml with unknown extension
                        else:
                            return source,True, 'unknown' #unidentified file
                elif os.path.isdir(source):
                    return source,False, 'isdir' #it's a directory
            else:
                return originalsource, False, 'unknown' #short string of unknown type
        urlobj = urllib.urlopen(source)
        info = urlobj.info()
        contentType = info.gettype()
        if 'xml' in contentType or 'html' in contentType:
            return urlobj.read(), False, 'xml' #it is an url of type xml
        return source, False, 'direct' #urlresolver
                 
   
    
#-------------------- fromXml --------------------------------
    def fromXml(self, source,catalog=None,bagcls=None,empty=None):
        """
        This method fills the Bag with values read from an XML string or file or URL.
        * `source`: the XML source to be loaded in the Bag. 
        * `catalog`:
        * `bagcls`:
        bagcls empty:
        """
        source, fromFile, mode = self._sourcePrepare(source)
        self._nodes[:] = self._fromXml(source, fromFile, catalog=catalog,
                                          bagcls=bagcls,empty=empty)
        
    def _fromXml(self, source, fromFile,catalog=None,bagcls=None,empty=None):
        from gnr.core.gnrbagxml import BagFromXml
        return BagFromXml().build(source, fromFile,catalog=catalog,bagcls=bagcls,empty=empty)
        
    def getIndex(self):
        """
        This method return the index of the Bag with all the internal address.
        """
        path = []
        resList = []
        exploredNodes = [self]
        self._deepIndex(path, resList, exploredNodes)
        return resList
    
    def _deepIndex(self,path,resList,exploredItems):
        for node in self._nodes:
            v = node.value
            resList.append((path+[node.label], node))
            if hasattr(v, '_deepIndex'):
                if not v in exploredItems:
                    exploredItems.append(v)
                    v._deepIndex(path+[node.label], resList, exploredItems)
                    
    def getIndexList(self,asText=False):
        """
        This method return the index of the Bag as a plan list of the Nodes paths.
        """
        l = self.getIndex()
        l=['.'.join(x) for x,y in l]
        if asText :
            return '\n'.join(l)
        return l
    

    def addValidator(self, path, validator, parameterString):
        """
        This method add a validator into the node at the given path
        * `path`: path of the node.
        * `validator`: the type of validation.
        * `parameterString`: string which contains the params for validation.
        """
        self.getNode(path,autocreate=True).addValidator(validator, parameterString)
        
    def removeValidator(self, path, validator):
        """
        This method add a validator into the node at the given path
        """
        self.getNode(path).removeValidator(validator)

    def _onNodeChanged(self, node, pathlist, evt, oldvalue=None):
        """
        This method is called from the trigger system and set a function at changing events
        """
        for s in self._upd_subscribers.values():
            s(node=node, pathlist=pathlist, oldvalue=oldvalue, evt=evt)
        if self.parent: 
            self.parent._onNodeChanged(node, [self.parentNode.label]+pathlist, evt ,oldvalue)
        
    def _onNodeInserted(self,node,ind, pathlist=None):
        """
        This method is called from the trigger system and set a function at inserting events
        """
        if pathlist==None:
            pathlist=[]        
        for s in self._ins_subscribers.values():
            s(node=node, pathlist=pathlist, ind=ind, evt='ins')
        if self.parent: 
            self.parent._onNodeInserted(node,ind, [self.parentNode.label]+pathlist)
    
    def _onNodeDeleted(self,node,ind, pathlist=None):
        """
        This method is called from the trigger system and set a function at deleting events
        """
        for s in self._del_subscribers.values():
            s(node=node, pathlist=pathlist, ind=ind, evt='del')
        if self.parent:
            if pathlist==None:
                pathlist=[]
            self.parent._onNodeDeleted(node,ind, [self.parentNode.label]+pathlist)
        
    def _subscribe(self, subscriberId, subscribersdict, callback):
        if not callback is None :
            subscribersdict[subscriberId]=callback
        
    def subscribe(self, subscriberId, update=None, insert=None, delete=None, any=None):
        """
        This method provides a subscribing of a function to an event.
        Subscribing an event on a Bag means that every time that it happens,
        it is propagated along the bag hierarchy and is triggered by its
        eventhandler. A subscription can be seen as a couple event-function,
        this means that I can define many eventhandlers for the same event.
        
        * `subscriberId`: an ID can be assigned for a subscription
        * `update`: the eventhandler function linked to update event.
        * `insert`: the eventhandler function linked to insert event.
        * `delete`: the eventhandler function linked to delete event.
        * `any`: the eventhandler function linked to do whenever something happens.
        """
        if self.backref == False:
            self.setBackRef()
            
        self._subscribe(subscriberId, self._upd_subscribers, update or any)
        self._subscribe(subscriberId, self._ins_subscribers, insert or any)
        self._subscribe(subscriberId, self._del_subscribers, delete or any)
        
    def unsubscribe(self,subscriberId, update=None,insert=None,delete=None, any=None):
        """
        delete a subscription of an event of given subscriberId.
        
        * `subscriberId`: an ID can be assigned for a subscription
        * `update`: the eventhandler function to remove
        * `insert`: the eventhandler function to remove
        * `delete`: the eventhandler function to remove
        * `any`: the eventhandler function to remove
        
        """
        if update or any:
            self._upd_subscribers.pop(subscriberId)
        if insert or any:
            self._ins_subscribers.pop(subscriberId)
        if delete or any:
            self._del_subscribers.pop(subscriberId)
        
    def setCallBackItem(self, path, callback, **kwargs):
        resolver = BagCbResolver(callback, **kwargs)
        self.setItem(path, resolver, **kwargs)
        
    def cbtraverse(self, pathlist, callback, result=None, **kwargs):
        if result is None:
            result = []
        if isinstance(pathlist, basestring):
            pathlist = gnrstring.smartsplit(pathlist.replace('../','#^.'),'.')
            pathlist = [x for x in pathlist if x]
        label = pathlist.pop(0)
        i = self._index(label)
        if i >= 0:
            result.append(callback(self._nodes[i], **kwargs))
            if pathlist:
                self._nodes[i].getValue().cbtraverse(pathlist, callback, result, **kwargs)
        return result
    
    def findNodeByAttr(self,attr,value):
        def f(node):
            if node.getAttr(attr) == value:
                return node
        return self.walk(f)
        
    def walk(self, callback, _mode='static', **kwargs):
        """
        Calls a function for each node of the Bag.
        * `callback`: the function which is called. 
        """
        result=None
        for node in self.nodes:
            result=callback(node,**kwargs)
            if result is None:
                value=node.getValue(mode=_mode)
                if isinstance(value,Bag):
                     result=value.walk(callback, _mode=_mode, **kwargs) 
            if result:
                return result
                
    def traverse(self):
        for node in self.nodes:
            yield node
            value=node.getStaticValue()
            if isinstance(value,Bag):
                for node in value.traverse():
                    yield node 

    def rowchild(self,childname='R_#', _pkey=None, **kwargs):
        if not childname:
            childname='R_#'
        childname = childname.replace('#', str(len(self)).zfill(8))
        _pkey=_pkey or childname
        return self.setItem(childname, None,_pkey=_pkey, _attributes=kwargs)
        
    def child(self, tag, childname='*_#', childcontent=None, _parentTag=None, **kwargs):
        """This method sets a new item of the type tag into the current structure
        * `tag`: structure type
        * `name`: structure name. Default value is formed by 'tag_position'
        * `content`: optional structure content
        * `kwargs`: other parameters
        @return : the new structure if content is none else the parent"""
        where=self
        if not childname:
            childname='*_#'
        if '.' in childname:
            namelist=childname.split('.')
            childname=namelist.pop()
            for label in namelist:
                if not label in where:
                    item = self.__class__()
                    where[label] = item
                where = where[label]
        childname = childname.replace('*', tag).replace('#', str(len(where)))
        
        if childcontent == None: 
            childcontent = self.__class__()
            result = childcontent
        else:
            result=None
            
        if _parentTag:
            if isinstance(_parentTag, basestring):
                _parentTag = gnrstring.splitAndStrip(_parentTag, ',')
            actualParentTag = where.getAttr('', tag)
            if not actualParentTag in _parentTag:
                raise BagException('%s "%s" cannot be inserted in a %s' % (tag, childname, actualParentTag))
        if childname in where and where[childname] != '' and where[childname] is not None:
            if where.getAttr(childname, 'tag') != tag:
                raise BagException('Cannot change %s from %s to %s' % (childname, where.getAttr(childname, 'tag'), tag))
            else:
                kwargs = dict([(k,v) for k,v in kwargs.items() if v != None]) # default kwargs don't clear old attributes
                result = where[childname]
                result.attributes.update(**kwargs)
        else:
            where.setItem(childname, childcontent, tag=tag, _attributes=kwargs)
        return result

class BagValidationList(object):
    """
    This class provides the validation system for a BagNode. This is a list
    of validators related to a BagNode. This class is used only from a the Bag's
    and BagNode's accessor methods addValidator and removeValidator.
    All the methods of this class must be considered private.
    """
    def __init__(self, parentNode):
        self.parentNode = parentNode
        self.validators = []
        self.validatorsdata = {}
        self.status= None
        self.errMsg=None

    def getdata(self,validator,label=None,dflt=None):
        """
        This method get the validatorsdata of a validator.
        """
        if validator in self.validatorsdata:
            data=self.validatorsdata [validator]
            if label is None:
                return data
            else :
                return data.get(label,dflt)
                
    def _set_node(self, node):
        if node != None:
            #self._node = weakref.ref(node)
            self._node = node
        else:
            self._node = None
            
    def _get_node(self):
        if self._node != None:
            #return self._node()
            return self._node
            
    node = property(_get_node, _set_node)
    
    def add(self, validator, parameterString):
        """
        This method add a new validator to the BagValidationList.
        * `validator`: type of validator
        * `parameterString`: the string that contains the parameters for
        the validators.
        """
        if isinstance(validator,basestring):
            validator = getattr(self,'validate_%s' % validator, self.defaultExt)
        if not validator in self.validators:
            self.validators.append(validator)
            self.validatorsdata[validator] = parameterString
            
    def remove(self,validator):
        """
        This method remove a validator
        """
        if validator in self.validators:
            self.validators.remove(validator)
            

    def __call__(self, value, oldvalue):
        """
        This method apply the validation to a BagNode value.
        """
        for validator in self.validators:
            value = validator(value, oldvalue, self.validatorsdata[validator])
        return value
    
    def validate_case(self,value, oldvalue, parameterString):
        """
        This method is set a validation for the case of a string value.
        * `parameterString`: this can be
        'upper'
        'lower'
        'capitalize'
        """
        mode=parameterString
        if not isinstance (value, basestring):
            raise BagValidationError('not a string value',value,'The value is not a string')
        else:
            if mode.lower()=='upper':
                value=value.upper()
            elif mode.lower()=='lower':
                value=value.lower()
            elif mode.lower()=='capitalize':
                value=value.capitalize()
            return value
        
    def validate_inList(self,value, oldvalue, parameterString):
        values=parameterString.split(',')
        if not value in values:
            raise BagValidationError('NotInList',value,'The value is non in list')
        else:
            return value
        
    def validate_hostaddr (self,value, oldvalue):
        """
        This method provides a validaton for Host address value
        """
        import socket
        try:
            x=socket.gethostbyaddr(socket.gethostbyname(value))
            hostaddr,hostname=x[2][0],x[0]
            self.validatorsdata['hostaddr']={'hostname':hostname}
            return hostaddr
        except:
            hostaddr=value
            self.validatorsdata['hostaddr']={'hostname':'Unknown host'}
            raise BagValidationError('Unknown host',value,'The host is not valid')

    def validate_length(self,value, oldvalue, parameterString):
        """
        This method provides a validaton for the length of a string value
        """
        minmax = parameterString.split(',')
        min = minmax[0]
        max = minmax[1]
        n=len(value)
        if (not min is None) and n <min:
            raise BagValidationError('Value too short',value,'The length of value is too short')
        if (not max is None) and n >max:
            raise BagValidationError('Value too long',value,'The length of value is too long')
        return value
    
    def coerceFromText(self,value):
        value=converter.fromText(value, self.gnrtype)
        
    def validate_db(self,value, oldvalue, parameterString):
        print value
        return value
        
    def defaultExt (self,value, oldvalue, parameterString):
        print 'manca il  validatore'

class BagResolver(object):
    """
    BagResolver is an abstract class, that defines the interface
    for a new kind of dynamic objects. By "Dynamic" we mean, properties
    that are calculated in real-time but looks like static ones.
    """
    classKwargs={'cacheTime':0, 'readOnly':True}
    classArgs=[]
    def __init__(self,*args,**kwargs):
        self._initArgs = list(args)
        self._initKwargs = dict(kwargs)
        self.parentNode = None
        self.kwargs = {}
        classKwargs = dict(self.classKwargs)
        for j,arg in enumerate(args):
            parname = self.classArgs[j]
            setattr(self, parname, arg)
            classKwargs.pop(parname, None)
            kwargs.pop(parname, None)
        
        for parname, dflt in classKwargs.items():
            setattr(self, parname, kwargs.pop(parname,dflt))
        self.kwargs.update(kwargs)
        
        self._attachKwargs()
        
        self._attributes={}# ma servono ?????
        self.init()
        
    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and (self.kwargs==other.kwargs):
                return True
        except:
            return False
        
    def _get_parentNode(self):
        if self._parentNode:
            return self._parentNode
            #return self._parentNode()
        
    def _set_parentNode(self, parentNode):
        if parentNode == None:
            self._parentNode = None
        else:
            #self._parentNode = weakref.ref(parentNode)
            self._parentNode = parentNode
    parentNode = property(_get_parentNode, _set_parentNode)
    
    def _get_instanceKwargs(self):
        result={}
        for par, dflt in self.classKwargs.items():
            result[par]=getattr(self,par)
        for par in self.classArgs:
            result[par]=getattr(self,par)
        return result
    instanceKwargs=property(_get_instanceKwargs)
    
    def _attachKwargs(self):
        for k,v in self.kwargs.items():
            setattr(self,k,v)
            if k in self.classKwargs:
                self.kwargs.pop(k)
    
    def _set_cacheTime(self, cacheTime):
        self._cacheTime=cacheTime
        if cacheTime != 0:
            if cacheTime <0:
                self._cacheTimeDelta=timedelta.max
            else:
                self._cacheTimeDelta = timedelta(0, cacheTime)
            self._cache = None
            self._cacheLastUpdate = datetime.min
        
    def _get_cacheTime(self):
        return self._cacheTime 
    cacheTime=property(_get_cacheTime, _set_cacheTime)
    
    def reset(self):
        self._cache = None
        self._cacheLastUpdate = datetime.min

    def _get_expired(self):
        if self._cacheTime == 0 or self._cacheLastUpdate == datetime.min:
            return True
        return ((datetime.now() - self._cacheLastUpdate ) > self._cacheTimeDelta)
    expired=property(_get_expired)
    
    def __call__(self,**kwargs):
        if kwargs and kwargs != self.kwargs:
            self.kwargs.update(kwargs)
            self._attachKwargs()
            self.reset()
            
        if self.cacheTime==0:
            return self.load() 
            
        if self.expired:
            result = self.load() 
            self._cacheLastUpdate = datetime.now()
            self._cache = result
        else:
            result = self._cache
        return result
    
    def load(self):
        """must be reimplemented"""
        pass 
    
    def init(self):
        pass
    
    def resolverSerialize(self):
        attr = {}
        attr['resolverclass'] = self.__class__.__name__
        attr['resolvermodule'] = self.__class__.__module__
        attr['args'] = self._initArgs
        attr['kwargs'] = self._initKwargs
        return attr

    def __getitem__(self,k):
        return self().__getitem__(k)
    
    def _htraverse(self,*args,**kwargs):
        return self()._htraverse(*args,**kwargs)
    
    def keys(self):
        return self().keys()
    
    def items(self):
        return self().items()
    
    def values(self):
        return self().values()
    
    def digest(self,k=None):
        return self().digest(k)
    
    def sum(self,k=None):
        return self().sum(k)
    
    def iterkeys(self):
        return self().iterkeys()
    
    def iteritems(self):
        return self().iteritems()
    
    def itervalues(self):
        return self().itervalues()
    
    def __iter__(self):
        return self().__iter__()
    
    def __contains__(self):
        return self().__contains__()
    
    def __len__(self):
        return len(self())
    
    def getAttributes(self):
        return self._attributes
    
    def setAttributes(self,attributes):
        self._attributes=attributes or dict()
    attributes=property(getAttributes,setAttributes)
    
    def resolverDescription(self):
        return repr(self)
    
    def __str__(self):
        return self.resolverDescription()
        
class GeoCoderBag(Bag):
    def setGeocode(self,key,address):
        k="ABQIAAAAUwVfREP6FPJzAIxWuaT4_BQXq7bWTC04Ff1KKaIsErBhwE7B5xSKrucRzm000Ur7Cm-a9MmuppH4ag"
        url="http://maps.google.com/maps/geo?%s" % urllib.urlencode(dict(key=k,q=address,output='xml'))
        result=Bag()
        def setData(n):
            v=n.getValue()
            if isinstance (v,basestring):
                result[n.label]=v
        answer=Bag(url)['#0.#0.Placemark']
        if answer:
            answer.walk(setData)
        self[key]=result
        
class BagCbResolver(BagResolver):
    """This is a standard resolver. It calls a callback method, passing its kwargs parameters
    """
    classArgs=['method']
    def load(self):
        return self.method(**self.kwargs)
            
class UrlResolver(BagResolver):
    classKwargs={'cacheTime':300, 'readOnly':True}
    classArgs=['url']
    
    def load(self):
        x=urllib.urlopen(self.url)
        result={}
        result['data']=x.read()
        result['info']=x.info()
        return result
        
class DirectoryResolver(BagResolver):
    classKwargs={'cacheTime':500,
                 'readOnly':True,
                 'invisible':False,
                 'relocate':'',
                 'ext':'xml',
                 'include':'',
                 'exclude':'',
                 'callback':None,
                 'dropext':False,
                 'processors':None
                }
    classArgs=['path','relocate']
    
    def load(self):
        extensions=dict([((ext.split(':')+(ext.split(':'))))[0:2] for ext in self.ext.split(',')])
        extensions['directory']='directory'
        result=Bag()
        try:
            directory=os.listdir(self.path)
        except OSError:
            directory = []
        if not self.invisible:
            directory=[x for x in directory if not x.startswith('.')]
        for fname in directory:
            nodecaption=fname
            fullpath=os.path.join(self.path, fname)
            relpath=os.path.join(self.relocate, fname)
            addIt=True
            if os.path.isdir(fullpath):
                ext='directory'
                if self.exclude:
                    addIt = gnrstring.filter(fname,exclude=self.exclude, wildcard='*')
            else:
                if self.include or self.exclude:
                    addIt=gnrstring.filter(fname,include=self.include,exclude=self.exclude, wildcard='*')
                fname, ext = os.path.splitext(fname)
                ext=ext[1:]
            if addIt:
                label=self.makeLabel(fname,ext)
                handler=getattr(self,'processor_%s' % extensions.get(ext.lower(),None), None)
                if not handler:
                    processors = self.processors or {}
                    handler=processors.get(ext.lower(), self.processor_default)
                try:
                    stat = os.stat(fullpath)
                    mtime=stat.st_mtime
                except OSError:
                    mtime=''
                
                if self.callback:
                    moreattr = self.callback(fullpath)
                else:
                    moreattr = {}
                result.setItem(label, handler(fullpath), file_name=fname, file_ext=ext, rel_path=relpath, abs_path=fullpath, mtime=mtime, nodecaption=nodecaption, **moreattr)
        return result
    
    def makeLabel(self,name,ext):
        if ext != 'directory' and not self.dropext:
            name='%s_%s' % (name, ext)
        return name.replace('.', '_' )

    def processor_directory(self,path):
        return DirectoryResolver(path,os.path.join(self.relocate,os.path.basename(path)), **self.instanceKwargs)
    
    def processor_xml(self, path):
        kwargs = dict(self.instanceKwargs)
        kwargs['path'] = path
        return XmlDocResolver(**kwargs)
    processor_html=processor_xml
    
    def processor_txt(self,path):
        kwargs = dict(self.instanceKwargs)
        kwargs['path'] = path
        return TxtDocResolver(**kwargs)
    
    def processor_default(self,path):
        return None

class TxtDocResolver(BagResolver):
    classKwargs={'cacheTime':500,
                 'readOnly':True
                }
    classArgs=['path']
    
    def load(self):
        f = file(self.path, mode='r')
        result = f.read()
        f.close()
        return result
    
class XmlDocResolver(BagResolver):
    classKwargs={'cacheTime':500,
                 'readOnly':True
                }
    classArgs=['path']
    
    def load(self):
        return Bag(self.path)
    
    
class BagFormula(BagResolver):
    """This resolver calculates the value of an algebric espression
    """
    classKwargs={'cacheTime':0,
                 'formula':'',
                 'parameters':None, 'readOnly':True
                }
    classArgs=['formula','parameters']
    
    def init(self):
        """
        * `root`:
        * `expr`: expression with symbolic terms
        * `symbols`: 
        """
        parameters = {}
        for key,value in self.parameters.items():
            if key.startswith('_'):
                parameters[key]="curr.getResolver('%s')" % value
            else:
                parameters[key] = "curr['%s']" % value
        self.expression = gnrstring.templateReplace(self.formula, parameters)

    def load(self):
        curr = self.parentNode.parentbag
        return eval(self.expression)

########################### start experimental features#######################
class BagResolverNew(object):
    """docstring for BagResolver"""
    
    def __init__(self,cacheTime=0, readOnly=True,
                    serializerStore=None, **kwargs):
        self.serializerStore=serializerStore
        self.kwargs={}
        self._updateKwargs(dict(cacheTime=cacheTime, readOnly=readOnly))      
        self._updateKwargs(kwargs)  
            
    def _get_serializerStore(self):
        if self._serializerStore is None:
            return self._serializerStore
        else:
            return self._serializerStore
            #return self._serializerStore()
            
    def _set_serializerStore(self, serializerStore):
        if serializerStore is None:
            self._serializerStore = serializerStore
        else:
            #self._serializerStore = weakref.ref(serializerStore)
            self._serializerStore = serializerStore
    serializerStore = property(_get_serializerStore, _set_serializerStore)
    
    def _getPar(self,name):
        attr = getattr(self,name)
        if isinstance(attr,basestring) or \
                  isinstance(attr,int) or \
                  isinstance(attr,float):
            return attr
        elif self.serializerStore is None:
            raise 'Missing SerializerStore'
        else:
            key = '%s' % name
            self.serializerStore[key]=attr
            return key
    
    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and (self.kwargs==other.kwargs):
                return True
        except:
            return False

    def _get_parentNode(self):
        if self._parentNode:
            return self._parentNode
            #return self._parentNode()

    def _set_parentNode(self, parentNode):
        if parentNode == None:
            self._parentNode = None
        else:
            #self._parentNode = weakref.ref(parentNode)
            self._parentNode = parentNode
    parentNode = property(_get_parentNode, _set_parentNode)

    def _set_cacheTime(self, cacheTime):
        self._cacheTime=cacheTime
        if cacheTime != 0:
            if cacheTime <0:
                self._cacheTimeDelta=timedelta.max
            else:
                self._cacheTimeDelta = timedelta(0, cacheTime)
            self._cache = None
            self._cacheLastUpdate = datetime.min

    def _get_cacheTime(self):
        return self._cacheTime 
    cacheTime=property(_get_cacheTime, _set_cacheTime)

    def reset(self):
        self._cache = None
        self._cacheLastUpdate = datetime.min

    def _get_expired(self):
        if self._cacheTime == 0 or self._cacheLastUpdate == datetime.min:
            return True
        return ((datetime.now() - self._cacheLastUpdate ) > self._cacheTimeDelta)
    expired=property(_get_expired)
 
    def _updateKwargs(self, kwargs):
        """docstring for _updateKwargs"""
        reset = False
        for k,v in kwargs.items():
            if self.kwargs.get(k) != v:
                reset = True
                self.kwargs(k,v)
                setattr(self,k,v)
        if reset:
            self.reset()
    
    def __call__(self,**kwargs):
        if kwargs:
            self._updateKwargs(kwargs)

        if self.cacheTime==0:
            return self.load() 

        if self.expired:
            result = self.load() 
            self._cacheLastUpdate = datetime.now()
            self._cache = result
        else:
            result = self._cache
        return result

    def load(self):
        """must be reimplemented"""
        pass 

    def init(self):
        pass

    def resolverSerialize(self):
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'],attr['kwargs'] = self._argSerializer()
        return attr

    def __getitem__(self,k):
        return self().__getitem__(k)

    def _htraverse(self,*args,**kwargs):
        return self()._htraverse(*args,**kwargs)

    def keys(self):
        return self().keys()

    def items(self):
        return self().items()

    def values(self):
        return self().values()

    def digest(self,k=None):
        return self().digest(k)

    def sum(self,k=None):
        return self().sum(k)

    def iterkeys(self):
        return self().iterkeys()

    def iteritems(self):
        return self().iteritems()

    def itervalues(self):
        return self().itervalues()

    def __iter__(self):
        return self().__iter__()

    def __contains__(self):
        return self().__contains__()

    def __len__(self):
        return len(self())

    def getAttributes(self):
        return self._attributes

    def setAttributes(self,attributes):
        self._attributes=attributes or dict()
    attributes=property(getAttributes,setAttributes)

    def resolverDescription(self):
        return repr(self)

    def __str__(self):
        return self.resolverDescription()
            
########################### end experimental features#########################



def testFormule():
    b= Bag()
    b.defineFormula(calc_riga_lordo='$riga_qta*$riga_prUnit')
    b.defineSymbol(riga_qta='qta',riga_prUnit='prUnit')
    b.defineFormula(calc_riga_netto='$riga_lordo*(100+$riga_sconto)/100')
    b.defineSymbol(riga_lordo='lordo',riga_sconto='../../sconto')
    b.defineFormula(sum_riga_netto="$righe.sum('netto')")
    b.defineSymbol(righe='righe')

    b['ft1.num'] = '12345'
    b.setItem('ft1.date', '2006-1-3')
    b['ft1.sconto'] = 5
    b['ft1.netto']=b.formula('sum_riga_netto')
    b['ft1.iva']=b.formula('$netto*0.2',netto='netto')
    b['ft1.totalefattura']=b.formula('$netto+$iva',netto='netto',iva='iva')
    b['ft1.righe.1.cod'] = 'b21'
    b['ft1.righe.1.desc'] = 'pollo'
    b['ft1.righe.1.prUnit'] = 3.5
    b['ft1.righe.1.qta'] = 2
    b['ft1.righe.1.lordo']=b.formula('calc_riga_lordo')
    b['ft1.righe.1.netto']=b.formula('calc_riga_netto')
    b['ft1.righe.2.cod'] = 'h26'
    b['ft1.righe.2.desc'] = 'trota'
    b['ft1.righe.2.prUnit'] = 9.2
    b['ft1.righe.2.qta'] = 1
    riga2 = b['ft1.righe.2']
    riga2['lordo']=b.formula('calc_riga_lordo')
    riga2['netto']=b.formula('calc_riga_netto')
    b['ft1.righe.3.cod'] = 'w43'
    b['ft1.righe.3.desc'] = 'manzo'
    b['ft1.righe.3.prUnit'] = 4.
    b['ft1.righe.3.qta'] = 4
    b['ft1.righe.3.lordo']=b.formula('calc_riga_lordo')
    b['ft1.righe.3.netto']=b.formula('calc_riga_netto')
    
    a= b['ft1.righe.1.lordo']
    
    print b
    print b['?']
    print b['ft1.righe.?']
    
    print b['ft1.totalefattura']
    print b['ft1.netto']
    print b['ft1.iva']
    
    print b['ft1.righe.1.lordo']
    print b['ft1.righe.1.netto']
    print b['ft1.righe.2.lordo']
    print b['ft1.righe.2.netto']
    print b['ft1.righe.3.lordo']
    print b['ft1.righe.3.netto']
    b['ft1.sconto'] = 10
    print b['ft1.totalefattura']


class TraceBackResolver(BagResolver):
    classKwargs={'cacheTime': 0, 'limit': None}
    classArgs=[]
    
    def load(self):
        import sys, linecache
        result = Bag()
        limit = self.limit
        if limit is None:
            if hasattr(sys, 'tracebacklimit'):
                limit = sys.tracebacklimit
        list = []
        n = 0
        tb = sys.exc_info()[2]
        while tb is not None and (limit is None or n < limit):
            tb_bag = Bag()
            
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno)
            if line: line = line.strip()
            else: line = None
            tb_bag['module'] = os.path.basename(os.path.splitext(filename)[0])
            tb_bag['filename'] = filename
            tb_bag['lineno'] = lineno
            tb_bag['name'] = name
            tb_bag['line'] = line
            tb_bag['locals'] = Bag(f.f_locals.items())
            tb = tb.tb_next
            n = n+1
            result['%s method: %s line: %s' % (tb_bag['module'], name, lineno)] = tb_bag
        return result
    
def testfunc (**kwargs):
    print kwargs

#import Pyro.core
#class PyroBag(Bag, Pyro.core.ObjBase):
#    def __init__(self):
#        Bag.__init__(self)
#        Pyro.core.ObjBase.__init__(self)
        
if __name__=='__main__':
    b=Bag()
    b.setItem('aa',4,_attributes={'aa':4,'bb':None},_removeNullAttributes=False)
    print b.toXml()
    
    
    
    
    