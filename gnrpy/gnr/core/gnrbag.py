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
The gnrbag module contains a single class intended to be used: Bag.

A Bag is a generic container object, similar to a dictionary, with some useful properties:

    * it is ordered
    * accessibility by key
    * iterability
    * it is hierarchic

A Bag can store any kind of python object with a label in an ordered list.
It can also store attributes about any value stored: Bag attributes are metadata
that are an addition to the stored object without distrurbing the stored data.

A Bag can be loaded and saved in some ways:

    * saved to and loaded from pikle files or strings: the object stored in the bag
      must be picklable of course
    * saved to and loaded from xml files or strings with a specific syntax: the object
      stored in the Bag must be strings, numbers or dates
    * loaded from a generic xml file preserving the whole hierarchical structure and
      the attributes: all values will be of type string of course
    * loaded from a generic html file: requires tidy.

Another class you could have to deal with is BagNode (a Bag is a list of BagNode-s).

BagNode is not intended to be instanced directly, it is used internally by Bag, however in some cases is useful
to interact with BagNode instances inside a Bag.

.. note:: The square brackets around some parameters in the following method signature denote
          that the parameter is optional, not that you should type square brackets at that position.
          You will see this notation frequently in the :ref:`Genro Library Reference <library_reference>`
          
.. note:: Some methods have the "square-brackets notation": it is a shorter notation for the method"""

#import weakref
import copy
import cPickle as pickle
from datetime import datetime, timedelta
import urllib, urlparse
from gnr.core import gnrstring
from gnr.core.gnrclasses import GnrClassCatalog as converter
from gnr.core.gnrlang import setCallable, GnrObject, GnrException
import os.path
import logging
import sys

gnrlogger = logging.getLogger(__name__)


    
class BagNodeException(GnrException):
    pass
    
class BagException(GnrException):
    pass
    
class BagAsXml(object):
    def __init__(self, value):
        self.value = value
        
class BagValidationError(BagException):
    pass
    # def __init__(self, errcode, value, message):
    # self.errcode=errcode
    #self.value = str(value)
    #self.message = message
    
class BagDeprecatedCall(BagException):
    def __init__(self, errcode, message):
        self.errcode = errcode
        self.message = message
        
class BagNode(object):
    """BagNode is the element type which a Bag is composed of. That's why it's possible to say that a Bag
    is a collection of BagNodes. A BagNode is an object that gather within itself, three main things:
    
    * *label*: can be only a string.
    * *value*: can be anything even a BagNode. If you got the xml of the Bag it should be serializable
    * *attributes*: dictionary that contains node's metadata"""

    def __init__(self, parentbag, label, value=None, attr=None, resolver=None,
                 validators=None, _removeNullAttributes=True):
        self.label = label
        self.locked = False
        self._value = None
        self.resolver = resolver
        self.parentbag = parentbag
        self._node_subscribers = {}
        self._validators = None
        self.attr = {}
        if attr:
            self.setAttr(attr, trigger=False, _removeNullAttributes=_removeNullAttributes)
        if validators:
            self.setValidators(validators)
        self.setValue(value, trigger=False)
        
    def __eq__(self, other):
        """One BagNode is equal to another one if its key, value, attributes and resolvers are the same of the other one"""
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
        """TODO"""
        for k, v in validators.items():
            self.addValidator(k, v)
            
    def _get_parentbag(self):
        return self._parentbag
            #return self._parentbag()
            
    def _set_parentbag(self, parentbag):
        self._parentbag = None
        if parentbag != None:
            if parentbag.backref or True:
                #self._parentbag=weakref.ref(parentbag)
                self._parentbag = parentbag
                if hasattr(self._value,'_htraverse') and parentbag.backref:
                    self._value.setBackRef(node=self, parent=parentbag)

    parentbag = property(_get_parentbag, _set_parentbag)

    def _get_fullpath(self):
        if not self.parentbag is None:
            fullpath = self.parentbag.fullpath
            if not fullpath is None:
                return '%s.%s' % (fullpath, self.label)

    fullpath = property(_get_fullpath)

    def getLabel(self):
        """Return the node's label"""
        return self.label

    def setLabel(self, label):
        """Set node's label"""
        self.label = label

    def getValue(self, mode=''):
        """Return the value of the BagNode. It is called by the property .value
            
        :param mode='static': allow to get the resolver instance instead of the calculated value
        :param mode='weak': allow to get a weak ref stored in the node instead of the actual object"""
        if not self._resolver == None:
            if 'static' in mode:
                return self._value
            else:
                if self._resolver.readOnly:
                    return self._resolver() # value is not saved in bag, eventually is cached by resolver or lost
                if self._resolver.expired: # check to avoid triggers if value unchanged
                    self.value = self._resolver() # this may be a deferred
                return self._value
        return self._value
    
    def getFormattedValue(self,joiner=None,omitEmpty=True,mode='',**kwargs):
        v = self.getValue(mode=mode)
        if isinstance(v,Bag):
            v = v.getFormattedValue(joiner=joiner,omitEmpty=omitEmpty,mode=mode,**kwargs)
        else:
            v = self.attr.get('_formattedValue') or self.attr.get('_displayedValue') or v
        if v or not omitEmpty:
            return '%s: %s' %((self.attr.get('_valuelabel') or self.attr.get('name_long') or self.label.capitalize()),v)
        return ''

    def setValue(self, value, trigger=True, _attributes=None, _updattr=None, _removeNullAttributes=True):
        """Set the node's value, unless the node is locked. This method is called by the property .value
        
        :param value: the value to set the new bag inherits the trigger of the parentBag and calls it sending an update event
        :param trigger: boolean. TODO
        """
        if self.locked:
            raise BagNodeException("Locked node %s" % self.label)
        if isinstance(value, BagNode):
            _attributes = _attributes or {}
            _attributes.update(value.attr)
            value = value._value
        if hasattr(value, '_htraverse'):
            rootattributes = value.rootattributes
            if rootattributes:
                _attributes = dict(_attributes or {})
                _attributes.update(rootattributes)
        oldvalue = self._value
        if self._validators:
            self._value = self._validators(value, oldvalue)
        else:
            self._value = value
        trigger = trigger and (oldvalue != self._value) # we have to check also attributes change
        evt = 'upd_value'
        if _attributes != None:
            evt = 'upd_value_attr'
            self.setAttr(_attributes, trigger=False, _updattr=_updattr,
                         _removeNullAttributes=_removeNullAttributes)
        if trigger:
            for subscriber in self._node_subscribers.values():
                subscriber(node=self, info=oldvalue, evt='upd_value')
        if self.parentbag != None and self.parentbag.backref:
            if hasattr(value,'_htraverse'):
                value.setBackRef(node=self, parent=self.parentbag)
            if trigger:
                self.parentbag._onNodeChanged(self, [self.label],
                                              oldvalue=oldvalue, evt=evt)

    value = property(getValue, setValue)

    def getStaticValue(self):
        """Get node's value in static mode"""
        return self.getValue('static')
        
    def setStaticValue(self, value):
        """Set node's value in static mode"""
        self._value = value
        
    staticvalue = property(getStaticValue, setStaticValue)
        
    def _set_resolver(self, resolver):
        """Set a resolver in the node"""
        if not resolver is None:
            resolver.parentNode = self
        self._resolver = resolver
        
    def _get_resolver(self):
        """Get node's resolver
        """
        return self._resolver
        
    resolver = property(_get_resolver, _set_resolver)
        
    def resetResolver(self):
        """TODO"""
        self._resolver.reset()
        self.setValue(None)
        
    def getAttr(self, label=None, default=None):
        """It returns the value of an attribute. You have to specify the attribute's label.
        If it doesn't exist then it returns a default value
        
        :param label: the attribute's label that should be get
        :param default: the default return value for a not found attribute"""
        if not label or label == '#':
            return self.attr
        return self.attr.get(label, default)
        
    def getInheritedAttributes(self):
        """TODO"""
        inherited = {}
        if self.parentbag:
            if self.parentbag.parentNode:
                inherited = self.parentbag.parentNode.getInheritedAttributes()
        inherited.update(self.attr)
        return inherited
        
    @property
    def parentNode(self):
        if self.parentbag:
            return self.parentbag.parentNode
    
    def attributeOwnerNode(self,attrname,**kwargs):
        curr = self;
        if not 'attrvalue' in kwargs:
            while curr and not (attrname in curr.attr):
                curr = curr.parentNode
        else:
            attrvalue = kwargs['attrvalue']
            while curr and curr.attr[attrname]!=attrvalue:
                curr = curr.parentNode
        return curr
        
    def hasAttr(self, label=None, value=None):
        """Check if a node has the given pair label-value in its attributes' dictionary"""
        if not label in self.attr: return False
        if value: return (self.attr[label] == value)
        return True
        
    def setAttr(self, attr=None, trigger=True, _updattr=True, _removeNullAttributes=True, **kwargs):
        """It receives one or more key-value couple, passed as a dict or as named parameters,
        and sets them as attributes of the node.
            
        :param attr: the attribute that should be set into the node
        :param trigger: TODO
        """
        if not _updattr:
            self.attr.clear()
            #if self.locked:
            #raise BagNodeException("Locked node %s" % self.label)
        if self._node_subscribers and trigger:
            oldattr = dict(self.attr)
        if attr:
            self.attr.update(attr)
        if kwargs:
            self.attr.update(kwargs)
        if _removeNullAttributes:
            [self.attr.__delitem__(k) for k, v in self.attr.items() if v == None]

        if trigger:
            if self._node_subscribers:
                upd_attrs = [k for k in self.attr.keys() if (k not in oldattr.keys() or self.attr[k] != oldattr[k])]
                for subscriber in self._node_subscribers.values():
                    subscriber(node=self, info=upd_attrs, evt='upd_attrs')
            if self.parentbag != None and self.parentbag.backref:
                self.parentbag._onNodeChanged(self, [self.label], evt='upd_attrs')

    def delAttr(self, *attrToDelete):
        """Receive one or more attributes' labels and remove them from the node's attributes"""
        if isinstance(attrToDelete, basestring):
            attrToDelete = attrToDelete.split(',')
        for attr in attrToDelete:
            if attr in self.attr.keys():
                self.attr.pop(attr)

    def __str__(self):
        return 'BagNode : %s' % self.label

    def __repr__(self):
        return 'BagNode : %s at %i' % (self.label, id(self))

    def asTuple(self):
        """TODO"""
        return (self.label, self.value, self.attr, self.resolver)

    def addValidator(self, validator, parameterString):
        """Set a new validator into the BagValidationList of the node.
        If there are no validators into the node then addValidator instantiate
        a new BagValidationList and append the validator to it
        
        :param validator: the type of validation to set into the list of the node
        :param parameterString: the parameter for a single validation type"""
        if self._validators is None:
            self._validators = BagValidationList(self)
        self._validators.add(validator, parameterString)

    def removeValidator(self, validator):
        """TODO"""
        if not self._validators is None:
            self._validators.remove(validator)

    def getValidatorData(self, validator, label=None, dflt=None):
        """TODO"""
        if not self._validators is None:
            return self._validators.getdata(validator, label=label, dflt=dflt)

    def subscribe(self, subscriberId, callback):
        """TODO
        
        :param subscriberId: TODO
        :param callback: TODO"""
        self._node_subscribers[subscriberId] = callback

    def unsubscribe(self, subscriberId):
        """TODO"""
        self._node_subscribers.pop(subscriberId)
        
#-------------------- Class Bag --------------------------------
class Bag(GnrObject):
    """A container object like a dictionary, but ordered.
    
    Nested elements can be accessed with a path of keys joined with dots"""
    #-------------------- __init__ --------------------------------
    def __init__(self, source=None,**kwargs):
        """ A new bag can be created in various ways:
        
        * parsing a local file, a remote url or a text string (see fromXml)
        * converting a dictionary into a Bag
        * passing a list or a tuple just like for the builtin dict() command"""
        GnrObject.__init__(self)
        self._nodes = []
        self._backref = False
        self._node = None
        self._parent = None
        self._symbols = None
        self._upd_subscribers = {}
        self._ins_subscribers = {}
        self._del_subscribers = {}
        self._modified = None
        self._rootattributes = None
        source=source or kwargs
        if source:
            self.fillFrom(source)
                    
    def _get_parent(self):
        return self._parent
        
    def _set_parent(self, parent):
        if parent is None:
            self._parent = None
        else:
            #self._parent=weakref.ref(parent)
            self._parent = parent

    parent = property(_get_parent, _set_parent)

    def _get_fullpath(self):
        if self.parent != None:
            parentFullPath = self.parent.fullpath
            if parentFullPath:
                return '%s.%s' % (self.parent.fullpath, self.parentNode.label)
            else:
                return self.parentNode.label

    fullpath = property(_get_fullpath)

    def _set_node(self, node):
        raise BagDeprecatedCall('Deprecated syntax', 'use .parentNode instead of .node')
        if node != None:
            self._parentNode = node
            #self._parentNode = weakref.ref(node)
        else:
            self._parentNode = None

    def _get_node(self):
        raise BagDeprecatedCall('Deprecated syntax', 'use .parentNode instead of .node')
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
        return getattr(self,'_parentNode', None)
        return self._parentNode
            #return self._parentNode()

    parentNode = property(_get_parentNode, _set_parentNode)

    def _get_attributes(self):
        return self.parentNode.getAttr() if self.parentNode else dict()

    attributes = property(_get_attributes)

    def _get_rootattributes(self):
        return self._rootattributes

    def _set_rootattributes(self, attrs):
        self._rootattributes = dict(attrs)

    rootattributes = property(_get_rootattributes, _set_rootattributes)

    def _get_modified(self):
        return self._modified

    def _set_modified(self, value):
        if value == None:
            self._modified = None
            self.unsubscribe('modify__', any=True)
        else:
            if self._modified == None:
                self.subscribe('modify__', any=self._setModified)
            self._modified = value

    modified = property(_get_modified, _set_modified)

    def _setModified(self, **kwargs):
        self._modified = True

    #-------------------- __contains__ --------------------------------
    def __contains__(self, what):
        """The "in" operator can be used to test the existence of a key in a
        bag. Also nested keys are allowed. Return ``True`` if the key exists
        in the Bag, ``False`` otherwise
        
        :param what: the key path to test"""
        if isinstance(what, basestring):
            return bool(self.getNode(what))
        elif isinstance(what, BagNode):
            return (what in self._nodes)
        else:
            return False

    #-------------------- getItem --------------------------------
    def getItem(self, path, default=None, mode=None):
        """Return the value of the given item if it is in the Bag, else it returns ``None``,
        so that this method never raises a ``KeyError``
        
        This method reimplements the list's __getitem__() method. Usually a path is a string
        formed by the labels of the nested items, joined by the char '.', but several different
        path notations have been implemented to offer some useful features:
        
        * if a path segment who starts with '#' is followed by a number, the item will by identified
          by its index position, as a list element
        * if a path ends with '.?', it returns the item's keys
        * if at the last path-level the label contains '#', what follows the '#' is considered the
          key of an item's attribute and this method will return that attribute's value
        * if a path starts with '?', then it is interpreted as a digest method
        
        A path can also be a list of keys
        
        :param path: the item's path
        :param default: the default return value for a not found item
        :param mode='static': with this attribute the getItem doesn't solve the Bag :ref:`bag_resolver`
        
        >>> mybag = Bag()
        >>> mybag.setItem('a',1)
        >>> first= mybag.getItem('a')
        >>> second = mybag.getItem('b')
        >>> print(first,second)
        (1, None)
        
        >>> b = Bag()
        >>> b['aa.bb.cc'] = 1234
        >>> b['aa.bb.cc']
        1234
        
        **Square-brackets notations:**
        
        >>> mybag = Bag({'a':1,'b':2})
        >>> second = mybag['b']
        >>> print second
        2"""
        if not path:
            return self
        if isinstance(path, basestring):
            if '?' in path:
                path, mode = path.split('?')
                if mode == '': mode = 'k'
        obj, label = self._htraverse(path)
        if isinstance(obj, Bag):
            return obj.get(label, default, mode=mode)
        if hasattr(obj, 'get'):
            value = obj.get(label, default)
            return value
        else:
            return default
            
    __getitem__ = getItem
        
    def setdefault(self, path, default=None):
        """If *path* is in the Bag, return its value. If not, insert in the *path* the default value
        and return it. Default defaults to ``None``"""
        node = self.getNode(path)
        if not node:
            self[path] = default
        else:
            return node.value
            
    def toTree(self, group_by, caption=None, attributes="*"):
        """It transforms a flat Bag into a hierarchical Bag and returns it.
        
        :param group_by: list of keys
        :param caption: the attribute to use for the leaf key. If not specified, it uses the original key
        :param attributes: keys to copy as attributes of the leaves. Default value
                           is ``*`` (= select all the attributes)"""
        #if isinstance(group_by, str) or isinstance(group_by, unicode): 
        # just test if is instance of basestring 
        # both str and unicode will return True
        if isinstance(group_by, basestring):
            group_by = group_by.split(',')
        result = Bag()
        for key, item in self.iteritems():
            path = []
            for g in group_by:
                path.append(unicode(item[g]))
            if caption is None:
                val = key
            else:
                val = item[caption]
            path.append(unicode(val).replace(u'.', u'_'))
            if attributes == '*':
                attributes = item.keys()
            attrs = dict([(k, item[k]) for k in attributes])
            result.addItem('.'.join(path), None, attrs)
        return result
        
    def sort(self, pars='#k:a'):
        """TODO
        
        :param pars: TODO None: label ascending"""
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
                if what == '#k':
                    self._nodes.sort(lambda a, b: cmp(a.label.lower(), b.label.lower()), reverse=reverse)
                elif what == '#v':
                    self._nodes.sort(lambda a, b: cmp(a.value, b.value), reverse=reverse)
                elif what.startswith('#a'):
                    attrname = what[3:]
                    self._nodes.sort(lambda a, b: cmp(a.getAttr(attrname), b.getAttr(attrname)), reverse=reverse)
                else:
                    self._nodes.sort(lambda a, b: cmp(a.value[what], b.value[what]), reverse=reverse)
        return self
        
    def sum(self, what='#v'):
        """TODO
        
        :param what: TODO"""
        if ',' in what:
            result = []
            wlist = what.split(',')
            for w in wlist:
                result.append(sum(map(lambda n: n or 0, self.digest(w))))
            return result
        else:
            return sum(map(lambda n: n or 0, self.digest(what)))
            
    def get(self, label, default=None, mode=None):
        """TODO
        
        :param label: the :ref:`bag`'s label
        :param default: TODO
        :param mode: TODO"""
        result = None
        currnode = None
        currvalue = None
        attrname = None
        if not label:
            currnode = self.parentNode
            currvalue = self
        elif label == '#^':
            currnode = self.parent.parentNode
        else:
            if '?' in label:
                label, attrname = label.split('?')
            i = self._index(label)
            if i < 0:
                return default
            else:
                currnode = self._nodes[i]
        if currnode:
            if attrname:
                currvalue = currnode.getAttr(attrname)
            else:
                currvalue = currnode.getValue()
        if not mode:
            result = currvalue
        else:
            cmd = mode.lower()
            if not ':' in cmd:
                result = currnode.getAttr(mode)
            else:
                if cmd == 'k:':
                    result = currvalue.keys()
                elif cmd.startswith('d:') or cmd.startswith('digest:'):
                    result = currvalue.digest(mode.split(':')[1])
        return result
        
    def _htraverse(self, pathlist, autocreate=False, returnLastMatch=False):
        """Receive a hierarchical path as a list and execute one step of the path,
        calling itself recursively. If autocreate mode is ``True``, the method creates all
        the not existing nodes of the pathlist. Return the current node's value
        
        :param pathlist: list of nodes' labels
        :param autocreate: boolean. If ``True``, it creates all the not existing nodes of the pathlist
        :param returnLastMatch: boolean. TODO"""
        curr = self
        if isinstance(pathlist, basestring):
            orpa=pathlist
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
        i = curr._index(label)
        if i < 0:
            if autocreate:
                if label.startswith('#'):
                    raise BagException('Not existing index in #n syntax')
                i = len(curr._nodes)
                newnode = BagNode(curr, label=label, value=curr.__class__())
                curr._nodes.append(newnode)
                if self.backref:
                    self._onNodeInserted(newnode, i)
            elif returnLastMatch:
                return self.parentNode, '.'.join([label] + pathlist)
            else:
                return None, None
        newcurrnode = curr._nodes[i]
        newcurr = newcurrnode.value #maybe a deferred
        # if deferred : 
        #return deferred.addcallback(this.getItem(path rimanente))
        isbag = hasattr(newcurr, '_htraverse')
        if autocreate and not isbag:
            newcurr = curr.__class__()
            self._nodes[i].value = newcurr
            #curr.__setValue(i,newcurr)
            isbag = True
        if isbag:
            return newcurr._htraverse(pathlist, autocreate=autocreate, returnLastMatch=returnLastMatch)
        else:
            if returnLastMatch:
                return newcurrnode, '.'.join(pathlist)
            return newcurr, '.'.join(pathlist)

    def __iter__(self):
        return self._nodes.__iter__()

    def __len__(self):
        return len(self._nodes)
    
 
    def __call__(self, what=None):
        if not what:
            return self.keys()
        return self[what]
        
    def __pow__(self,kwargs):
        if self.parentNode:
            self.parentNode.attr.update(kwargs)
    #-------------------- __str__ --------------------------------
    def __str__(self, exploredNodes=None, mode='static,weak'):
        """Return a formatted representation of the bag contents"""
        if not exploredNodes:
            exploredNodes = {}
        outlist = []
        for idx, el in enumerate(self._nodes):
            attr = '<' + ' '.join(["%s='%s'" % attr for attr in el.attr.items()]) + '>'
            if attr == '<>': attr = ''
            try:
                value = el.getValue(mode)
            except:
                value = '****  error ****'
            if isinstance(value, Bag):
                el_id = id(el)
                outlist.append(("%s - (%s) %s: %s" %
                                (str(idx), value.__class__.__name__, el.label, attr)))
                if el_id in exploredNodes:
                    innerBagStr = 'visited at :%s' % exploredNodes[el_id]
                else:
                    exploredNodes[el_id] = el.label
                    innerBagStr = '\n'.join(["    %s" % (line,)
                                             for line in unicode(
                            value.__str__(exploredNodes, mode=mode)).split('\n')])
                outlist.append(innerBagStr)
            else:
                currtype = str(type(value)).split(" ")[1][1:][:-2]
                if currtype == 'NoneType': currtype = 'None'
                if '.' in currtype: currtype = currtype.split('.')[-1]
                if not isinstance(value, unicode):
                    if isinstance(value, basestring):
                        value = value.decode('UTF-8', 'ignore')
                outlist.append(("%s - (%s) %s: %s  %s" % (str(idx), currtype,
                                                          el.label, unicode(value), attr)))
        return '\n'.join(outlist)

    def asString(self, encoding='UTF-8', mode='weak'):
        """Call the __str__ method, and return an ascii encoded formatted representation of the Bag
        
        :param encoding: the encoding type
        :param mode: TODO"""
        return self.__str__(mode=mode).encode(encoding, 'ignore')
    
    def getFormattedValue(self,joiner='\n',omitEmpty=True,**kwargs):
        r = []
        for n in self:
            if not n.label.startswith('_'):
                fv = n.getFormattedValue(joiner=joiner,omitEmpty=omitEmpty,**kwargs)
                if fv or not omitEmpty:
                    r.append(fv)
        return joiner.join(r)


    def keys(self):
        """Return a copy of the Bag as a list of keys
        
        >>> b = Bag({'a':1,'a':2,'a':3})
        >>> b.keys()
        ['a', 'c', 'b']"""
        return [x.label for x in self._nodes]

    def values(self):
        """Return a copy of the Bag values as a list"""
        return [x.value for x in self._nodes]

    def items(self):
        """Return a copy of the Bag as a list of tuples containing all key,value pairs
        
        >>> b = Bag({'a':1,'b':2,'c':3})
        >>> b.items()
        [('a', 1), ('c', 3), ('b', 2)]"""
        return [(x.label, x.value) for x in self._nodes]
        
    def iteritems(self):
        """TODO"""
        for x in self._nodes:
            yield (x.label, x.value)
            
    def iterkeys(self):
        """TODO"""
        for x in self._nodes:
            yield x.label
            
    def itervalues(self):
        """TODO"""
        for x in self._nodes:
            yield x.value
            
    def digest(self, what=None, condition=None, asColumns=False):
        """It returns a list of ``n`` tuples including keys and/or values and/or attributes of all the Bag's elements,
        where ``n`` is the number of *special keys* called in the method
            
        :param what: the parameter who includes a string of one or more special keys separated by a comma
        
        Here follows a list of the *special keys*:
            
            +------------------------+----------------------------------------------------------------------+
            |  *Special keys*        |  Description                                                         |
            +========================+======================================================================+
            | ``'#k'``               | Show the label of each item                                          |
            +------------------------+----------------------------------------------------------------------+
            | ``'#v'``               | Show the value of each item                                          |
            +------------------------+----------------------------------------------------------------------+
            | ``'#v.path'``          | Show inner values of each item                                       |
            +------------------------+----------------------------------------------------------------------+
            | ``'#__v'``             | Show the values of each node in 'static' mode  ???                   |
            +------------------------+----------------------------------------------------------------------+
            | ``'#a'``               | Show attributes of each item                                         |
            +------------------------+----------------------------------------------------------------------+
            | ``'#a.attributeName'`` | Show the attribute called 'attrname' for each item                   |
            +------------------------+----------------------------------------------------------------------+
            
        :param condition: set a :ref:`sql_condition` for digest process
        :param asColumns: TODO
            
            >>> b=Bag()
            >>> b.setItem('documents.letters.letter_to_mark','file0',createdOn='10-7-2003',createdBy= 'Jack')
            >>> b.setItem('documents.letters.letter_to_john','file1',createdOn='11-5-2003',createdBy='Mark',
            ... lastModify='11-9-2003')
            >>> b.setItem('documents.letters.letter_to_sheila','file2')
            >>> b.setAttr('documents.letters.letter_to_sheila',createdOn='12-4-2003',createdBy='Walter',
            ... lastModify='12-9-2003',fileOwner='Steve')
            >>> print b['documents.letters'].digest('#k,#a.createdOn,#a.createdBy')
            [('letter_to_sheila','12-4-2003','Walter'),('letter_to_mark','10-7-2003','Jack'),('letter_to_john','11-5-2003','Mark')]
            
        **Square-brackets notations:**
        
        You have to use the special char ``?`` followed by ``d:`` followed by one or more *expressions*:
            
            >>> print b['documents.letters.?d:#k,#a.createdOn,#a.createdBy']
            [('letter_to_sheila','12-4-2003','Walter'),('letter_to_mark','10-7-2003','Jack'),('letter_to_john','11-5-2003','Mark')]
            >>> print b['documents.letters.?d:#v,#a.createdOn']
            [('file0', '10-7-2003'), ('file1', '11-5-2003'), ('file2', '12-4-2003')]"""

        if not what:
            what = '#k,#v,#a'
        if isinstance(what, basestring):
            if ':' in what:
                where, what = what.split(':')
                obj = self[where]
            else:
                obj = self
            whatsplit = [x.strip() for x in what.split(',')]
        else:
            whatsplit = what
            obj = self
        result = []
        nodes = obj.getNodes(condition)
        for w in whatsplit:
            if w == '#k':
                result.append([x.label for x in nodes])
            elif callable(w):
                result.append([w(x) for x in nodes])
            elif w == '#v':
                result.append([x.value for x in nodes])
            elif w.startswith('#v.'):
                w, path = w.split('.', 1)
                result.append([x.value[path] for x in nodes if hasattr(x.value, 'getItem')])
            elif w == '#__v':
                result.append([x.staticvalue for x in nodes])
            elif w.startswith('#a'):
                attr = None
                if '.' in w:
                    w, attr = w.split('.', 1)
                if w == '#a':
                    result.append([x.getAttr(attr) for x in nodes])
            else:
                result.append([x.value[w] for x in nodes])
        if asColumns:
            return result
        if len(result) == 1:
            return result.pop()
        return zip(*result)
        
    def columns(self, cols, attrMode=False):
        """TODO
        
        :param cols: TODO
        :param attrMode: boolean. TODO"""
        if isinstance(cols, basestring):
            cols = cols.split(',')
        mode = ''
        if attrMode:
            mode = '#a.'
        what = ','.join(['%s%s' % (mode, col) for col in cols])
        return self.digest(what, asColumns=True)

    def has_key(self, path):
        """This method is analog to dictionary's has_key() method. Seek for the presence of the key
        in the Bag, and return ``True`` if the given item has the key, ``False`` otherwise
        
        :param path: the path of the given item
        
        >>> b = Bag({'a':1,'b':2,'c':3})
        >>> b.has_key('a')
        True
        >>> b.has_key('abc')
        False"""
        return bool(self.getNode(path))

    def getNodes(self, condition=None):
        """Get the actual list of nodes contained in the Bag.
        The getNodes method works as the filter of a list"""
        if not condition:
            return self._nodes
        else:
            return [n for n in self._nodes if condition(n)]

    nodes = property(getNodes)

    def popNode(self, path):
        """This method is analog to dictionary's pop() method. It pops the given node from
        a Bag at the relative path and returns it
        
        :param path: path of the given node"""
        obj, label = self._htraverse(path)
        if obj:
            n = obj._pop(label)
            if n:
                return n

    def pop(self, path, dflt=None):
        """This method is analog to dictionary's pop() method. It pops the given item from
        a Bag at the relative path and returns it
        
        :param path: path of the given item
        :param dflt: TODO
        
        >>> b = Bag()
        >>> b.setItem('a',1)
        >>> b.addItem('a',2)
        >>> b.addItem('a',3)
        >>> b.pop('a')
        1
        >>> print b
        0 - (int) a: 2
        1 - (int) a: 3"""
        result = dflt
        obj, label = self._htraverse(path)
        if obj:
            n = obj._pop(label)
            if n:
                result = n.value
        return result
        
    # the following means __delitem__ is the same as pop
    delItem = pop
    __delitem__ = pop
        
    def _pop(self, label):
        """bag.pop(key)"""
        p = self._index(label)
        if p >= 0:
            node = self._nodes.pop(p)
            if self.backref:
                self._onNodeDeleted(node, p)
            return node

        #-------------------- clear --------------------------------

    def clear(self):
        """Clear the Bag"""
        oldnodes = self._nodes
        self._nodes = []
        if self.backref:
            self._onNodeDeleted(oldnodes, -1)

    def update(self, otherbag, resolved=False):
        """Update the Bag with the ``key/value`` pairs from *otherbag*,
        overwriting all the existing keys. Return ``None``
        
        :param otherbag: the Bag to merge into
        :param resolved: TODO"""
        if isinstance(otherbag, dict):
            for k, v in otherbag.items():
                self.setItem(k, v)
            return
        if isinstance(otherbag, basestring):
            cls = self.__class__
            b = Bag()
            b.fromXml(otherbag, bagcls=cls, empty=cls)
            otherbag = b
        for n in otherbag:
            node_resolver = n.resolver
            node_value = None
            if node_resolver is None or resolved:
                node_value = n.value
                node_resolver = None
            if n.label in self.keys():
                currNode = self.getNode(n.label)
                currNode.attr.update(n.attr)
                if node_resolver is not None:
                    currNode.resolver = node_resolver
                if isinstance(node_value, Bag) and  isinstance(currNode.value, Bag):
                    currNode.value.update(node_value)
                else:
                    currNode.value = node_value
            else:
                self.setItem(n.label, node_value, n.attr)

    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__):
                return self._nodes == other._nodes
            else:
                return False
        except:
            return False

    def __getstate__(self):
        result = dict(self.__dict__)
        for k in ('_upd_subscribers','_del_subscribers','_ins_subscribers'):
            result[k] = {}
        result['_parent'] = None
        result['_parentNode'] = None
        return result



    def merge(self, otherbag, upd_values=True, add_values=True, upd_attr=True, add_attr=True):
        """.. warning:: deprecated since version 0.7
        
        Allow to merge two bags into one
        
        >>> john_doe=Bag()
        >>> john_doe['telephones']=Bag()
        >>> john_doe['telephones.house']=55523412
        >>> other_numbers=Bag({'mobile':444334523, 'office':3320924, 'house':2929387})
        >>> other_numbers.setAttr('office',{'from': 9, 'to':17})
        >>> john_doe['telephones']=john_doe['telephones'].merge(other_numbers)
        >>> print john_doe
        0 - (Bag) telephones:
            0 - (int) house: 2929387
            1 - (int) mobile: 444334523
            2 - (int) office: 3320924  <to='17' from='9'>
        >>> john_doe['credit_cards']=Bag()"""
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
                    attr = dict([(ak, oattr.get(ak, av)) for ak, av in attr.items()])
                elif add_attr:
                    oattr = dict([(ak, av) for ak, av in oattr.items() if not ak in attr.keys()])
                    attr.update(oattr)
                ov = onode.getValue()
                if isinstance(v, Bag) and isinstance(ov, Bag):
                    v = v.merge(ov, upd_values=upd_values, add_values=add_values, upd_attr=upd_attr, add_attr=add_attr)
                elif upd_values:
                    v = ov
            result.setItem(k, v, _attributes=attr)
        if add_values:
            for k, n in othernodes.items():
                result.setItem(k, n.getValue(), _attributes=n.getAttr())
        return result

    #-------------------- copy --------------------------------
    def copy(self):
        """Return a Bag copy"""
        return copy.copy(self)

    #-------------------- deepcopy -------------------------------
    def deepcopy(self):
        """Return a deep Bag copy"""
        result = Bag()
        for node in self:
            value = node.getStaticValue()
            if isinstance(value, Bag):
                value = value.deepcopy()
            result.setItem(node.label, value, dict(node.getAttr()))
        return result

    #-------------------- getNodeByAttr --------------------------------
    def getNodeByAttr(self, attr, value, path=None):
        """Return a BagNode with the requested attribute (e.g. searching a node
        with a given 'id' in a Bag build from html)
        
        :param attr: path of the given item
        :param value: path of the given item
        :param path:  an empty list that will be filled with the path of the found node"""
        bags = []
        if path == None: path = []
        for node in self._nodes:
            if node.hasAttr(attr, value):
                path.append(node.label)
                return node
            if isinstance(node._value, Bag): bags.append(node)

        for node in bags:
            nl = [node.label]
            n = node._value.getNodeByAttr(attr, value, path=nl)
            if n:
                path.extend(nl)
                return n

    def getNodeByValue(self,label,value):
        result = None
        for n in self:
            if n.value and n.value[label] == value:
                result = n
                break
        return result

    def getDeepestNode(self, path=None):
        """Return the deepest matching node in the bag and the remaining path of the path.
        bag.getDeepestNode('foo.bar.baz') returns:
            
        >>> if 'foo.bar.baz' in bag:
        >>>     return (bag.getNode(foo.bar.baz), [])
        >>> elif 'foo.bar' in bag:
        >>>     return (bag.getNode('foo.bar'), ['baz'])
        >>> elif 'bar' in bag:
        >>>     return (bag.getNode(foo),['bar','baz'])
        >>> else:
        >>>     return (None,['foo','bar','baz'])"""
        node, tail_path = self._htraverse(path, returnLastMatch=True)
        if hasattr(node, '_htraverse'):
            node = node.getNode(tail_path)
            tail_path = ''
        if node:
            node._tail_list = []
            if tail_path:
                node._tail_list =  gnrstring.smartsplit(tail_path.replace('../', '#^.'), '.')
            return node
            #return None

    def getDeepestNode_(self, path=None):
        """This method returns the deepest matching node in the bag and the remaining path of the path.
        bag.getDeepestNode('foo.bar.baz') returns:
            
        >>> if 'foo.bar.baz' in bag:
        >>>     return (bag.getNode(foo.bar.baz), [])
        >>> elif 'foo.bar' in bag:
        >>>     return (bag.getNode('foo.bar'), ['baz'])
        >>> elif 'bar' in bag:
        >>>     return (bag.getNode(foo),['bar','baz'])
        >>> else:
        >>>     return (None,['foo','bar','baz'])"""
        result = self._htraverse(path, returnLastMatch=True)
        if hasattr(result[0], '_htraverse'):
            return result[0].getNode(result[1]), ''
        return result

    #-------------------- getNode --------------------------------
    def getNode(self, path=None, asTuple=False, autocreate=False, default=None):
        """Return the BagNode stored at the relative path
        
        :param path: path of the given node
        :param asTuple: boolean. If ``True``, return a tuple with the object and the node
        :param autocreate: boolean. If ``True``, it creates all the not existing nodes of the pathlist
        :param default: the default return value for a not found node"""
        if not path:
            return self.parentNode
        if isinstance(path, int):
            return self._nodes[path]
        obj, label = self._htraverse(path, autocreate=autocreate)

        if isinstance(obj, Bag):
            node = obj._getNode(label, autocreate, default)
            if asTuple:
                return (obj, node)
            return node

    def _getNode(self, label, autocreate, default):
        p = self._index(label)
        if p >= 0:
            node = self._nodes[p]
        elif autocreate:
            node = BagNode(self, label=label, value=default)
            i = len(self._nodes)
            self._nodes.append(node)
            node.parentbag = self
            if self.backref:
                self._onNodeInserted(node, i)

        else:
            node = None
        return node

    def setAttr(self, _path=None, _attributes=None, _removeNullAttributes=True, **kwargs):
        """Allow to set, modify or delete attributes into a node at the given path
        
        You can set the attributes into a Bag with the `_attributes` parameter if
        you have a dict of attributes; alternatively, you can pass all the attributes as **kwargs.
        
        >>> b = Bag()
        >>> b.setAttr('documents.letters.letter_to_sheila', createdOn='12-4-2003', createdBy='Walter', lastModify= '12-9-2003')
        >>> b.setAttr('documents.letters.letter_to_sheila', fileOwner='Steve')
        >>> b.setAttr('documents',{'type':'secret','createdOn':'2010-11-15'})
        >>> print b
        0 - (Bag) documents: <createdOn='2010-11-15' type='secret'>
            0 - (Bag) letters: 
                0 - (str) letter_to_mark: file0  <createdOn='10-7-2003' createdBy='Jack'>
                1 - (str) letter_to_john: file1  <lastModify='11-9-2003' createdOn='11-5-2003' createdBy='Mark'>
                2 - (str) letter_to_sheila: file2  <lastModify='12-9-2003' createdOn='12-4-2003' fileOwner='Steve' createdBy='Walter'>
        
        You may delete an attribute assigning ``None`` to an existing value:
        
        >>> b.setAttr('documents.letters.letter_to_sheila', fileOwner=None, createdOn=None, createdBy=None)
        >>> print b
        0 - (Bag) documents: <createdOn='2010-11-15' type='secret'>
            0 - (Bag) letters:
                0 - (str) letter_to_sheila: file2  <lastModify='12-9-2003'>
        """
        self.getNode(_path, autocreate=True).setAttr(attr=_attributes, _removeNullAttributes=_removeNullAttributes,
                                                     **kwargs)

    def getAttr(self, path=None, attr=None, default=None):
        """Get the node's attribute at the given path and return it. If it doesn't exist, it returns ``None``,
        so that this method never raises a ``KeyError``
            
        :param path: path of the given item
        :param attr: the label of the attribute to get
        :param default: the value returned by this method for an unexisting attribute
        
        >>> b = Bag()
        >>> b.setItem('documents.letters.letter_to_mark','file0',createdOn='10-7-2003',createdBy= 'Jack')
        >>> print b
        0 - (Bag) documents: 
            0 - (Bag) letters: 
                0 - (str) letter_to_mark: file0  <createdOn='10-7-2003' createdBy='Jack'>
        >>> print b.getAttr('documents.letters.letter_to_mark', 'createdBy')
        Jack
        >>> print b.getAttr('documents.letters.letter_to_mark', 'fileOwner')
        None
        >>> print b.getAttr('documents.letters.letter_to_mark', 'fileOwner', default='wrong')
        wrong
        
        **Square-brackets notations:**
        
        You have to use the special char ``?`` followed by the attribute's name:
        
        >>> print b['documents.letters.letter_to_sheila?fileOwner']
        Steve"""
        node = self.getNode(path)
        if node:
            return node.getAttr(label=attr, default=default)
        else:
            return default

    def delAttr(self, path=None, attr=None):
        """TODO
        
        :param path: the path of the BagNode.
        :param attr: the name of the attribute to delete"""
        return self.getNode(path).delAttr(attr)
    
    def getInheritedAttributes(self):
        """TODO"""
        if self.parentNode:
            return self.parentNode.getInheritedAttributes()
        else:
            return dict()

    def _pathSplit(self, path):
        """Split a path string it at each '.' and return both a list of nodes' labels
        and the first list's element label.
        
        :param path: the given path"""
        if isinstance(path, basestring):
            escape = "\\."
            if escape in path:
                path = path.replace(escape, chr(1))
                pathList = path.split('.')
                pathList = [x.replace(chr(1), '.') for x in pathList]
            else:
                pathList = path.split('.')
        else:
            pathList = list(path)

        label = pathList.pop(0)
        return label, pathList

    def asDict(self, ascii=False, lower=False):
        """Convert a Bag in a Dictionary and return it.
        
        :param ascii: boolean. TODO
        :param lower: boolean. TODO
        
        .. note:: If you attempt to transform a hierarchical bag to a dictionary, the resulting dictionary will contain
                  nested bags as values. In other words only the first level of the Bag is transformed to a dictionary,
                  and the transformation is not recursive"""
        result = {}
        for el in self._nodes:
            key = el.label
            if ascii: key = str(key)
            if lower: key = key.lower()
            result[key] = el.value
        return result

    def asDictDeeply(self, ascii=False, lower=False):
        """TODO
        
        :param ascii: boolean. TODO
        :param lower: boolean. TODO"""
        d = self.asDict(ascii=ascii, lower=lower)
        for k, v in d.items():
            if isinstance(v, Bag):
                d[k] = v.asDictDeeply(ascii=ascii, lower=lower)
        return d

    #-------------------- addItem --------------------------------
    def addItem(self, item_path, item_value, _attributes=None, _position=">", _validators=None, **kwargs):
        """Add an item to the current Bag using a path in the form "label1.label2. ... .labelN", returning the current Bag.
        If the path already exists, this method replicates the path keeping both the old values and the new value
        
        :param item_path: the path of the given item
        :param item_value: the value to set
        :param _attributes: it specifies the attributes of the value to set
        :param _position: allow to set a new value at a particular position among its brothers
                          Default value is ``>``. You can use one of the following types:
                          
                              +----------------------------+----------------------------------------------------------------------+
                              | *Position's attributes*    |  Description                                                         |
                              +============================+======================================================================+
                              | ``'<'``                    | Set the value as the first value of the Bag                          |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'>'``                    | Set the value as the last value of the Bag                           |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'<label'``               | Set the value in the previous position respect to the labelled one   |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'>label'``               | Set the value in the position next to the labelled one               |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'<#index'``              | Set the value in the previous position respect to the indexed one    |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'>#index'``              | Set the value in the position next to the indexed one                |
                              +----------------------------+----------------------------------------------------------------------+
                              | ``'#index'``               | Set the value in a determined position indicated by ``index`` number |
                              +----------------------------+----------------------------------------------------------------------+
            
        :param _validators: it specifies the value's validators to set
        :param \*\*kwargs: attributes AND/OR validators
        
        Example:
        
        >>> beatles = Bag()
        >>> beatles.setItem('member','John')    # alternatively, you could write beatles.addItem('member','John')
        >>> beatles.addItem('member','Paul')
        >>> beatles.addItem('member','George')
        >>> beatles.addItem('member','Ringo')
        >>> print beatles
        0 - (str) member: John
        1 - (str) member: Paul
        2 - (str) member: George
        3 - (str) member: Ringo
        
        Obviously, you can't use the *square-brackets notations* within this method, because if you try to insert different
        values with the same label you would lose all the values except for the last one"""
        return self.setItem(item_path, item_value, _attributes=_attributes, _position=_position,
                            _duplicate=True, _validators=_validators, **kwargs)

    #-------------------- setItem --------------------------------
    def setItem(self, item_path, item_value, _attributes=None, _position=None, _duplicate=False,
                _updattr=False, _validators=None, _removeNullAttributes=True, **kwargs):
        """Set an item (values and eventually attributes) to your Bag using a path in the form
        ``label1.label2...labelN``. If path already exists, it overwrites the value at the given path.
        Return the Bag.
        
        The default behaviour of ``setItem()`` is to add the new value as the last element.
        You can change this trend with the *_position* argument, who provides a compact
        syntax to insert the element in the desired place
        
        :param item_path: the path of the given item
        :param item_value: the value to set
        :param _attributes:  it specified, the value's attributes to set
        :param _position: it is possible to set a new value at a particular position among its brothers.
                          
                          *expression* must be a string of the following types:
                          
                          +----------------------------+----------------------------------------------------------------------+
                          | *Expressions*              |  Description                                                         |
                          +============================+======================================================================+
                          | ``'<'``                    | Set the value as the first value of the Bag                          |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'>'``                    | Set the value as the last value of the Bag                           |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'<label'``               | Set the value in the previous position respect to the labelled one   |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'>label'``               | Set the value in the position next to the labelled one               |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'<#index'``              | Set the value in the previous position respect to the indexed one    |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'>#index'``              | Set the value in the position next to the indexed one                |
                          +----------------------------+----------------------------------------------------------------------+
                          | ``'#index'``               | Set the value in a determined position indicated by ``index`` number |
                          +----------------------------+----------------------------------------------------------------------+
                          
        :param _duplicate: boolean. Specify if a node with an existing path overwrite the value or
                           append to it the new one
        :param _updattr: boolean. TODO
        :param _validators: specify the value's validators to set
        :param _removeNullAttributes: boolean. If ``True``, remove the null attributes
        :param \*\*kwargs: attributes AND/OR validators
        
        Example:
        
        >>> mybag = Bag()
        >>> mybag.setItem('a',1)
        >>> mybag.setItem('b',2)
        >>> mybag.setItem('c',3)
        >>> mybag.setItem('d',4)
        >>> mybag.setItem('e',5, _position= '<')
        >>> mybag.setItem('f',6, _position= '<c')
        >>> mybag.setItem('g',7, _position= '<#3')
        >>> print mybag
        0 - (int) e: 5
        1 - (int) a: 1
        2 - (int) b: 2
        3 - (int) g: 7
        4 - (int) f: 6
        5 - (int) c: 3
        6 - (int) d: 4
        
        **Square-brackets notations**::
        
            Bag[path] = value
        
        Example:
        
        >>> mybag = Bag()
        >>> mybag['a'] = 1
        >>> mybag['b.c.d'] = 2
        >>> print mybag
        0 - (int) a: 1
        1 - (Bag) b:
            0 - (Bag) c:
                0 - (int) d: 2
                
        .. note:: if you have to use the ``_position`` attribute you can't use the square-brackets notation"""

        if kwargs:
            _attributes = dict(_attributes or {})
            _validators = dict(_validators or {})
            for k, v in kwargs.items():
                if k.startswith('validate_'):
                    _validators[k[9:]] = v
                else:
                    _attributes[k] = v
        if item_path == '' or item_path is True:
            if isinstance(item_value, BagResolver):
                item_value = item_value()
            if isinstance(item_value, Bag):
                for el in item_value:
                    self.setItem(el.label, el.value, _attributes=el.attr, _updattr=_updattr)
                    if el._validators:
                        self.getNode(el.label)._validators = el._validators
            elif 'items' in dir(item_value):
                for key, v in item_value.items(): self.setItem(key, v)
            return self
        else:
            obj, label = self._htraverse(item_path, autocreate=True)
            obj._set(label, item_value, _attributes=_attributes, _position=_position,
                     _duplicate=_duplicate, _updattr=_updattr,
                     _validators=_validators, _removeNullAttributes=_removeNullAttributes)

    __setitem__ = setItem

    def _set(self, label, value, _attributes=None, _position=None,
             _duplicate=False, _updattr=False, _validators=None, _removeNullAttributes=True):
        resolver = None
        if isinstance(value, BagResolver):
            resolver = value
            value = None
            if resolver.attributes:
                _attributes = dict(_attributes or ()).update(resolver.attributes)
        i = self._index(label)
        if i < 0 or _duplicate:
            if label.startswith('#'):
                raise BagException('Not existing index in #n syntax')
            else:
                bagnode = BagNode(self, label=label, value=value, attr=_attributes,
                                  resolver=resolver, validators=_validators,
                                  _removeNullAttributes=_removeNullAttributes)
                self._insertNode(bagnode, _position)

        else:
            node = self._nodes[i]
            if resolver != None:
                node.resolver = resolver
            if _validators:
                node.setValidators(_validators)
            node.setValue(value, _attributes=_attributes, _updattr=_updattr,
                          _removeNullAttributes=_removeNullAttributes)

    def defineSymbol(self, **kwargs):
        """Define a variable and link it to a BagFormula Resolver at the specified path.
        
        :param kwargs: a dict of symbol to make a formula.
        
        >>> mybag=Bag({'rect': Bag()})
        >>> mybag['rect.params.base'] = 20
        >>> mybag['rect.params.height'] = 10
        >>> mybag.defineFormula(calculate_perimeter='2*($base + $height)' )
        >>> mybag.defineSymbol(base ='params.base',  height='params.height')
        >>> mybag['rect.perimeter']= mybag.formula('calculate_perimeter')
        >>> print mybag['rect.perimeter']
        60"""
        if self._symbols == None:
            self._symbols = {}
        self._symbols.update(kwargs)

    def defineFormula(self, **kwargs):
        """Define a formula that uses defined symbols
        
        :param kwargs: a key-value couple which represents the formula and the string that describes it"""
        if self._symbols == None:
            self._symbols = {}
        for key, value in kwargs.items():
            self._symbols['formula:%s' % key] = value

    def formula(self, formula, **kwargs):
        """Set a BagFormula resolver
        
        :param formula: a string that represents the expression with symbolic vars
        :param \*\*kwargs: links between symbols and paths associated to their values"""
        self.setBackRef()
        if self._symbols == None:
            self._symbols = {}
        formula = self._symbols.get('formula:%s' % formula, formula)
        parameters = dict(self._symbols)
        parameters.update(kwargs)
        return BagFormula(formula=formula, parameters=parameters)

    def getResolver(self, path):
        """This method get the resolver of the node at the given path
        
        :param path: the path of the node"""
        return self.getNode(path).getResolver()

    getFormula = getResolver

    def setResolver(self, path, resolver):
        """Set a resolver into the node at the given path
        
        :param path: the path of the node
        :param resolver: the resolver to set"""
        return self.setItem(path, None, resolver=resolver)

    def setBackRef(self, node=None, parent=None):
        """Force a Bag to a more strict structure. It makes the Bag similar to a
        tree-leaf model: a Bag can have only one Parent and it knows this reference
        
        :param node: the parent node
        :param parent: TODO"""
        if self._backref != True:
            self._backref = True
            self.parent = parent
            self.parentNode = node
            for node in self:
                node.parentbag = self #node property calls back setBackRef recursively

    def delParentRef(self):
        """Set ``False`` in the ParentBag reference of the relative Bag"""
        self.parent = None
        self._backref = False

    def clearBackRef(self):
        """Clear all the :meth:`setBackRef()` assumption"""
        if self._backref:
            self._backref = False
            self.parent = None
            self.parentNode = None
            for node in self:
                node.parentbag = None
                value = node.staticvalue
                if isinstance(value, Bag):
                    value.clearBackRef()

    def makePicklable(self):
        """Allow a Bag to be picklable"""
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
        """Restore a Bag from its picklable form to its original form"""
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

    backref = property(_get_backref)

    def _insertNode(self, node, position):
        if isinstance(position,int):
            n = position
        elif not (position) or position == '>':
            n = -1
        elif position == '<':
            n = 0
        elif position[0] == '#':
            n = int(position[1:])
        else:
            if position[0] in '<>':
                position, label = position[0], position[1:]
            else:
                position, label = '<', position
            if label[0] == '#':
                n = int(label[1:])
            else:
                n = self._index(label)
            if position == '>' and n >= 0:
                n = n + 1
        if n < 0:
            n = len(self._nodes)
        self._nodes.insert(n, node)
        node.parentbag = self
        if self.backref:
            self._onNodeInserted(node, n)
        return n

    #-------------------- index --------------------------------
    def _index(self, label):
        """Return the label position into a given Bag. It is not recursive, so it works just in the current level.
        The label can be '#n' where n is the position. The label can be '#attribute=value'.
        If the label doesn't exist it returns -1. The mach is not case sensitive
        
        :param label: a not hierarchical label"""
        result = -1
        if label.startswith('#'):
            if '=' in label:
                k, v = label[1:].split('=')
                if not k: k = 'id'
                for idx, el in enumerate(self._nodes):
                    if el.attr.get(k, None) == v:
                        result = idx
                        break
            else:
                idx = int(label[1:])
                if idx < len(self._nodes): result = idx

        else:
        #f=filter(lambda x: x[1].label==label, enumerate(self._nodes))
        #if len(f)>0:
        #result=f[0][0]
            for idx, el in enumerate(self._nodes):
                if el.label == label:
                    result = idx
                    break
        return result

    #-------------------- pickle --------------------------------
    def pickle(self, destination=None, bin=True):
        """Return a pickled Bag
        
        :param destination: it is the destination path; default is 'None'
        :param bin: boolean; if ``False`` the Bag will be pickled in ASCII code,
                             if ``True`` the Bag will be pickled in a binary format"""
        if not destination:
            return pickle.dumps(self, bin)
        if isinstance(destination, file):
            pickle.dump(self, destination, bin)
        else:
            destination = file(destination, mode='w')
            pickle.dump(self, destination, bin)
            destination.close()
            
        #-------------------- unpickle --------------------------------
        
    def unpickle(self, source):
        """Unpickle a pickled Bag
        
        :param source: the source path"""
        source, fromFile, mode = self._sourcePrepare(source)
        if source and mode == 'pickle':
            self[:] = self._unpickle(source, fromFile)
            
    def _unpickle(self, source, fromFile):
        if fromFile:
            source = file(source, mode='r')
            result = pickle.load(source)
            source.close()
        else:
            result = pickle.loads(source)
        return result
        
    def setCallable(self, name, argstring=None, func='pass'):
        """TODO
        
        :param name: TODO
        :param argstring: TODO
        :param func: TODO"""
        setCallable(self, name, argstring=argstring, func=func)
        
    #-------------------- toXml --------------------------------
    def toXml(self, filename=None, encoding='UTF-8', typeattrs=True, typevalue=True, unresolved=False,
              addBagTypeAttr=True,onBuildTag=None,
              autocreate=False, translate_cb=None, self_closed_tags=None,
              omitUnknownTypes=False, catalog=None, omitRoot=False, forcedTagAttr=None, docHeader=None,
              mode4d=False,pretty=False):
        """Return a complete standard XML version of the Bag, including the encoding
        tag <?xml version=\'1.0\' encoding=\'UTF-8\'?> (the *docHeader* default value)
        
        The content of the Bag is hierarchically represented as an XML block
        sub-element of the node <GenRoBag> (see the toXmlBlock() documentation
        for more details about type representation).
        Is also possible to write the result on a file, passing the path of the file
        as the 'filename' parameter.
        
        :param filename: the output file path
        :param encoding: set the XML encoding
        :param typeattrs: boolean. If ``True``, keep the attribute's types
        :param typevalue: boolean. If ``True``, keep the value's type
        :param unresolved: boolean. TODO
        :param addBagTypeAttr: boolean. TODO
        :param autocreate: boolean. If ``True``, it creates all the not existing nodes of the pathlist
        :param translate_cb: TODO
        :param self_closed_tags: TODO
        :param omitUnknownTypes: boolean. TODO
        :param catalog: TODO
        :param omitRoot: boolean. If ``False``, add the ``<GenRoBag>`` tag root
        :param forcedTagAttr: TODO
        :param docHeader: set an header tag external the ``<GenRoBag>`` tag
        
        >>> mybag=Bag()
        >>> mybag['aa.bb']=4567
        >>> mybag.toXml()
        '<?xml version=\'1.0\' encoding=\'iso-8859-15\'?>
        <GenRoBag>
        <aa><bb T="L">
        4567</bb></aa></GenRoBag>'"""
        from gnr.core.gnrbagxml import BagToXml
        
        return BagToXml().build(self, filename=filename, encoding=encoding, typeattrs=typeattrs, typevalue=typevalue,
                                addBagTypeAttr=addBagTypeAttr,onBuildTag=onBuildTag,
                                unresolved=unresolved, autocreate=autocreate, forcedTagAttr=forcedTagAttr,
                                translate_cb=translate_cb, self_closed_tags=self_closed_tags,
                                omitUnknownTypes=omitUnknownTypes, catalog=catalog, omitRoot=omitRoot,
                                docHeader=docHeader,mode4d=mode4d,pretty=pretty)
                                
    def fillFrom(self, source):
        """Fill a void Bag from a source (basestring, Bag or list)
        
        :param source: the source for the Bag"""
        if isinstance(source, basestring):
            b = self._fromSource(*self._sourcePrepare(source))
            if not b: b = Bag()
            self._nodes[:] = b._nodes[:]

        elif isinstance(source, Bag):
            self._nodes = [BagNode(self, *x.asTuple()) for x in source]
        elif isinstance(source, list) or isinstance(source, tuple):
            if len(source) > 0:
                if not (isinstance(source[0], list) or isinstance(source[0], tuple)):
                    source = [source]
                for x in source:
                    if len(x) == 3:
                        self.setItem(x[0], x[1], _attributes=x[2])
                    else:
                        self.setItem(x[0], x[1])
        elif hasattr(source, 'items'):
            for key, value in source.items():
                if hasattr(value, 'items'):
                    value = Bag(value)
                self.setItem(key, value)

    def _fromSource(self, source, fromFile, mode):
        """Receive "mode" and "fromFile" and switch between the different
        modes calling _fromXml or _unpickle
        
        :param source: the source string or source URI
        :param fromFile: flag that says if source is eventually an URI
        :param mode: flag of the importation mode (XML, pickle or VCARD)
        :returns: a Bag from _unpickle() method or from _fromXml() method"""
        if not source:
            return
            
        if mode == 'xml':
            return self._fromXml(source, fromFile)
        elif mode == 'pickle':
            return self._unpickle(source, fromFile)
        elif mode == 'direct':
            return Bag((os.path.basename(source).replace('.', '\.'), UrlResolver(source)))
        elif mode == 'isdir':
            source = source.rstrip('/')
            return Bag((os.path.basename(source), DirectoryResolver(source)))
        elif mode == 'unknown':
            raise  BagException('invalid source: %s' % source)
            
    def _sourcePrepare(self, source):
        """Generate a Bag from a generic xml
        
        :param source: an xml string or a path to an xml document
        :type source: basestring
        :returns: source, fromFile, mode
        
        "source" parameter can be either a URI (file path or URL) or a string.
        If source is a an URI the method opens and reads the identified file an sets
        the value of the flag "fromFile" to true.
        
        Anyway source can be a well-formed XML document, or a raw one,or even a
        pickled bag. In any of this cases the method sets the value of the flag
        "mode" to xml, vcard or pickle and returns it with \"source\" and \"fromFile\""""
        originalsource = source
        if source.startswith('<'):
            return source, False, 'xml'
        if len(source) > 300:
            #if source is longer than 300 chars it cannot be a path or an URI
            return source, False, 'unknown' #it is a long not xml string
        if sys.platform == "win32" and ":\\" in source:
            urlparsed = ('file', None, source)
        else:
            urlparsed = urlparse.urlparse(source)
        if not urlparsed[0] or urlparsed[0] == 'file':
            source = urlparsed[2]
            if os.path.exists(source):
                if os.path.isfile(source):
                    fname, fext = os.path.splitext(source)
                    fext = fext[1:]
                    if fext in ['pckl', 'pkl', 'pik']:
                        return source, True, 'pickle'
                    elif fext in ['xml', 'html', 'xhtml', 'htm']:
                        return source, True, 'xml'
                    else:
                        f = file(source, mode='r')
                        sourcestart = f.read(30)
                        f.close()
                        if sourcestart.startswith('<'):
                            return source, True, 'xml' #file xml with unknown extension
                        else:
                            return source, True, 'unknown' #unidentified file
                elif os.path.isdir(source):
                    return source, False, 'isdir' #it's a directory
            else:
                return originalsource, False, 'unknown' #short string of unknown type
        urlobj = urllib.urlopen(source)
        info = urlobj.info()
        contentType = info.gettype().lower()
        if 'xml' in contentType or 'html' in contentType:
            return urlobj.read(), False, 'xml' #it is an url of type xml
        return source, False, 'direct' #urlresolver


    #-------------------- fromXml --------------------------------
    def fromXml(self, source, catalog=None, bagcls=None, empty=None):
        """Fill a Bag with values read from an XML string or file or URL
        
        :param source: the XML source to be loaded in the Bag
        :param catalog: TODO
        :param bagcls: TODO
        :param empty: TODO"""
        source, fromFile, mode = self._sourcePrepare(source)
        self._nodes[:] = self._fromXml(source, fromFile, catalog=catalog,
                                       bagcls=bagcls, empty=empty)

    def _fromXml(self, source, fromFile, catalog=None, bagcls=None, empty=None):
        from gnr.core.gnrbagxml import BagFromXml

        return BagFromXml().build(source, fromFile, catalog=catalog, bagcls=bagcls, empty=empty)

    def getIndex(self):
        """Return the Bag index with all the internal address"""
        path = []
        resList = []
        exploredNodes = [self]
        self._deepIndex(path, resList, exploredNodes)
        return resList

    def _deepIndex(self, path, resList, exploredItems):
        for node in self._nodes:
            v = node.value
            resList.append((path + [node.label], node))
            if hasattr(v, '_deepIndex'):
                if not v in exploredItems:
                    exploredItems.append(v)
                    v._deepIndex(path + [node.label], resList, exploredItems)
                    
    def getIndexList(self, asText=False):
        """Return the Bag index as a plan list of the Nodes paths
        
        :param asText: TODO"""
        l = self.getIndex()
        l = ['.'.join(x) for x, y in l]
        if asText:
            return '\n'.join(l)
        return l
        
    def addValidator(self, path, validator, parameterString):
        """Add a validator into the node at the given path
        
        :param path: node's path
        :param validator: validation's type
        :param parameterString: a string which contains the parameters for the validation"""
        self.getNode(path, autocreate=True).addValidator(validator, parameterString)

    def removeValidator(self, path, validator):
        """Remove a node's validator at the given path
        
        :param path: node's path
        :param validator: validation's type"""
        self.getNode(path).removeValidator(validator)

    def _onNodeChanged(self, node, pathlist, evt, oldvalue=None):
        """Set a function at changing events. It is called from the trigger system.
        
        :param node: the node that has benn changed
        :param pathlist: it includes the Bag subscribed's path linked to the node
                         where the event was catched
        :param evt: it is the event type, that is insert, delete, upd_value or upd_attrs
        :param oldvalue: it is the previous node's value"""
        for s in self._upd_subscribers.values():
            s(node=node, pathlist=pathlist, oldvalue=oldvalue, evt=evt)
        if self.parent:
            self.parent._onNodeChanged(node, [self.parentNode.label] + pathlist, evt, oldvalue)

    def _onNodeInserted(self, node, ind, pathlist=None):
        """Set a function at inserting events. It is called from the trigger system
        
        :param node: The node inserted
        :param ind: TODO
        :param pathlist: it includes the Bag subscribed's path linked to the node
                         where the event was catched"""
        parent = node.parentbag
        if parent != None and parent.backref and hasattr(node._value, '_htraverse'):
            node._value.setBackRef(node=node, parent=parent)

        if pathlist == None:
            pathlist = []
        for s in self._ins_subscribers.values():
            s(node=node, pathlist=pathlist, ind=ind, evt='ins')
        if self.parent:
            self.parent._onNodeInserted(node, ind, [self.parentNode.label] + pathlist)

    def _onNodeDeleted(self, node, ind, pathlist=None):
        """This method is called from the trigger system and set a function at deleting events
        
        :param node: The node inserted
        :param ind: TODO
        :param pathlist: it includes the Bag subscribed's path linked to the node
                         where the event was catched"""
        for s in self._del_subscribers.values():
            s(node=node, pathlist=pathlist, ind=ind, evt='del')
        if self.parent:
            if pathlist == None:
                pathlist = []
            self.parent._onNodeDeleted(node, ind, [self.parentNode.label] + pathlist)
            
    def _subscribe(self, subscriberId, subscribersdict, callback):
        if not callback is None:
            subscribersdict[subscriberId] = callback
            
    def subscribe(self, subscriberId, update=None, insert=None, delete=None, any=None):
        """Provide a subscribing of a function to an event.
        Subscribing an event on a Bag means that every time that it happens,
        it is propagated along the bag hierarchy and is triggered by its
        eventhandler. A subscription can be seen as a event-function couple,
        so you can define many eventhandlers for the same event
        
        :param subscriberId: the Id of the Bag's subscription
        :param update: the eventhandler function linked to update event
        :param insert: the eventhandler function linked to insert event
        :param delete: the eventhandler function linked to delete event
        :param any: the eventhandler function linked to do whenever something
                    (delete, insert or update action) happens"""
        if self.backref == False:
            self.setBackRef()

        self._subscribe(subscriberId, self._upd_subscribers, update or any)
        self._subscribe(subscriberId, self._ins_subscribers, insert or any)
        self._subscribe(subscriberId, self._del_subscribers, delete or any)

    def unsubscribe(self, subscriberId, update=None, insert=None, delete=None, any=None):
        """Delete a subscription of an event of a given subscriberId
        
        :param subscriberId: the Id of the Bag's subscription
        :param update: the eventhandler function linked to update event
        :param insert: the eventhandler function linked to insert event
        :param delete: the eventhandler function linked to delete event
        :param any: the eventhandler function linked to do whenever something
                    (delete, insert or update action) happens"""
        if update or any:
            self._upd_subscribers.pop(subscriberId, None)
        if insert or any:
            self._ins_subscribers.pop(subscriberId, None)
        if delete or any:
            self._del_subscribers.pop(subscriberId, None)

    def setCallBackItem(self, path, callback, **kwargs):
        """An alternative syntax for a :class:`BagCbResolver` call
        
        :param path: TODO
        :param callback: TODO"""
        resolver = BagCbResolver(callback, **kwargs)
        self.setItem(path, resolver, **kwargs)
        
    def cbtraverse(self, pathlist, callback, result=None, **kwargs):
        """TODO
        
        :param pathlist: TODO
        :param callback: TODO
        :param result: TODO"""
        if result is None:
            result = []
        if isinstance(pathlist, basestring):
            pathlist = gnrstring.smartsplit(pathlist.replace('../', '#^.'), '.')
            pathlist = [x for x in pathlist if x]
        label = pathlist.pop(0)
        i = self._index(label)
        if i >= 0:
            result.append(callback(self._nodes[i], **kwargs))
            if pathlist:
                self._nodes[i].getValue().cbtraverse(pathlist, callback, result, **kwargs)
        return result
        
    def nodesByAttr(self,attr,_mode='static',**kwargs):
        if 'value' in kwargs:
            def f(node,r):
                if node.getAttr(attr) == value:
                    r.append(node)
        else:
            def f(node,r):
                if attr in node.attr:
                    r.append(node)
        r = []
        self.walk(f,r,_mode=_mode)
        return r   
        
    def findNodeByAttr(self, attr, value,_mode='static',**kwargs):
        def f(node):
            if node.getAttr(attr) == value:
                return node 
        return self.walk(f,_mode=_mode)

    
        
    def filter(self, cb, _mode='static', **kwargs):
        """TODO
        
        :param cb: TODO
        """
        result=Bag()
        for node in self.nodes:
            value = node.getValue(mode=_mode)
            if value and isinstance(value, Bag):
                value=value.filter(cb,_mode=_mode,**kwargs)
                if value:
                    result.setItem(node.label,value,node.attr)
            elif cb(node):
                result.setItem(node.label,value,node.attr)
        return result

    def walk(self, callback, _mode='static', **kwargs):
        """Calls a function for each node of the Bag
        
        :param callback: the function which is called
        """
        result = None
        for node in self.nodes:
            result = callback(node, **kwargs)
            if result is None:
                value = node.getValue(mode=_mode)
                if isinstance(value, Bag):
                    kw=dict(kwargs)
                    if '_pathlist' in kwargs:
                        kw['_pathlist'] = kw['_pathlist'] + [node.label]
                    result = value.walk(callback, _mode=_mode, **kw)
            if result:
                return result

    def traverse(self):
        """TODO"""
        for node in self.nodes:
            yield node
            value = node.getStaticValue()
            if isinstance(value, Bag):
                for node in value.traverse():
                    yield node

    def rowchild(self, childname='R_#', _pkey=None, **kwargs):
        """TODO
        
        :param childname: the :ref:`childname` including the row name
        """
        if not childname:
            childname = 'R_#'
        childname = childname.replace('#', str(len(self)).zfill(8))
        _pkey = _pkey or childname
        return self.setItem(childname, None, _pkey=_pkey, _attributes=kwargs)

    def child(self, tag, childname='*_#', childcontent=None, _parentTag=None, **kwargs):
        """Set a new item of a tag type into the current structure or return the parent
        
        :param tag: structure type
        :param name: structure name
        :param childcontent: the html content
        """
        where = self
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
        childname = childname.replace('*', tag).replace('#', str(len(where)))
        
        if childcontent == None:
            childcontent = self.__class__()
            result = childcontent
        else:
            result = None
            
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
                kwargs = dict(
                        [(k, v) for k, v in kwargs.items() if v != None]) # default kwargs don't clear old attributes
                result = where[childname]
                result.attributes.update(**kwargs)
        else:
            where.setItem(childname, childcontent, tag=tag, _attributes=kwargs)
        return result

class BagValidationList(object):
    """This class provides the validation system for a BagNode. This is a list
    of validators related to a BagNode. This class is used only from the addValidator
    and removeValidator methods of the Bag and BagNode' classes.
    All the methods of this class must be considered private."""
    def __init__(self, parentNode):
        self.parentNode = parentNode
        self.validators = []
        self.validatorsdata = {}
        self.status = None
        self.errMsg = None

    def getdata(self, validator, label=None, dflt=None):
        """This method get the validatorsdata of a validator"""
        if validator in self.validatorsdata:
            data = self.validatorsdata[validator]
            if label is None:
                return data
            else:
                return data.get(label, dflt)

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
        """Add a new validator to the BagValidationList.
        
        :param validator: type of validator
        :param parameterString: the string that contains the parameters for the validators"""
        if isinstance(validator, basestring):
            validator = getattr(self, 'validate_%s' % validator, self.defaultExt)
        if not validator in self.validators:
            self.validators.append(validator)
            self.validatorsdata[validator] = parameterString
            
    def remove(self, validator):
        """Remove a validator
        
        :param validator: the validator to remove"""
        if validator in self.validators:
            self.validators.remove(validator)
            
    def __call__(self, value, oldvalue):
        """Apply the validation to a BagNode value."""
        for validator in self.validators:
            value = validator(value, oldvalue, self.validatorsdata[validator])
        return value

    def validate_case(self, value, oldvalue, parameterString):
        """Set a validation for the case of a string value
        
        :param value: TODO
        :param oldvalue: TODO
        :param parameterString: values = 'upper' or 'lower' or 'capitalize'"""
        mode = parameterString
        if not isinstance(value, basestring):
            raise BagValidationError('not a string value', value, 'The value is not a string')
        else:
            if mode.lower() == 'upper':
                value = value.upper()
            elif mode.lower() == 'lower':
                value = value.lower()
            elif mode.lower() == 'capitalize':
                value = value.capitalize()
            return value
            
    def validate_inList(self, value, oldvalue, parameterString):
        """TODO
        
        :param value: TODO
        :param oldvalue: TODO
        :param parameterString: TODO"""
        values = parameterString.split(',')
        if not value in values:
            raise BagValidationError('NotInList', value, 'The value is non in list')
        else:
            return value
            
    def validate_hostaddr (self, value, oldvalue):
        """Provide a validaton for Host address value
        
        :param value: TODO
        :param oldvalue: TODO"""
        import socket
        
        try:
            x = socket.gethostbyaddr(socket.gethostbyname(value))
            hostaddr, hostname = x[2][0], x[0]
            self.validatorsdata['hostaddr'] = {'hostname': hostname}
            return hostaddr
        except:
            hostaddr = value
            self.validatorsdata['hostaddr'] = {'hostname': 'Unknown host'}
            raise BagValidationError('Unknown host', value, 'The host is not valid')
            
    def validate_length(self, value, oldvalue, parameterString):
        """Provides a validation for the length of a string value
        
        :param value: TODO
        :param oldvalue: TODO
        :param parameterString: TODO"""
        minmax = parameterString.split(',')
        min = minmax[0]
        max = minmax[1]
        n = len(value)
        if (not min is None) and n < min:
            raise BagValidationError('Value too short', value, 'The length of value is too short')
        if (not max is None) and n > max:
            raise BagValidationError('Value too long', value, 'The length of value is too long')
        return value

    def coerceFromText(self, value):
        """TODO
        
        :param value: TODO"""
        value = converter.fromText(value, self.gnrtype)

    def validate_db(self, value, oldvalue, parameterString):
        """TODO
        
        :param value: TODO
        :param oldvalue: TODO
        :param parameterString: TODO"""
        # print value
        return value

    def defaultExt (self, value, oldvalue, parameterString):
        """TODO
        
        :param value: TODO
        :param oldvalue: TODO
        :param parameterString: TODO"""
        print 'manca il validatore'

class BagResolver(object):
    """BagResolver is an abstract class, that defines the interface for a new kind
    of dynamic objects. By "Dynamic" property we mean a property that is calculated
    in real-time but looks like a static one"""
    classKwargs = {'cacheTime': 0, 'readOnly': True}
    classArgs = []

    def __init__(self, *args, **kwargs):
        self._initArgs = list(args)
        self._initKwargs = dict(kwargs)
        self.parentNode = None
        self.kwargs = {}
        classKwargs = dict(self.classKwargs)
        for j, arg in enumerate(args):
            parname = self.classArgs[j]
            setattr(self, parname, arg)
            classKwargs.pop(parname, None)
            kwargs.pop(parname, None)

        for parname, dflt in classKwargs.items():
            setattr(self, parname, kwargs.pop(parname, dflt))
        self.kwargs.update(kwargs)

        self._attachKwargs()

        self._attributes = {}# ma servono ?????
        self.init()

    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and (self.kwargs == other.kwargs):
                return True
        except:
            return False

    def _get_parentNode(self):
        if hasattr(self,'_parentNode'):
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
        result = {}
        for par, dflt in self.classKwargs.items():
            result[par] = getattr(self, par)
        for par in self.classArgs:
            result[par] = getattr(self, par)
        return result

    instanceKwargs = property(_get_instanceKwargs)

    def _attachKwargs(self):
        for k, v in self.kwargs.items():
            setattr(self, k, v)
            if k in self.classKwargs:
                self.kwargs.pop(k)

    def _set_cacheTime(self, cacheTime):
        self._cacheTime = cacheTime
        if cacheTime != 0:
            if cacheTime < 0:
                self._cacheTimeDelta = timedelta.max
            else:
                self._cacheTimeDelta = timedelta(0, cacheTime)
            self._cache = None
            self._cacheLastUpdate = datetime.min

    def _get_cacheTime(self):
        return self._cacheTime

    cacheTime = property(_get_cacheTime, _set_cacheTime)

    def reset(self):
        """TODO"""
        self._cache = None
        self._cacheLastUpdate = datetime.min

    def _get_expired(self):
        if self._cacheTime == 0 or self._cacheLastUpdate == datetime.min:
            return True
        return ((datetime.now() - self._cacheLastUpdate ) > self._cacheTimeDelta)

    expired = property(_get_expired)

    def __call__(self, **kwargs):
        if kwargs and kwargs != self.kwargs:
            self.kwargs.update(kwargs)
            self._attachKwargs()
            self.reset()

        if self.cacheTime == 0:
            return self.load()

        if self.expired:
            result = self.load()
            self._cacheLastUpdate = datetime.now()
            self._cache = result
        else:
            result = self._cache
        return result

    def load(self):
        """.. warning:: deprecated since version 0.7"""
        pass

    def init(self):
        """TODO
        """
        pass

    def resolverSerialize(self):
        """TODO"""
        attr = {}
        attr['resolverclass'] = self.__class__.__name__
        attr['resolvermodule'] = self.__class__.__module__
        attr['args'] = self._initArgs
        attr['kwargs'] = self._initKwargs
        return attr
        
    def __getitem__(self, k):
        return self().__getitem__(k)
        
    def _htraverse(self, *args, **kwargs):
        return self()._htraverse(*args, **kwargs)
        
    def keys(self):
        """same method of the dict :meth:`keys()`"""
        return self().keys()
        
    def items(self):
        """same method of the dict :meth:`items()`"""
        return self().items()
        
    def values(self):
        """same method of the dict :meth:`values()`"""
        return self().values()
        
    def digest(self, k=None):
        """same method of the dict :meth:`digest()`"""
        return self().digest(k)
        
    def sum(self, k=None):
        """TODO"""
        return self().sum(k)
        
    def iterkeys(self):
        """TODO"""
        return self().iterkeys()
        
    def iteritems(self):
        """TODO"""
        return self().iteritems()

    def itervalues(self):
        """TODO"""
        return self().itervalues()
        
    def __iter__(self):
        return self().__iter__()
        
    def __contains__(self):
        return self().__contains__()
        
    def __len__(self):
        return len(self())
        
    def getAttributes(self):
        """TODO"""
        return self._attributes
        
    def setAttributes(self, attributes):
        """TODO"""
        self._attributes = attributes or dict()
        
    attributes = property(getAttributes, setAttributes)
        
    def resolverDescription(self):
        """TODO"""
        return repr(self)
        
    def __str__(self):
        return self.resolverDescription()
        
class GeoCoderBag(Bag):
    def setGeocode(self, key, address):
        """TODO

        :param key: TODO
        :param address: TODO"""
        url = "http://maps.google.com/maps/geo?%s" % urllib.urlencode(dict(q=address, output='xml'))
        result = Bag()

        def setData(n):
            v = n.getValue()
            if isinstance(v, basestring):
                result[n.label] = v


        answer = Bag(url)['#0.#0.Placemark']
        if answer:
            answer.walk(setData)
        self[key] = result


class VObjectBag(Bag):
    def fillFrom(self,source):
        if isinstance(source,basestring):
            source, fromFile, mode = self._sourcePrepare(source)
            if fromFile:
                urlobj = urllib.urlopen(source)
                info = urlobj.info()
                contentType = info.gettype().lower()
                source= urlobj.read()
            source=source.split('\r\n')
        current=Bag()
        self._vparse(source,current)
        self._nodes[:] = current._nodes[:]
        
    def _vparse(self,rows,current):
        counters={}
        while rows:
            r=rows.pop(0)
            if not ':' in r:
                if r:
                    if label:
                        value='%s%s'%(value,r)
                    current.setItem(label,value)
            else:
                vtag,value=r.split(':',1)
                if vtag=='BEGIN':
                    vtag=value
                    value=VObjectBag(rows)
                    
                elif vtag=='END':
                    return 
                if not vtag in counters:                    
                    counters[vtag]=0
                    label=vtag
                else:
                    label=('%s_%s'%(vtag,counters[vtag]))
                label=label.lower()
                current.setItem(label,value,vtag=vtag)
                counters[vtag]=counters[vtag]+1       
                
                
class GeoCoderBagNew(Bag):
    def setGeocode(self, key, address, language='it'):
        """TODO

        :param key: TODO
        :param address: TODO"""
        urlparams = dict(address=address,sensor='false')
        if language:
            urlparams['language']=language
        url = "http://maps.googleapis.com/maps/api/geocode/xml?%s" % urllib.urlencode(urlparams)
        self._result = Bag()
        answer = Bag(url)
        if answer['GeocodeResponse.status']=='OK':
            answer=answer['GeocodeResponse.result']
            for n in answer:
                if n.label == 'formatted_address':
                    self._result[n.label]=n.value
                elif n.label == 'address_component':
                    self._parseAddressComponent(n.value)
                elif n.label=='geometry':
                    self._result.setItem('details.geometry',n.value)
        self[key] = self._result
        self.result=None

    def _parseAddressComponent(self, node):
        attr=dict()
        attr[node['type']]=node['long_name']
        self._result['details.%s'%node['type']]=node['short_name']
        self._result.setAttr('formatted_address',**attr)
        
class BagCbResolver(BagResolver):
    """A standard resolver. Call a callback method, passing its kwargs parameters"""
    classArgs = ['method']
        
    def load(self):
        """TODO"""
        return self.method(**self.kwargs)
        
class UrlResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 300, 'readOnly': True}
    classArgs = ['url']
        
    def load(self):
        """TODO"""
        x = urllib.urlopen(self.url)
        result = {}
        result['data'] = x.read()
        result['info'] = x.info()
        return result
        
class DirectoryResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 500,
                   'readOnly': True,
                   'invisible': False,
                   'relocate': '',
                   'ext': 'xml',
                   'include': '',
                   'exclude': '',
                   'callback': None,
                   'dropext': False,
                   'processors': None
    }
    classArgs = ['path', 'relocate']
    
    def load(self):
        """TODO"""
        extensions = dict([((ext.split(':') + (ext.split(':'))))[0:2] for ext in self.ext.split(',')])
        extensions['directory'] = 'directory'
        result = Bag()
        try:
            directory = os.listdir(self.path)
        except OSError:
            directory = []
        if not self.invisible:
            directory = [x for x in directory if not x.startswith('.')]
        for fname in directory:
            nodecaption = fname
            fullpath = os.path.join(self.path, fname)
            relpath = os.path.join(self.relocate, fname)
            addIt = True
            if os.path.isdir(fullpath):
                ext = 'directory'
                if self.exclude:
                    addIt = gnrstring.filter(fname, exclude=self.exclude, wildcard='*')
            else:
                if self.include or self.exclude:
                    addIt = gnrstring.filter(fname, include=self.include, exclude=self.exclude, wildcard='*')
                fname, ext = os.path.splitext(fname)
                ext = ext[1:]
            if addIt:
                label = self.makeLabel(fname, ext)
                handler = getattr(self, 'processor_%s' % extensions.get(ext.lower(), None), None)
                if not handler:
                    processors = self.processors or {}
                    handler = processors.get(ext.lower(), self.processor_default)
                try:
                    stat = os.stat(fullpath)
                    mtime = stat.st_mtime
                except OSError:
                    mtime = ''
                    
                if self.callback:
                    moreattr = self.callback(fullpath)
                else:
                    moreattr = {}
                result.setItem(label, handler(fullpath), file_name=fname, file_ext=ext, rel_path=relpath,
                               abs_path=fullpath, mtime=mtime, nodecaption=nodecaption, **moreattr)
        return result
        
    def makeLabel(self, name, ext):
        """TODO
        
        :param name: TODO
        :param ext: TODO"""
        if ext != 'directory' and not self.dropext:
            name = '%s_%s' % (name, ext)
        return name.replace('.', '_')
        
    def processor_directory(self, path):
        """TODO
        
        :param path: TODO"""
        return DirectoryResolver(path, os.path.join(self.relocate, os.path.basename(path)), **self.instanceKwargs)
        
    def processor_xml(self, path):
        """TODO
        
        :param path: TODO"""
        kwargs = dict(self.instanceKwargs)
        kwargs['path'] = path
        return XmlDocResolver(**kwargs)
        
    processor_html = processor_xml
        
    def processor_txt(self, path):
        """TODO
        
        :param path: TODO"""
        kwargs = dict(self.instanceKwargs)
        kwargs['path'] = path
        return TxtDocResolver(**kwargs)
        
    def processor_default(self, path):
        """TODO
        
        :param path: TODO"""
        return None
        
class TxtDocResolver(BagResolver):
    classKwargs = {'cacheTime': 500,
                   'readOnly': True
    }
    classArgs = ['path']
        
    def load(self):
        f = file(self.path, mode='r')
        result = f.read()
        f.close()
        return result

class XmlDocResolver(BagResolver):
    classKwargs = {'cacheTime': 500,
                   'readOnly': True
    }
    classArgs = ['path']

    def load(self):
        return Bag(self.path)


class BagFormula(BagResolver):
    """Calculate the value of an algebric espression"""
    classKwargs = {'cacheTime': 0,
                   'formula': '',
                   'parameters': None, 'readOnly': True
    }
    classArgs = ['formula', 'parameters']
        
    def init(self):
        """TODO"""
        parameters = {}
        for key, value in self.parameters.items():
            if key.startswith('_'):
                parameters[key] = "curr.getResolver('%s')" % value
            else:
                parameters[key] = "curr['%s']" % value
        self.expression = gnrstring.templateReplace(self.formula, parameters)
        
    def load(self):
        """TODO"""
        curr = self.parentNode.parentbag
        return eval(self.expression)
        
########################### start experimental features#######################
class BagResolverNew(object):
    def __init__(self, cacheTime=0, readOnly=True,
                 serializerStore=None, **kwargs):
        self.serializerStore = serializerStore
        self.kwargs = {}
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
        
    def _getPar(self, name):
        attr = getattr(self, name)
        if isinstance(attr, basestring) or\
           isinstance(attr, int) or\
           isinstance(attr, float):
            return attr
        elif self.serializerStore is None:
            raise BagException('Missing SerializerStore')
        else:
            key = '%s' % name
            self.serializerStore[key] = attr
            return key
            
    def __eq__(self, other):
        try:
            if isinstance(other, self.__class__) and (self.kwargs == other.kwargs):
                return True
        except:
            return False
            
    def _get_parentNode(self):
        if hasattr(self,'_parentNode'):
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
        self._cacheTime = cacheTime
        if cacheTime != 0:
            if cacheTime < 0:
                self._cacheTimeDelta = timedelta.max
            else:
                self._cacheTimeDelta = timedelta(0, cacheTime)
            self._cache = None
            self._cacheLastUpdate = datetime.min
            
    def _get_cacheTime(self):
        return self._cacheTime
        
    cacheTime = property(_get_cacheTime, _set_cacheTime)
        
    def reset(self):
        self._cache = None
        self._cacheLastUpdate = datetime.min
        
    def _get_expired(self):
        if self._cacheTime == 0 or self._cacheLastUpdate == datetime.min:
            return True
        return ((datetime.now() - self._cacheLastUpdate ) > self._cacheTimeDelta)
        
    expired = property(_get_expired)
        
    def _updateKwargs(self, kwargs):
        reset = False
        for k, v in kwargs.items():
            if self.kwargs.get(k) != v:
                reset = True
                self.kwargs(k, v)
                setattr(self, k, v)
        if reset:
            self.reset()
            
    def __call__(self, **kwargs):
        if kwargs:
            self._updateKwargs(kwargs)
            
        if self.cacheTime == 0:
            return self.load()
            
        if self.expired:
            result = self.load()
            self._cacheLastUpdate = datetime.now()
            self._cache = result
        else:
            result = self._cache
        return result
        
    def load(self):
        """.. warning:: deprecated since version 0.7"""
        pass

    def init(self):
        pass

    def resolverSerialize(self):
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'], attr['kwargs'] = self._argSerializer()
        return attr

    def __getitem__(self, k):
        return self().__getitem__(k)

    def _htraverse(self, *args, **kwargs):
        return self()._htraverse(*args, **kwargs)

    def keys(self):
        return self().keys()

    def items(self):
        return self().items()

    def values(self):
        return self().values()

    def digest(self, k=None):
        return self().digest(k)

    def sum(self, k=None):
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

    def setAttributes(self, attributes):
        self._attributes = attributes or dict()

    attributes = property(getAttributes, setAttributes)

    def resolverDescription(self):
        return repr(self)

    def __str__(self):
        return self.resolverDescription()

########################### end experimental features#########################

def testFormule():
    b = Bag()
    b.defineFormula(calc_riga_lordo='$riga_qta*$riga_prUnit')
    b.defineSymbol(riga_qta='qta', riga_prUnit='prUnit')
    b.defineFormula(calc_riga_netto='$riga_lordo*(100+$riga_sconto)/100')
    b.defineSymbol(riga_lordo='lordo', riga_sconto='../../sconto')
    b.defineFormula(sum_riga_netto="$righe.sum('netto')")
    b.defineSymbol(righe='righe')

    b['ft1.num'] = '12345'
    b.setItem('ft1.date', '2006-1-3')
    b['ft1.sconto'] = 5
    b['ft1.netto'] = b.formula('sum_riga_netto')
    b['ft1.iva'] = b.formula('$netto*0.2', netto='netto')
    b['ft1.totalefattura'] = b.formula('$netto+$iva', netto='netto', iva='iva')
    b['ft1.righe.1.cod'] = 'b21'
    b['ft1.righe.1.desc'] = 'pollo'
    b['ft1.righe.1.prUnit'] = 3.5
    b['ft1.righe.1.qta'] = 2
    b['ft1.righe.1.lordo'] = b.formula('calc_riga_lordo')
    b['ft1.righe.1.netto'] = b.formula('calc_riga_netto')
    b['ft1.righe.2.cod'] = 'h26'
    b['ft1.righe.2.desc'] = 'trota'
    b['ft1.righe.2.prUnit'] = 9.2
    b['ft1.righe.2.qta'] = 1
    riga2 = b['ft1.righe.2']
    riga2['lordo'] = b.formula('calc_riga_lordo')
    riga2['netto'] = b.formula('calc_riga_netto')
    b['ft1.righe.3.cod'] = 'w43'
    b['ft1.righe.3.desc'] = 'manzo'
    b['ft1.righe.3.prUnit'] = 4.
    b['ft1.righe.3.qta'] = 4
    b['ft1.righe.3.lordo'] = b.formula('calc_riga_lordo')
    b['ft1.righe.3.netto'] = b.formula('calc_riga_netto')

    a = b['ft1.righe.1.lordo']

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
    classKwargs = {'cacheTime': 0, 'limit': None}
    classArgs = []

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
            n = n + 1
            result['%s method: %s line: %s' % (tb_bag['module'], name, lineno)] = tb_bag
        return result

def testfunc (**kwargs):
    print kwargs

#import Pyro.core
#class PyroBag(Bag, Pyro.core.ObjBase):
#    def __init__(self):
#        Bag.__init__(self)
#        Pyro.core.ObjBase.__init__(self)

if __name__ == '__main__':
    b = Bag()
    b.setItem('aa', 4, _attributes={'aa': 4, 'bb': None}, _removeNullAttributes=False)
    print b.toXml()
