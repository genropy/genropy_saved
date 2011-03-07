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

from gnr.core import gnrstring
from gnr.core.gnrdict import dictExtract
import uuid
import base64
import time

thread_ws = dict()

class FilterList(list):
    """add???"""
    def __contains__(self, item):
        return len([k for k in self if k == item or k.endswith('*') and item.startswith(k[0:-1])]) > 0

def thlocal():
    """add???"""
    return thread_ws.setdefault(thread.get_ident(), {})
        
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used.
    
    :param func: the function to deprecate
    :returns: add???
    """
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
        
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc
        
def extract_kwargs(_adapter=None,**extract_kwargs):
    def decore(func):
        def newFunc(self,*args, **kwargs):
            if _adapter:
                adapter=getattr(self,_adapter)
                if adapter:
                    adapter(kwargs)
            for extract_key,extract_value in extract_kwargs.items():
                grp_key='%s_kwargs' %extract_key
                curr=kwargs.pop(grp_key,dict())
                dfltExtract=dict(slice_prefix=True,pop=False)
                if extract_value is True:
                    dfltExtract['pop']=True
                elif isinstance(extract_value,dict):
                    dfltExtract.update(extract_value)
                curr.update(dictExtract(kwargs,'%s_' %extract_key,**dfltExtract))
                kwargs[grp_key] = curr
            return func(self,*args,**kwargs)
        return newFunc
    return decore
    
def boolean(x):
    """add???
    
    :param x: add???
    """
    if isinstance(x, basestring):
        x = x.upper()
        if x in ('TRUE', 'T', 'Y', 'YES', '1'):
            return True
        if x in ('FALSE', 'F', 'N', 'NO', '0'):
            return False
    return bool(x)
    
def objectExtract(myobj, f):
    """add???
    
    :param myobj: add???
    :param f: add???
    :returns: add???
    """
    lf = len(f)
    return dict([(k[lf:], getattr(myobj, k)) for k in dir(myobj) if k.startswith(f)])
    
def importModule(module):
    """add???
    
    :param module: add???
    :returns: add???
    """
    if module not in sys.modules:
        __import__(module)
    return sys.modules[module]
    
def debug_call(func):
    """add???
    
    :param func: add???
    :returns: add???
    """
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
    
def timer_call(time_list=None, print_time=True):
    """add???
    
    :param time_list: add???. Default value is ``None``
    :param print_time: add???. Default value is ``True``
    :returns: add???
    """
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
    
def metadata(**kwargs):
    """add???
    
    :returns: add???
    """
    def decore(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func
        
    return decore
    
def getUuid():
    """add???
    
    :returns: add???
    """
    return base64.urlsafe_b64encode(uuid.uuid3(uuid.uuid1(), str(thread.get_ident())).bytes)[0:22]
    
def safe_dict(d):
    """Use the str method, coercing all the dict keys into a string type
    
    :param d: a dict
    :returns: the dict with string-type keys
    """
    return dict([(str(k), v) for k, v in d.items()])
    
def uniquify(seq):
    """add???
    
    :param seq: add???
    :returns: add???
    """
    def seen_function(seq):
        seen = set()
        for x in seq:
            if x in seen:
                continue
            seen.add(x)
            yield x
            
    return list(seen_function(seq))
            
def optArgs(**kwargs):
    """add???
    
    :returns: add???
    """
    return dict([(k, v) for k, v in kwargs.items() if v != None])
            
def moduleDict(module, proplist):
    """add???
    
    :param module: add???
    :param proplist: add???
    :returns: add???
    """
    result = {}
    if isinstance(module, basestring):
        module = gnrImport(module)
    for prop in [x.strip() for x in proplist.split(',')]:
        modulelist = [getattr(module, x) for x in dir(module) if
                      hasattr(getattr(module, x), prop) and getattr(getattr(module, x), '__module__',
                                                                    None) == module.__name__]
        result.update(dict([(getattr(x, prop).lower(), x) for x in modulelist]))
    return result
    
def gnrImport(source, importAs=None, avoidDup=False):
    """add???
    
    :param source: add???
    :param importAs: add???. Default value is ``None``
    :param avoidDup: if ``True``, allow to avoid duplicates. Default value is ``False``
    :returns: add???
    """
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
        except Exception, e:
            module = None
            error = e
        finally:
            if module_file:
                module_file.close()
            if imp.lock_held():
                imp.release_lock()
            if error:
                raise
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
        """add???
        
        :param localizer: add???
        """
        self.localizer = localizer
        
    def localize(self, v):
        """add???
        
        :param v: add???
        """
        return self.localizer.translateText(v[2:])
        
    def localizedMsg(self, msg, msgargs):
        """add???
        
        :param msg: add???
        :param msgargs: add???
        """
        if self.localizer:
            msg = self.localize(msg)
            for k, v in msgargs.items():
                if isinstance(v, basestring) and v.startswith('!!'):
                    msgargs[k] = self.localize(msgargs[k])
        return msg % msgargs % msgargs # msgargs is use 2 times as we could have msgargs nested(max 1 level)
        
class NotImplementedException(GnrException):
    pass
        
class GnrObject(object):
    """add???"""
    def __init__(self):
        pass
        
    def mixin(self, cls, **kwargs):
        """add???
        
        :param cls: add???
        """
        if isinstance(cls, basestring):
            modulename, cls = cls.split(':')
            m = gnrImport(modulename)
            if m != None:
                cls = getattr(m, cls)
            else:
                raise GnrException('cannot import module: %s' % modulename)
        instanceMixin(self, cls, **kwargs)
        
class GnrImportedModule(object):
    """add???"""
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
        """get the path of the module
        
        :returns: the path
        """
        return self.path
        
    def getModule(self):
        """get the module
        
        :returns: the module
        """
        return self.module
        
    def getName(self):
        """add???
        
        :returns: add???
        """
        return self.name
        
    def getDoc(self, memberName=None):
        """add???
        
        :param memberName: add???. Default value is ``memberName``
        :returns: add???
        """
        m = self.module
        if memberName:
            m = self.getMember(memberName)
        if m:
            doc = m.__doc__
        if doc: doc = unicode(doc, 'UTF-8')
        else: doc = ""
        return doc
        
    def getMember(self, memberName):
        """add???
        
        :param memberName: add???
        :returns: add???
        """
        return getattr(self.module, memberName, None)
        
    #    def getImportedMember(self, memberName):
    #        return ImportedMember(self, memberName)
        
    def load(self):
        """add???"""
        if self.path.endswith('py'):
            self.module = imp.load_source(self.name, self.path)
        else:
            self.module = imp.load_compiled(self.name, self.path)
            #globals()[self.name]=self.module
            
    def update(self):
        """add???"""
        self.load()
        
class GnrAddOn(object):
    """A class to be subclassed to inherit some introspection methods"""
        
    def className(self):
        """The class name
        
        :returns: the class name
        """
        return self.__class__.__name__
        
    def recorderReset(self):
        """add???"""
        self.__recorder__ = []
        
    def recorderWrite(self):
        """add???"""
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
        """add???
        
        :returns: add???
        """
        return self.__recorder__
        
    def recorderDo(self, recorder=None):
        """add???
        
        :param recorder: add???. Default value is ``None``
        :returns: add???
        """
        if not recorder: recorder = self.__recorder__[:]
        result = []
        for command, args, kwargs in recorder:
            commandHandler = getattr(self, command)
            result.append(commandHandler(*args, **kwargs))
        return result
        
    def superdo(self, *args, **kwargs):
        """like calling :meth:`super()` with the right arguments
        
        ??? check if it works on multiple levels
        
        :returns: add???
         """
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
        """add???
        
        :param src: is a string of a python function or an imported function
        :param importAs: a name for identify the function in error messages. Default value is ``None``
        :param bound: boolean. If ``True`` the function will be bounded to this instance. Default value is ``True``
        """
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
    """add???"""
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
        """add???
        
        :param name: add???. Default value is ``None``.
        """
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
        """add???
        
        :param cls: add???
        :returns: add???
        """
        #return [v() for v in cls._gnr_members__.values()]
        return [v for v in cls._gnr_members__.values()]
        
    rememberedMembers = classmethod(rememberedMembers)
        
    def rememberedNamedMembers(cls):
        """add???
        
        :param cls: add???
        :returns: add???
        """
        #return dict([(name,cls._gnr_members__[objid]()) for  name,objid in cls._gnr_namedmembers__.items()])
        return dict([(name, cls._gnr_members__[objid]) for  name, objid in cls._gnr_namedmembers__.items()])
        
    rememberedNamedMembers = classmethod(rememberedNamedMembers)
        
    def rememberedGet(cls, name):
        """add???
        
        :param cls: add???
        :param name: add???
        :returns: add???
        """
        objid = cls._gnr_namedmembers__.get(name, None)
        #if objid:return cls._gnr_members__[objid]()
        if objid: return cls._gnr_members__[objid]
        
    rememberedGet = classmethod(rememberedGet)
        
class GnrMetaString(object):
    """add???"""
    _glossary = {}
        
    def glossary(cls):
        """add???
        
        :param cls: add???
        :returns: add???
        """
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
    """add???"""
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
    """add???
    
    :param obj: add???
    :param method: add???
    """
    name = method.__name__
    setattr(obj, name, method)
        
def addBoundCallable(obj, method, importAs=None):
    """add???
    
    :param obj: add???
    :param method: add???
    :param importAs: add???. Default value is ``None``
    """
    z = type(obj.__init__)
    k = z(method, obj, obj.__class__)
    if not importAs:
        importAs = method.__name__
    setattr(obj, importAs, k)
        
def setMethodFromText(obj, src, importAs):
    """add???
    
    :param obj: add???
    :param src: add???
    :param importAs: add???
    """
    compiled = compile(src, 'xyz', 'exec')
    auxDict = {}
    exec compiled in auxDict
    addBoundCallable(obj, auxDict[importAs], importAs)
        
def getObjCallables(obj):
    """add???
    
    :param obj: add???
    :returns: add???
    """
    return [(k, getattr(obj, k))  for k in dir(obj) if
            callable(getattr(obj, k)) and not k in ('__call__', '__class__', '__cmp__')]
            
def getObjAttributes(obj):
    """add???
    
    :param obj: add???
    :returns: add???
    """
    return [(k, getattr(obj, k))  for k in dir(obj) if not callable(getattr(obj, k))]
        
def callables(obj):
    """add???
    
    :param obj: add???
    :returns: add???
    """
    s = getObjCallables(obj)
    return '\n'.join([x for x, v in s])
        
def testbound(self, n):
    """add???
    
    :param n: add???
    :returns: add???
    """
    self.special = n * '-'
    return self.special
        
def compareInstances(a, b, __visited=None):
    """add???
    
    :param a: add???
    :param b: add???
    :param _visited: add???. Default value is ``None``
    :returns: add???
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
    """add???"""
    return (args, kwargs)
    
def setCallable(obj, name, argstring=None, func='pass'):
    """add???
    
    :param obj: add???
    :param name: add???
    :param argstring: add???. Default value is ``None``
    :param func: add???. Default value is ``pass``
    """
    body = '    ' + '\n    '.join(func.split('\n'))
    if argstring:
        argstring = ',' + argstring
    else:
        argstring = ''
    f = "def %s(self%s):\n%s" % (name, argstring, body)
    setMethodFromText(obj, f, name)
        
def cloneClass(name, source_class):
    """add???
    
    :param name: add???
    :param source_class: add???
    :returns: add???
    """
    return type(name, source_class.__bases__, dict([(k, v) for k, v in source_class.__dict__.items()
                                                    if not k in ('__dict__', '__module__', '__weakref__', '__doc__')]))
                                                    
def moduleClasses(m):
    """add???
    
    :param m: add???
    :returns: add???
    """
    modulename = m.__name__
    return [x for x in dir(m) if (not x.startswith('__')) and  getattr(getattr(m, x), '__module__', None) == modulename]
        
def classMixin(target_class, source_class, methods=None, only_callables=True,
               exclude='js_requires,css_requires,py_requires', **kwargs):
    """Add to the class methods from 'source'.
    
    :param target_class: add???
    :param source_class: add???
    :param methods: add???. Default value is ``None``
    :param only_callables: add???. Default value is ``True``
    :param exclude: add???. Default value is ``js_requires,css_requires,py_requires``
    If not 'methods' all methods are added.  
    """
    if isinstance(methods, basestring):
        methods = methods.split(',')
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
    exclude_list = dir(type) + ['__weakref__', '__onmixin__', '__on_class_mixin__', '__py_requires__']
    if exclude:
        exclude_list.extend(exclude.split(','))
    mlist = [k for k in dir(source_class) if
             ((only_callables and callable(getattr(source_class, k))) or not only_callables) and not k in exclude_list]
    if methods:
        mlist = filter(lambda item: item in FilterList(methods), mlist)
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
        setattr(target_class, name, new)
        if original:
            setattr(target_class, '%s_' % name, original)
    if hasattr(source_class, '__on_class_mixin__'):
        source_class.__on_class_mixin__(target_class, **kwargs)
        
def base_visitor(cls):
    """add???
    
    :param cls: add???
    """
    yield cls
    for base in cls.__bases__:
        for inner_base in base_visitor(base):
            yield inner_base
            
def instanceMixin(obj, source, methods=None, attributes=None, only_callables=True,
                  exclude='js_requires,css_requires,py_requires', prefix=None, **kwargs):
    """Add to the instance obj methods from 'source'.
    
    :param obj: add???
    :param source: it can be an instance or a class
    :param methods: If ``None``, then all methods are added. Default value is ``None``
    :param attributes: add???. Default value is ``None``
    :param only_callables: add???. Default value is ``True``
    :param exclude: add???. Default value is ``js_requires,css_requires,py_requires``
    :param prefix: add???. Default value is ``None``
    :returns: add???
    """
    if isinstance(methods, basestring):
        methods = methods.split(',')
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
            instanceMixin(obj, source, methods=methods, only_callables=only_callables, exclude=exclude, prefix=prefix,
                          **kwargs)
        return
    if source is None:
        return
        
    mlist = [k for k in dir(source) if
             callable(getattr(source, k)) and not k in dir(type) + ['__weakref__', '__onmixin__']]
    instmethod = type(obj.__init__)
    if methods:
        mlist = filter(lambda item: item in FilterList(methods), mlist)
    for name in mlist:
        method = getattr(source, name).im_func
        k = instmethod(method, obj, obj.__class__)
        name_as = name
        if prefix:
            name_as = '%s_%s' % (prefix, name)
        if hasattr(obj, name_as):
            original = getattr(obj, name_as)
            setattr(obj, name_as + '_', original)
        setattr(obj, name_as, k)
    if not only_callables:
        exclude = (exclude or '').split(',')
        attributes = [k for k in dir(source) if
                      not callable(getattr(source, k)) and not k.startswith('_') and not k in exclude]
    if attributes:
        if isinstance(attributes, basestring):
            attributes = attributes.split(',')
        for attribute in attributes:
            if hasattr(source, attribute):
                setattr(obj, attribute, getattr(source, attribute))
    if hasattr(source, '__onmixin__'):
        source.__onmixin__.im_func(obj, _mixinsource=source, **kwargs)
        
def safeStr(self, o):
    """add???
    
    :param o: add???
    :returns: a "safe" string
    """
    if isinstance(o, unicode):
        return o.encode('UTF-8', 'ignore')
    else:
        return str(o)
        
#def checkGarbage():
#    gc.collect()
#    assert not gc.garbage

class GnrExpandible(object):
    """add???"""
    def __onmixin__(self, **kwargs):
        self.__expanders = []
        
    def addExpander(self, expander):
        """add???
        
        :param expander: add???
        """
        if not expander in self.__expanders:
            expander.parent = self
            #expander.parent=weakref.ref(self)
            self.__expanders.insert(0, expander)
            
    def delExpander(self, expander):
        """add???
        
        :param expander: add???
        """
        self.__expanders.remove(expander)
        
    def __getattr__(self, attr):
        for expander in self.__expanders:
            if hasattr(expander, attr):
                return getattr(expander, attr)
                
def instanceOf(obj, *args, **kwargs):
    """add???
    
    :param obj: add???
    :returns: the object
    """
    if isinstance(obj, basestring):
        modulename, clsname = obj.split(':')
        m = gnrImport(modulename)
        return getattr(m, clsname)(*args, **kwargs)
    elif isinstance(obj, type): # is a class, not an instance
        return obj(*args, **kwargs)
    else:
        return obj
        
def errorTxt():
    """add???
    
    :returns: add???
    """
    el = sys.exc_info()
    tb_text = traceback.format_exc()
    e = el[2]
    while e.tb_next:
        e = e.tb_next
        
    locals_list = []
    for k, v in e.tb_frame.f_locals.items():
        try:
            strvalue = gnrstring.toText(v)
        except:
            strvalue = 'unicode error'
        locals_list.append('%s: %s' % (k, strvalue))
    return u'%s\n\nLOCALS:\n\n%s' % (tb_text, '\n'.join(locals_list))
        
def errorLog(proc_name, host=None, from_address='', to_address=None, user=None, password=''):
    """add???
    
    :param proc_name: add???
    :param host: add???. Default value is ``None``
    :param from_address: add???. Default value is `` ``
    :param to_address: add???. Default value is ``None``
    :param user: add???. Default value is ``None``
    :param password: add???. Default value is `` ``
    :returns: add???
    """
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
        
if __name__ == '__main__':
    pass