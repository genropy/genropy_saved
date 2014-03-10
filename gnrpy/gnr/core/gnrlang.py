# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrlang : support funtions
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

import inspect
#import weakref
import sys, imp, traceback, datetime
import os.path
import thread
import warnings
import atexit
import uuid
import base64
import time
from gnr.core.gnrdecorator import deprecated,extract_kwargs # keep for compatibility
thread_ws = dict()


def tracebackBag(limit=None):
    import linecache
    from gnr.core.gnrstructures import GnrStructData
    from gnr.core.gnrbag import Bag
    result = Bag()
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    n = 0
    tb = sys.exc_info()[2]
    def cb(n):
        if n.resolver:
            n.resolver = None
            n.value = '*RESOLVER* %s' %n.label

        if isinstance(n.getValue('static'),GnrStructData):
            n.value = '*STRUCTURE*'

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
        #tb_bag['locals'] = Bag(f.f_locals.items())
        loc = Bag()
        for k,v in f.f_locals.items():
            try:
                loc[k] = v
            except Exception:
                loc[k] = '*UNSERIALIZABLE* %s' %v.__class__
        tb_bag['locals'] = loc
        tb_bag['locals'].walk(cb)
        tb = tb.tb_next
        n = n + 1
        result['%s method %s line %s' % (tb_bag['module'], name, lineno)] = tb_bag
    return Bag(root=result)


class BaseProxy(object):
    def __init__(self, main):
        self.main=main

class FilterList(list):
    """TODO"""
    def __contains__old(self, item):
        return len([k for k in self if k == item or k.endswith('*') and item.startswith(k[0:-1])]) > 0

    def __contains__(self, item):
        for my_item in self:
            if my_item == item or my_item.endswith('*') and item.startswith(my_item[0:-1]):
                return True
        return False

def thlocal():
    """TODO"""
    return thread_ws.setdefault(thread.get_ident(), {})
    
def boolean(x):
    """Control if a string is "True" or "False" respect to Genro acceptable "True" and "False" strings
    and return ``True`` (or ``False``). The control is executed on the string uppercased
    
    * "True" strings: ``TRUE``, ``T``, ``Y``, ``YES``, ``1``
    * "False" strings: ``FALSE``, ``F``, ``N``, ``NO``, ``0``
    
    :param x: the string to be checked"""
    if isinstance(x, basestring):
        x = x.upper()
        if x in ('TRUE', 'T', 'Y', 'YES', '1'):
            return True
        if x in ('FALSE', 'F', 'N', 'NO', '0'):
            return False
    return bool(x)
    
def objectExtract(myobj, f):
    """TODO
    
    :param myobj: TODO
    :param f: TODO"""
    lf = len(f)
    return dict([(k[lf:], getattr(myobj, k)) for k in dir(myobj) if k.startswith(f)])
    
def importModule(module):
    """TODO
    
    :param module: the module to be imported"""
    if module not in sys.modules:
        __import__(module)
    return sys.modules[module]
    
def debug_call(func):
    """TODO
    
    :param func: TODO"""
    def decore(self, *args, **kwargs):
        tloc = thlocal()
        indent = tloc['debug_call_indent'] = tloc.get('debug_call_indent', -1) + 1
        indent = ' ' * indent
        print'%sSTART: %s (args:%s, kwargs=%s)' % (indent, func.func_name, args, kwargs)
        _timer_ = time.time()
        result = func(self, *args, **kwargs)
        print'%sEND  : %s ms: %.4f' % (indent, func.func_name, (time.time() - _timer_) * 1000)
        tloc['debug_call_indent'] -= 1
        return result
        
    return decore

def debug_call_new(attribute_list=None, print_time=False):
    """TODO

    :param time_list: TODO. 
    :param print_time: boolean. TODO"""
    attribute_list=attribute_list or []
    def decore(func):
        def wrapper(*arg, **kw):
            thread_ident = thread.get_ident()
            t1 = time.time()
            tloc = thlocal()
            indent = tloc['debug_call_indent'] = tloc.get('debug_call_indent', -1) + 1
            print'%sSTART: %s in %s (args:%s, kwargs=%s)' % (indent, func.func_name, thread_ident, arg, kw)
            if attribute_list:
                values_dict = dict(map(lambda a: (a,getattr(arg[0],a,None)),attribute_list))
                print values_dict
            print'%sEND  : %s' % (indent, func.func_name)
            res = func(*arg, **kw)
            t2 = time.time()
            if print_time:
                print '-' * 80
                print '%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
                print 10 * ' ' + 28 * '-' + 'args' + 28 * '-' + 10 * ' '
                print arg
                print 10 * ' ' + 27 * '-' + 'kwargs' + 27 * '-' + 10 * ' '
                print kw or (hasattr(arg[0], 'kwargs') and arg[0].kwargs)
                print '-' * 80
            #time_list.append((func.func_name, (t2 - t1) * 1000.0))
            return res
        return wrapper

    return decore

def timer_call(time_list=None, print_time=True):
    """TODO
    
    :param time_list: TODO. 
    :param print_time: boolean. TODO"""
    time_list = time_list or []
    
    def decore(func):
        def wrapper(*arg, **kw):
            t1 = time.time()
            res = func(*arg, **kw)
            t2 = time.time()
            if print_time:
                print '-' * 80
                print '%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
                print 10 * ' ' + 28 * '-' + 'args' + 28 * '-' + 10 * ' '
                print arg
                print 10 * ' ' + 27 * '-' + 'kwargs' + 27 * '-' + 10 * ' '
                print kw or (hasattr(arg[0], 'kwargs') and arg[0].kwargs)
                print '-' * 80
            time_list.append((func.func_name, (t2 - t1) * 1000.0))
            return res
            
        return wrapper
        
    return decore

def getUuid():
    """Return a Python Universally Unique IDentifier 3 (UUID3) through the Python \'base64.urlsafe_b64encode\' method"""
    return base64.urlsafe_b64encode(uuid.uuid3(uuid.uuid1(), str(thread.get_ident())).bytes)[0:22].replace('-','_')
    
def safe_dict(d):
    """Use the str method, coercing all the dict keys into a string type and return the dict
    with string-type keys
    
    :param d: a dict"""
    return dict([(str(k), v) for k, v in d.items()])
    
def uniquify(seq):
    """TODO
    
    :param seq: TODO"""
    def seen_function(seq):
        seen = set()
        for x in seq:
            if x in seen:
                continue
            seen.add(x)
            yield x
            
    return list(seen_function(seq))
            
def optArgs(**kwargs):
    """TODO"""
    return dict([(k, v) for k, v in kwargs.items() if v != None])
            
def moduleDict(module, proplist):
    """TODO
    
    :param module: TODO
    :param proplist: TODO"""
    result = {}
    if isinstance(module, basestring):
        module = gnrImport(module)
    for prop in [x.strip() for x in proplist.split(',')]:
        modulelist = [getattr(module, x) for x in dir(module) if
                      hasattr(getattr(module, x), prop) and getattr(getattr(module, x), '__module__',
                                                                    None) == module.__name__]
        result.update(dict([(getattr(x, prop).lower(), x) for x in modulelist]))
    return result
    
def gnrImport(source, importAs=None, avoidDup=False, silent=True):
    """TODO
    
    :param source: TODO
    :param importAs: TODO
    :param avoidDup: if ``True``, allow to avoid duplicates"""
    modkey = source
    path_sep = os.path.sep
    if path_sep in source:
        if avoidDup and not importAs:
            importAs = os.path.splitext(source)[0].replace(path_sep, '_').replace('.', '_')
        modkey = importAs or os.path.splitext(os.path.basename(source))[0]
    try:
        m = sys.modules[modkey]
        return m
    except KeyError:
        pass
    path = None
    if path_sep in source:
        path = [os.path.dirname(source)]
        source = os.path.splitext(os.path.basename(source))[0]
    segments = source.split('.')
    error = None
    for segment in segments:
        module_file = None
        try:
            imp.acquire_lock()
            module_file, module_path, module_description = imp.find_module(segment, path)
        except ImportError:
            imp.release_lock()
            return None
        if importAs and segment == segments[-1]:
            segment = importAs
        try:
            module = imp.load_module(segment, module_file, module_path, module_description)
            path = getattr(module, '__path__', None)
        except SyntaxError, e:
            raise
        except Exception, e:
            if not silent:
                raise
            module = None
            error = e
        finally:
            if module_file:
                module_file.close()
            if imp.lock_held():
                imp.release_lock()
    return module
    
class GnrException(Exception):
    """Standard Gnr Exception"""
    code = 'GNR-001'
    description = '!!Genro base exception'
    caption = """!!Error code %(code)s : %(description)s."""
    localizer = None
    
    def __init__(self, description=None, **kwargs):
        if description:
            self.description = description
        self.msgargs = kwargs
        self.localizer = None
        
    def __str__(self):
        msgargs = dict(code=self.code, description=self.description)
        msgargs.update(self.msgargs)
        return self.localizedMsg(self.caption, msgargs)
        
    def setLocalizer(self, localizer):
        """TODO
        
        :param localizer: TODO"""
        self.localizer = localizer
        
    def localize(self, v):
        """TODO
        
        :param v: TODO"""
        return self.localizer.translateText(v[2:])
        
    def localizedMsg(self, msg, msgargs):
        """TODO
        
        :param msg: TODO
        :param msgargs: TODO"""
        if self.localizer:
            msg = self.localize(msg)
            for k, v in msgargs.items():
                if isinstance(v, basestring) and v.startswith('!!'):
                    msgargs[k] = self.localize(msgargs[k])
        return msg % msgargs % msgargs # msgargs is use 2 times as we could have msgargs nested(max 1 level)
        
class NotImplementedException(GnrException):
    pass
        
class GnrObject(object):
    """TODO"""
    def __init__(self):
        pass
        
    def mixin(self, cls, **kwargs):
        """TODO
        
        :param cls: the python class to mixin"""
        if isinstance(cls, basestring):
            modulename, cls = cls.split(':')
            m = gnrImport(modulename)
            if m != None:
                cls = getattr(m, cls)
            else:
                raise GnrException('cannot import module: %s' % modulename)
        return instanceMixin(self, cls, **kwargs)
        
class GnrImportedModule(object):
    """TODO"""
    def __init__(self, source):
        if isinstance(source, basestring):
            self.path = source
            self.name = inspect.getmodulename(source)
            self.module = None
            self.load()
        elif(inspect.ismodule(source)):
            self.module = source
            self.name = source.__name__
            path = source.__file__
            info = inspect.getmoduleinfo(path)
            if info[1] == 'pyc':
                path = os.path.splitext(path)[0] + '.py'
                if os.path.isfile(path):
                    self.path = path
                else:
                    self.path = source.__file__
            else:
                self.path = path
                
    def getPath(self):
        """Get the path of the module and return it"""
        return self.path
        
    def getModule(self):
        """Get the module and return it"""
        return self.module
        
    def getName(self):
        """Get the module name and return it"""
        return self.name
        
    def getDoc(self, memberName=None):
        """TODO
        
        :param memberName: TODO"""
        m = self.module
        if memberName:
            m = self.getMember(memberName)
        if m:
            doc = m.__doc__
        if doc: doc = unicode(doc, 'UTF-8')
        else: doc = ""
        return doc
        
    def getMember(self, memberName):
        """TODO
        
        :param memberName: TODO"""
        return getattr(self.module, memberName, None)
        
    #    def getImportedMember(self, memberName):
    #        return ImportedMember(self, memberName)
        
    def load(self):
        """TODO"""
        if self.path.endswith('py'):
            self.module = imp.load_source(self.name, self.path)
        else:
            self.module = imp.load_compiled(self.name, self.path)
            #globals()[self.name]=self.module
            
    def update(self):
        """TODO"""
        self.load()
        
class GnrAddOn(object):
    """A class to be subclassed to inherit some introspection methods"""
        
    def className(self):
        """Get the class name and return it"""
        return self.__class__.__name__
        
    def recorderReset(self):
        """TODO"""
        self.__recorder__ = []
        
    def recorderWrite(self):
        """TODO"""
        frame = sys._getframe(1)
        selector = frame.f_code.co_name
        srcargname, srcargs, srckwargs, vlocals = inspect.getargvalues(frame)
        srcdefaults = inspect.getargspec(getattr(self, selector))[3]
        if not srcdefaults: srcdefaults = []
        nargs = len(srcargname) - len(srcdefaults)
        args = [vlocals[key] for key in srcargname[1:nargs]]
        if srcargs: args.extend(vlocals[srcargs])
        kwargs = dict([(key, vlocals[key]) for key in srcargname[nargs:]])
        if  srckwargs: kwargs.update(vlocals[srckwargs])
        self.__recorder__.append((selector, args, kwargs))
        
    def recorderGet(self):
        """TODO"""
        return self.__recorder__
        
    def recorderDo(self, recorder=None):
        """TODO
        
        :param recorder: TODO"""
        if not recorder: recorder = self.__recorder__[:]
        result = []
        for command, args, kwargs in recorder:
            commandHandler = getattr(self, command)
            result.append(commandHandler(*args, **kwargs))
        return result
        
    def superdo(self, *args, **kwargs):
        """Like calling :meth:`super()` with the right arguments
        
        ??? check if it works on multiple levels"""
        frame = sys._getframe(1)
        superObj = super(self.__class__, self)
        selector = frame.f_code.co_name
        selectorMethod = getattr(superObj, selector, None)
        if selectorMethod:
            if not(args or kwargs):
                srcargname, srcargs, srckwargs, vlocals = inspect.getargvalues(frame)
                srcdefaults = inspect.getargspec(getattr(self, selector))[3]
                if not srcdefaults: srcdefaults = []
                nargs = len(srcargname) - len(srcdefaults)
                args = [vlocals[key] for key in srcargname[1:nargs]]
                if srcargs: args.extend(vlocals[srcargs])
                kwargs = dict([(key, vlocals[key]) for key in srcargname[nargs:]])
                if  srckwargs: kwargs.update(vlocals[srckwargs])
                dstargname, dstargs, dstkwargs, dstdefaults = inspect.getargspec(selectorMethod)
                if not dstdefaults: dstdefaults = []
                nargs = len(dstargname) - len(dstdefaults) - 1
                if not dstargs: args = args[:nargs]
                if not dstkwargs:
                    dstkw = dstargname[-len(dstdefaults):]
                    kwargs = dict([(key, value) for key, value in kwargs.items() if key in dstkw])
            return selectorMethod(*args, **kwargs)
            
    dosuper = staticmethod(superdo)
        
    def setCallable(self, src, importAs=None, bound=True):
        """TODO
        
        :param src: is a string of a python function or an imported function
        :param importAs: a name for identify the function in error messages
        :param bound: boolean. If ``True`` the function will be bounded to this instance"""
        if isinstance(src, basestring):
            if not importAs: importAs = 'abcd'
            compiled = compile(src, importAs, 'exec')
            auxDict = {}
            exec compiled in auxDict
            for name, obj in auxDict.items():
                self.setCallable(obj, name, bound=bound)
        elif inspect.isfunction(src):
            if not importAs: importAs = src.__name__
            if bound:
                newbounded = type(self.__init__)(src, self, self.__class__)
                setattr(self, importAs, newbounded)
            else:
                setattr(self, importAs, src)
                
class GnrRemeberableAddOn(GnrAddOn):
    """TODO"""
    _gnr_members__ = {}
    _gnr_namedmembers__ = {}
    _gnr_remembered_as__ = None
        
    def __del__(self):
        try:
            self._gnr_members__.pop(id(self))
            if self._gnr_remembered_as__: self._gnr_namedmembers__.pop(self._gnr_remembered_as__)
        except:
            pass
        object.__del__(self)
        
    def rememberMe(self, name=None):
        """TODO
        
        :param name: TODO"""
        objid = id(self)
        #self._gnr_members__[objid]=weakref.ref(self)
        self._gnr_members__[objid] = self
        if name:
            old = self._gnr_namedmembers__.get(name, None)
            #if old: self._gnr_members__[old]()._gnr_remembered_as__=None
            if old: self._gnr_members__[old]._gnr_remembered_as__ = None
            self._gnr_remembered_as__ = name
            self._gnr_namedmembers__[name] = objid
            
    def rememberedMembers(cls):
        """TODO
        
        :param cls: TODO"""
        #return [v() for v in cls._gnr_members__.values()]
        return [v for v in cls._gnr_members__.values()]
        
    rememberedMembers = classmethod(rememberedMembers)
        
    def rememberedNamedMembers(cls):
        """TODO
        
        :param cls: TODO"""
        #return dict([(name,cls._gnr_members__[objid]()) for  name,objid in cls._gnr_namedmembers__.items()])
        return dict([(name, cls._gnr_members__[objid]) for  name, objid in cls._gnr_namedmembers__.items()])
        
    rememberedNamedMembers = classmethod(rememberedNamedMembers)
        
    def rememberedGet(cls, name):
        """TODO
        
        :param cls: TODO
        :param name: TODO"""
        objid = cls._gnr_namedmembers__.get(name, None)
        #if objid:return cls._gnr_members__[objid]()
        if objid: return cls._gnr_members__[objid]
        
    rememberedGet = classmethod(rememberedGet)
        
class GnrMetaString(object):
    """TODO"""
    _glossary = {}
        
    def glossary(cls):
        """TODO
        
        :param cls: TODO"""
        return cls._glossary.keys()
        
    glossary = classmethod(glossary)
        
    def __init__(self, value):
        self._glossary[value] = None
        self.value = value
        
    def __repr__(self):
        return '(*' + self.value + '*)'
        
    def __str__(self):
        return '(*)' + self.value + '*)'
        
    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return bool(self.value == value.value)
            
class SuperdoTest(object):
    """TODO"""
    def __init__(self, first, second, alfa='alfadef', beta='betadef'):
        pass
        
class SuperdoTestChild(SuperdoTest, GnrAddOn):
    def __init__(self, a, b, alfa='alfachildef', beta='betachildefd', gamma=78, *args, **kwargs):
        if a == 'gino': a = 'pino'
        self.superdo()
        
class SuperdoTestChildX(SuperdoTest):
    def __init__(self, a, b, alfa='alfachildef', beta='betachildefd', gamma=78, *args, **kwargs):
        if a == 'gino': a = 'pino'
        GnrAddOn.dosuper(self)
        
def addCallable(obj, method):
    """TODO
    
    :param obj: TODO
    :param method: TODO"""
    name = method.__name__
    setattr(obj, name, method)
        
def addBoundCallable(obj, method, importAs=None):
    """TODO
    
    :param obj: TODO
    :param method: TODO
    :param importAs: TODO"""
    z = type(obj.__init__)
    k = z(method, obj, obj.__class__)
    if not importAs:
        importAs = method.__name__
    setattr(obj, importAs, k)
        
def setMethodFromText(obj, src, importAs):
    """TODO
    
    :param obj: TODO
    :param src: TODO
    :param importAs: TODO"""
    compiled = compile(src, 'xyz', 'exec')
    auxDict = {}
    exec compiled in auxDict
    addBoundCallable(obj, auxDict[importAs], importAs)
        
def getObjCallables(obj):
    """TODO
    
    :param obj: TODO"""
    return [(k, getattr(obj, k))  for k in dir(obj) if
            callable(getattr(obj, k)) and not k in ('__call__', '__class__', '__cmp__')]
            
def getObjAttributes(obj):
    """TODO
    
    :param obj: TODO"""
    return [(k, getattr(obj, k))  for k in dir(obj) if not callable(getattr(obj, k))]
        
def callables(obj):
    """TODO
    
    :param obj: TODO"""
    s = getObjCallables(obj)
    return '\n'.join([x for x, v in s])
        
def testbound(self, n):
    """TODO
    
    :param n: TODO"""
    self.special = n * '-'
    return self.special
        
def compareInstances(a, b, __visited=None):
    """TODO
    
    :param a: TODO
    :param b: TODO
    """
    if not __visited:
        __visited = {}
    k1 = str(id(a)) + '-' + str(id(b))
    k2 = str(id(b)) + '-' + str(id(a))
    if dir(a) != dir(b):
        return False
    builtins = dir(__builtins__)
    for propName in dir(a):
        prop = getattr(a, propName)
        if not callable(prop):
            if prop.__class__.__name__ in builtins:
                if prop != getattr(b, propName):
                    return False
            else:
                if not k1 in __visited and not k2 in __visited:
                    result = compareInstances(prop, getattr(b, propName))
                    if result:
                        __visited[k1] = None
                    else:
                        return False
    return True
    
def args(*args, **kwargs):
    """TODO"""
    return (args, kwargs)
    
def setCallable(obj, name, argstring=None, func='pass'):
    """TODO
    
    :param obj: TODO
    :param name: TODO
    :param argstring: TODO
    :param func: TODO"""
    body = '    ' + '\n    '.join(func.split('\n'))
    if argstring:
        argstring = ',' + argstring
    else:
        argstring = ''
    f = "def %s(self%s):\n%s" % (name, argstring, body)
    setMethodFromText(obj, f, name)
        
def cloneClass(name, source_class):
    """TODO
    
    :param name: TODO
    :param source_class: TODO"""
    return type(name, source_class.__bases__, dict([(k, v) for k, v in source_class.__dict__.items()
                                                    if not k in ('__dict__', '__module__', '__weakref__', '__doc__')]))
                                                    
def moduleClasses(m):
    """TODO
    
    :param m: TODO"""
    modulename = m.__name__
    return [x for x in dir(m) if (not x.startswith('__')) and  getattr(getattr(m, x), '__module__', None) == modulename]
        
def classMixin(target_class, source_class, methods=None, only_callables=True,
               exclude='js_requires,css_requires,py_requires', **kwargs):
    """Add to the class methods from 'source'.
    
    :param target_class: TODO
    :param source_class: TODO
    :param methods: TODO
    :param only_callables: TODO
    :param exclude: TODO. If not *methods* then all methods are added"""
    if isinstance(methods, basestring):
        methods = methods.split(',')
    if isinstance(exclude, basestring):
        exclude = exclude.split(',')
    if isinstance(source_class, basestring):
        if ':' in source_class:
            modulename, clsname = source_class.split(':')
        else:
            modulename, clsname = source_class, '*'
        m = gnrImport(modulename, avoidDup=True)
        if m is None:
            raise GnrException('cannot import module: %s' % modulename)
        if clsname == '*':
            classes = moduleClasses(m)
        else:
            classes = [clsname]
        for clsname in classes:
            source_class = getattr(m, clsname, None)
            if source_class:
                classMixin(target_class, source_class, methods=methods,
                            only_callables=only_callables, exclude=exclude, **kwargs)
        return
    if source_class is None:
        return
    if hasattr(source_class, '__py_requires__'):
        py_requires_iterator = source_class.__py_requires__(target_class, **kwargs)
        for cls_address in py_requires_iterator:
            classMixin(target_class, cls_address, methods=methods,
                       only_callables=only_callables, exclude=exclude, **kwargs)
    exclude_list = dir(type) + ['__weakref__', '__onmixin__', '__on_class_mixin__', '__py_requires__','proxy']
    if exclude:
        exclude_list.extend(exclude)
    mlist = [k for k in dir(source_class) if
             ((only_callables and callable(getattr(source_class, k))) or not only_callables) and not k in exclude_list]
    if methods:
        mlist = filter(lambda item: item in FilterList(methods), mlist)
    if exclude:
        mlist = filter(lambda item: item not in FilterList(exclude), mlist)
    proxy = getattr(source_class, 'proxy', None)
    if proxy:
        if proxy==True:
            proxy = source_class.__name__.lower()
        proxy_class = getattr(target_class, '%s_proxyclass'%proxy, None)
        if not proxy_class:
            proxy_class = BaseProxy
            setattr(target_class,'%s_proxyclass'%proxy,proxy_class)
        target_class = proxy_class
    __mixin_pkg = getattr(source_class, '__mixin_pkg', None)
    __mixin_path = getattr(source_class, '__mixin_path', None)
    for name in mlist:
        original = target_class.__dict__.get(name)
        
        base_generator = base_visitor(source_class)
        new = None
        found = False
        while not found:
            base_class = base_generator.next()
            if name in base_class.__dict__:
                new = base_class.__dict__.get(name)
                found = True
        if callable(new):
            new.proxy_name = proxy
            new.__mixin_pkg = __mixin_pkg
            new.__mixin_path = __mixin_path
        if getattr(new,'mixin_as',None):
            mixin_as = new.mixin_as.replace('#',str(id(source_class)))
            setattr(target_class, new.mixin_as, new)
        else:
            setattr(target_class, name, new)
            if original:
                setattr(target_class, '%s_' % name, original)
    if hasattr(source_class, '__on_class_mixin__'):
        source_class.__on_class_mixin__(target_class, **kwargs)
        
def base_visitor(cls):
    """TODO
    
    :param cls: TODO"""
    yield cls
    for base in cls.__bases__:
        for inner_base in base_visitor(base):
            yield inner_base
            
@extract_kwargs(mangling=True)       
def instanceMixin(obj, source, methods=None, attributes=None, only_callables=True,
                  exclude='js_requires,css_requires,py_requires',
                  prefix=None, suffix=None, mangling_kwargs=None,_mixined=None,**kwargs):
    """Add to the instance obj methods from 'source'
    
    ``instanceMixin()`` method is decorated with the :meth:`extract_kwargs <gnr.core.gnrdecorator.extract_kwargs>` decorator
    
    :param obj: TODO
    :param source: it can be an instance or a class
    :param methods: If ``None``, then all methods are added
    :param attributes: TODO
    :param only_callables: boolean. TODO
    :param exclude: TODO
    :param prefix: TODO
    :param mangling_kwargs: TODO"""
    
    if _mixined is None:
        _mixined=[]
    if isinstance(methods, basestring):
        methods = methods.split(',')
    if isinstance(exclude, basestring):
        exclude = exclude.split(',')
    exclude = exclude or ''
    if isinstance(source, basestring):
        if ':' in source:
            modulename, clsname = source.split(':')
        else:
            modulename, clsname = source, '*'
        m = gnrImport(modulename, avoidDup=True)
        if m is None:
            raise GnrException('cannot import module: %s' % modulename)
        if clsname == '*':
            classes = moduleClasses(m)
        else:
            classes = [clsname]
        for clsname in classes:
            source = getattr(m, clsname, None)
            if source:
                instanceMixin(obj, source, methods=methods, only_callables=only_callables, exclude=exclude, 
                         prefix=prefix, suffix=suffix,_mixined=_mixined, **kwargs)
        return _mixined
    if source is None:
        return
    source_dir = dir(source)
    mlist = [k for k in source_dir if
             callable(getattr(source, k)) and not k in dir(type) + ['__weakref__', '__onmixin__','mixin']]
    instmethod = type(obj.__init__)
    if methods:
        mlist = filter(lambda item: item in FilterList(methods), mlist)
    if exclude:
        mlist = filter(lambda item: item not in FilterList(exclude), mlist)
    __mixin_pkg = getattr(source, '__mixin_pkg', None)
    __mixin_path = getattr(source, '__mixin_path', None)
    for name in mlist:
        method = getattr(source, name).im_func
        method.__mixin_pkg = __mixin_pkg
        method.__mixin_path = __mixin_path
        k = instmethod(method, obj, obj.__class__)
        curr_prefix = prefix
        name_as = name
        if mangling_kwargs and '_' in name:
            splitted_name=name.split('_',1)
            mangling = mangling_kwargs.get(splitted_name[0],None)
            if mangling:
                curr_prefix=mangling
                name=splitted_name[1]
        if curr_prefix:
            name_as = '%s_%s' % (curr_prefix, name)
        if suffix:
            name_as = '%s_%s' % (name_as, suffix)
        if hasattr(obj, name_as):
            original = getattr(obj, name_as)
            setattr(obj, name_as + '_', original)
        setattr(obj, name_as, k)
        _mixined.append(name_as)
    if not only_callables:
        attributes = [k for k in source_dir if
                      not callable(getattr(source, k)) and not k.startswith('_') and not k in exclude]
    if attributes:
        if isinstance(attributes, basestring):
            attributes = attributes.split(',')
        for attribute in attributes:
            if hasattr(source, attribute):
                setattr(obj, attribute, getattr(source, attribute))
    if hasattr(source, '__onmixin__'):
        source.__onmixin__.im_func(obj, _mixinsource=source, **kwargs)
    return _mixined
    
def safeStr(self, o):
    """Return a safe string
    
    :param o: the string to be checked"""
    if isinstance(o, unicode):
        return o.encode('UTF-8', 'ignore')
    else:
        return str(o)
        
#def checkGarbage():
#    gc.collect()
#    assert not gc.garbage

class GnrExpandible(object):
    """TODO"""
    def __onmixin__(self, **kwargs):
        self.__expanders = []
        
    def addExpander(self, expander):
        """TODO
        
        :param expander: TODO
        """
        if not expander in self.__expanders:
            expander.parent = self
            #expander.parent=weakref.ref(self)
            self.__expanders.insert(0, expander)
            
    def delExpander(self, expander):
        """TODO
        
        :param expander: TODO
        """
        self.__expanders.remove(expander)
        
    def __getattr__(self, attr):
        for expander in self.__expanders:
            if hasattr(expander, attr):
                return getattr(expander, attr)
                
def instanceOf(obj, *args, **kwargs):
    """TODO
    
    :param obj: TODO"""
    if isinstance(obj, basestring):
        modulename, clsname = obj.split(':')
        m = gnrImport(modulename)
        return getattr(m, clsname)(*args, **kwargs)
    elif isinstance(obj, type): # is a class, not an instance
        return obj(*args, **kwargs)
    else:
        return obj
        
def errorTxt():
    """TODO"""
    el = sys.exc_info()
    tb_text = traceback.format_exc()
    e = el[2]
    while e.tb_next:
        e = e.tb_next
        
    locals_list = []
    for k, v in e.tb_frame.f_locals.items():
        try:
            from gnr.core.gnrstring import toText
            strvalue = toText(v)
        except:
            strvalue = 'unicode error'
        locals_list.append('%s: %s' % (k, strvalue))
    return u'%s\n\nLOCALS:\n\n%s' % (tb_text, '\n'.join(locals_list))
        
def errorLog(proc_name, host=None, from_address='', to_address=None, user=None, password=''):
    """Report the error log
    
    :param proc_name: the name of the wrong process
    :param host: the database server host
    :param from_address: the email sender
    :param to_address: the email receiver
    :param user: the username
    :param password: the username's password"""
    from gnr.utils.gnrmail import sendmail
        
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S: ')
    title = '%s - Error in %s' % (ts, proc_name)
    print title
    tb_text = errorTxt()
    print tb_text.encode('ascii', 'ignore')
        
    if (host and to_address):
        try:
            sendmail(host=host,
                     from_address=from_address,
                     to_address=to_address,
                     subject=title,
                     body=tb_text,
                     user=user,
                     password=password
                     )
        except:
            pass
    return tb_text

def _waitChild(status_dict = None, exit_timeout = 60):
    elapsed = 0
    while True:
        if status_dict['ended'] or (exit_timeout and elapsed > exit_timeout):
            break
        time.sleep(1)
        elapsed +=1

def _calledAync(call=None, call_args=None, call_kwargs=None, cb=None, cb_args=None, cb_kwargs=None, status_dict=None):
    status_dict['running'] = True
    status_dict['ended'] = False
    call_args = call_args or ()
    call_kwargs = call_kwargs or {}
    call_result = call(*call_args, **call_kwargs)
    if cb:
        cb_args = cb_args or ()
        cb_kwargs = cb_kwargs or {}
        cb_kwargs['result'] = call_result
        cb(*cb_args, **cb_kwargs)
    status_dict['running'] = False
    status_dict['ended'] = True

def callAsync(call=None, call_args=None, call_kwargs=None, cb=None, cb_args=None, cb_kwargs=None, exit_timeout = 60):
    """Calls a method in a separate thread

    :param call: callable, the method to run in the thread
    :param call_args: args tuple for the method invocation
    :param call_kwargs: kwargs dict for the method invocation
    :param cb: callback to be called after method execution
    :param cb_args: args tuple for the callback invocation
    :param cb_kwargs: kwargs dict for the callback invocation
    :param exit_timeout: max seconds to wait if the main process 
            is exiting and 'call' is not yet completed. 0 or None waits forether

    """
    thread_params = dict(call=call, call_args=call_args, cb=cb, cb_args=cb_args, cb_kwargs=cb_kwargs)
    status_dict = dict(running=False, ended=False)
    thread_params['status_dict'] = status_dict
    thread.start_new_thread(_calledAync,(),thread_params)
    atexit.register(_waitChild,status_dict=status_dict, exit_timeout=exit_timeout)


if __name__ == '__main__':
    pass