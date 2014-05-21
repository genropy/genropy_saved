#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package       : GenroPy web - see LICENSE for details
# module gnrsqlclass : Genro Web structures implementation
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

#import weakref

from gnr.core.gnrbag import Bag,BagCbResolver,DirectoryResolver
from gnr.core.gnrstructures import GnrStructData
from gnr.core import gnrstring
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import extract_kwargs,deprecated

from time import time
from copy import copy



def cellFromField(field,tableobj):
    kwargs = dict()
    fldobj = tableobj.column(field)
    fldattr = dict(fldobj.attributes or dict())
    if 'values' in fldattr:
        kwargs['values'] = fldattr['values']
    kwargs.update(dictExtract(fldattr,'cell_'))
    kwargs.setdefault('format_pattern',fldattr.get('format'))
    kwargs.update(dictExtract(fldattr,'format_',slice_prefix=False))
    if getattr(fldobj,'sql_formula',None) and fldobj.sql_formula.startswith('@') and '.(' in fldobj.sql_formula:
        kwargs['_subtable'] = True
    kwargs['name'] =  fldobj.name_short or fldobj.name_long
    kwargs['dtype'] =  fldobj.dtype
    kwargs['width'] = '%iem' % int(fldobj.print_width*.6) if fldobj.print_width else None
    relfldlst = tableobj.fullRelationPath(field).split('.')
    kwargs.update(dictExtract(fldobj.attributes,'validate_',slice_prefix=False))
    #if 'values' in fldobj.attributes:
    #    kwargs['values']=fldobj.attributes['values']
    if hasattr(fldobj,'relatedColumnJoiner'):
        columnjoiner = fldobj.relatedColumnJoiner()
        if columnjoiner:
            relatedTable = fldobj.relatedColumn().table
            kwargs['related_table'] = relatedTable.fullname
            kwargs['related_table_lookup'] = relatedTable.attributes.get('lookup')
            if len(relfldlst) == 1:
                caption_field = kwargs.pop('caption_field',None) or relatedTable.attributes.get('caption_field')
                if caption_field and not kwargs.get('hidden'):
                    rel_caption_field = '@%s.%s' %(field,caption_field)
                    caption_fieldobj = tableobj.column(rel_caption_field)
                    kwargs['width'] = '%iem' % int(caption_fieldobj.print_width*.6) if caption_fieldobj.print_width else None
                    kwargs['caption_field'] = rel_caption_field
                    caption_field_kwargs = cellFromField(rel_caption_field,tableobj)
                    if '_joiner_storename' in caption_field_kwargs:
                        kwargs['_joiner_storename'] = caption_field_kwargs['_joiner_storename']
                        kwargs['_external_fkey'] = caption_field_kwargs['_external_fkey']
                        kwargs['_external_name'] = caption_field_kwargs['_external_name']
                    kwargs['relating_column'] = field
                    kwargs['related_column'] = caption_field
                    kwargs['rowcaption'] = caption_field

    if len(relfldlst) > 1:
        fkey = relfldlst[0][1:]
        kwargs['relating_column'] = fkey
        kwargs['related_column'] = '.'.join(relfldlst[1:])
        fkeycol=tableobj.column(fkey)
        if fkeycol is not None:
            joiner = fkeycol.relatedColumnJoiner()
            ext_fldname = '.'.join(relfldlst[1:])
            if 'storefield' in joiner:
                externalStore(tableobj,field,joiner,fkey,ext_fldname,kwargs)
            elif '_storename' in joiner:
                externalStore(tableobj,field,joiner,fkey,ext_fldname,kwargs)
    return kwargs


def externalStore(tableobj,field,joiner,fkey,ext_fldname,kwargs):
    ext_table = '.'.join(joiner['one_relation'].split('.')[0:2])
    storefield = joiner.get('storefield')
    kwargs['_joiner_storename'] = storefield if storefield else " '%s' " % (joiner.get('_storename') or tableobj.db.rootstore)
    kwargs['_external_fkey'] ='$%s AS %s_fkey' %(fkey,ext_table.replace('.','_'))
    if not ext_fldname.startswith('@'):
        ext_fldname = '$%s' %ext_fldname
    kwargs['_external_name'] = '%s:%s AS %s' %(ext_table,ext_fldname,field.replace('.','_').replace('@','_'))

    
    
class StructMethodError(Exception):
    pass
    
def struct_method(func_or_name):
    """A decorator. Allow to register a new method (in a page or in a component)
    that will be available in the web structs::
        
        @struct_method
        def includedViewBox(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.includedViewBox(...)
            
    If the method name includes an underscore, only the part that follows the first
    underscore will be the struct method's name::
        
        @struct_method
        def iv_foo(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.foo(...)
            
    You can also pass a name explicitly::
        
        @struct_method('bar')
        def foo(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.bar(...)"""
    def register(name, func):
        func_name = func.__name__
        existing_name = GnrDomSrc._external_methods.get(name, None)
        if existing_name and (existing_name != func_name):
            # If you want to override a struct_method, be sure to call its implementation method in the same way as the original.
            # (Otherwise, the result would NOT  be well defined due to uncertainty in the mixin process at runtime plus the fact that the GnrDomSrc is global)
            raise StructMethodError(
                    "struct_method %s is already tied to implementation method %s" % (repr(name), repr(existing_name)))
        GnrDomSrc._external_methods[name] = func_name
        
    if isinstance(func_or_name, basestring):
        name = func_or_name
        
        def decorate(func):
            register(name, func)
            return func
            
        return decorate
    else:
        name = func_or_name.__name__
        if '_' in name:
            name = name.split('_', 1)[1]
        register(name, func_or_name)
        return func_or_name
    
class GnrDomSrcError(Exception):
    pass

class GnrDomElem(object):
    def __init__(self, obj, tag):
        self.obj = obj
        self.tag = tag

    def __call__(self, *args, **kwargs):
        child = self.obj.child(self.tag, *args, **kwargs)
        return child

class GnrDomSrc(GnrStructData):
    """GnrDomSrc class"""
    _external_methods = dict()
    
    def js_sourceNode(self,mode=''):
        return "==pyref('%s','%s')" % (self.attributes.setdefault('__ref','%s_%i' % (self.parentNode.attr.get('tag',''),id(self.parentNode))),mode)

    @property
    def js_widget(self):
        """TODO"""
        return self.js_sourceNode('w')
    
    @property
    def js_domNode(self):
        """TODO"""
        return self.js_sourceNode('d')
        
    @property
    def js_form(self):
        """TODO"""
        return self.js_sourceNode('f')
    
    def makeRoot(cls, page, source=None):
        """Build the root through the :meth:`makeRoot()
        <gnr.core.gnrstructures.GnrStructData.makeRoot>` method and return it
        
        :param cls: the structure class
        :param page: the webpage instance
        :param source: the filepath of the xml file"""
        root = GnrStructData.makeRoot(source=source, protocls=cls)
        root._page = page
        return root
    makeRoot = classmethod(makeRoot)

    def _get_page(self):
        return self.root._page
    page = property(_get_page)
    
    def checkNodeId(self, nodeId):
        """Check if the :ref:`nodeid` is already existing or not
        
        :param nodeId: the :ref:`nodeid`"""
        assert not nodeId in self.register_nodeId,'%s is duplicated' %nodeId
        self.page._register_nodeId[nodeId] = self
        
    @property
    def register_nodeId(self):
        """TODO"""
        if not hasattr(self.page,'_register_nodeId'):
            register = dict()
            self.page._register_nodeId = register
        return self.page._register_nodeId
        
    def _get_parentfb(self):
        if hasattr(self, 'fbuilder'):
            return self.fbuilder
        elif self.parent:
            return self.parent.parentfb
    parentfb = property(_get_parentfb)
            
    def __getattr__(self, fname): 
        fnamelower = fname.lower()
        if (fname != fnamelower) and hasattr(self, fnamelower):
            return getattr(self, fnamelower)
        if fnamelower in self.genroNameSpace:
            return GnrDomElem(self, '%s' % (self.genroNameSpace[fnamelower]))
        if fname in self._external_methods:
            handler = getattr(self.page, self._external_methods[fname])
            return lambda *args, **kwargs: handler(self, *args,**kwargs)
        attachnode = self.getNode(fname)
        if attachnode:
            return attachnode._value
        autoslots = self._parentNode.attr.get('autoslots')
        if autoslots:
            autoslots = autoslots.split(',')
            if fname in autoslots:
                return self.child('autoslot',childname=fname)
        parentTag = self._parentNode.attr.get('tag','').lower()
        if parentTag and not fnamelower.startswith(parentTag):
            subtag = ('%s_%s' %(parentTag,fname)).lower()
            if hasattr(self,subtag):
                return getattr(self,subtag)
        raise AttributeError("Object has no attribute '%s': provide another nodeId" % fname)
    
    @deprecated
    def getAttach(self, childname):
        """.. warning:: deprecated since version 0.7"""
        childnode = self.getNode(childname)
        if childnode:
            return childnode._value
        
    def child(self, tag, childname=None, childcontent=None, envelope=None,**kwargs):
        """Set a new item of the ``tag`` type into the current structure through
        the :meth:`child() <gnr.core.gnrstructures.GnrStructData.child>` and return it
        
        :param tag: the html tag
        :param childname: the :ref:`childname`
        :param childcontent: the html content
        :param envelope: TODO"""
        if '_tags' in kwargs and not self.page.application.checkResourcePermission(kwargs['_tags'], self.page.userTags):
            kwargs['__forbidden__'] = True
        if 'fld' in kwargs:
            fld_dict = self.getField(kwargs.pop('fld'))
            fld_dict.update(kwargs)
            kwargs = fld_dict
            t = kwargs.pop('tag', tag)
            if tag == 'input':
                tag = t
        if hasattr(self, 'fbuilder'):
            if not tag in (
            'tr', 'data', 'script', 'func', 'connect', 'dataFormula', 'dataScript', 'dataRpc', 'dataRemote',
            'dataRecord', 'dataSelection', 'dataController'):
                if tag == 'br':
                    return self.fbuilder.br()
                if not 'disabled' in kwargs:
                    if hasattr(self, 'childrenDisabled'):
                        kwargs['disabled'] = self.childrenDisabled
                return self.fbuilder.place(tag=tag, childname=childname, **kwargs)
        if envelope:
            obj = GnrStructData.child(self, 'div', childname='*_#', **envelope)
        else:
            obj = self
        for k,v in kwargs.items():
            if isinstance(v,GnrStructData):
                kwargs[k]=v.js_sourceNode()
        if kwargs.get('nodeId'):
            self.checkNodeId(kwargs['nodeId'])
        sourceNodeValueAttr = dictExtract(kwargs,'attr_')
        serverpath = sourceNodeValueAttr.get('serverpath')
       # dbenv = sourceNodeValueAttr.get('dbenv')
        if serverpath: #or dbenv:
            clientpath = kwargs.get('value') or kwargs.get('src') or kwargs.get('innerHTML')
            if clientpath:
                clientpath = clientpath.replace('^','').replace('=','')
                value=kwargs.get('default_value')
                self.data(clientpath,value,**sourceNodeValueAttr)
        return GnrStructData.child(obj, tag, childname=childname, childcontent=childcontent,**kwargs)
        
    def htmlChild(self, tag, childcontent, value=None, **kwargs):
        """Create an html child and return it
        
        :param tag: the html tag
        :param childcontent: the html content
        :param value: TODO"""
        if childcontent :
            kwargs['innerHTML'] = childcontent
            childcontent = None
        elif value:
            kwargs['innerHTML'] = value
            value = None
        return self.child(tag, childcontent=childcontent, **kwargs)
        
    def nodeById(self, id):
        """TODO
        
        :param id: the :ref:`nodeid`"""
        return self.findNodeByAttr('nodeId', id)
        
    def framepane(self, frameCode=None, centerCb=None, **kwargs):
        """Create a :ref:`framepane` and return it. A framePane is a :ref:`bordercontainer`
        with :ref:`frame_sides` attribute added: these sides follow the Dojo borderContainer
        suddivision: there is indeed the *top*, *bottom*, *left*, *right* and *center* regions
        
        :param frameCode: the framepane code
        :param centerCb: TODO"""
        frameCode = frameCode or 'frame_#'
        if '#' in frameCode:
            frameCode = frameCode.replace('#',self.page.getUuid())
        frame = self.child('FramePane',frameCode=frameCode,autoslots='top,bottom,left,right,center',**kwargs)
        if callable(centerCb):
            centerCb(frame)
        return frame
        
    @property
    def record(self):
        """TODO"""
        assert self.attributes['tag'] == 'FrameForm','only on FrameForm'
        return self.center.contentPane(datapath='.record')
        
    @extract_kwargs(store=True)
    def frameform(self, formId=None, frameCode=None, store=None, storeCode=None,
                  slots=None, table=None, store_kwargs=None, **kwargs):
        """TODO
        
        ``frameform()`` method is decorated with the :meth:`extract_kwargs <gnr.core.gnrdecorator.extract_kwargs>` decorator
        
        :param formId: TODO
        :param frameCode: TODO
        :param store: TODO
        :param storeCode: TODO
        :param slots: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param store_kwargs: TODO"""
        formId = formId or '%s_form' %frameCode
        if not storeCode:
            storeCode = formId
        if not table:
            storeNode = self.root.nodeById('%s_store' %storeCode)
            if storeNode:
                table = storeNode.attr['table']
        centerCb = kwargs.pop('centerCb',None)
        frame = self.child('FrameForm',formId=formId,frameCode=frameCode,
                            namespace='form',storeCode=storeCode,table=table,
                            autoslots='top,bottom,left,right,center',**kwargs)
        if store:
            if store is True:
                store = 'recordCluster'
            store_kwargs['handler'] = store
            frame.formStore(**store_kwargs)
        if callable(centerCb):
            centerCb(frame)
        return frame
        
    def formstore(self, handler='recordCluster', nodeId=None, table=None,
                  storeType=None, parentStore=None, **kwargs):
        """TODO
        
        :param storepath: TODO
        :param handler: TODO
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param storeType: TODO
        :param parentStore: TODO"""
        assert self.attributes.get('tag','').lower()=='frameform', 'formstore can be created only inside a FrameForm'
        storeCode = self.attributes['frameCode']
        self.attributes['storeCode'] = storeCode
        if not storeType:
            if parentStore:
                storeType='Collection'
            else:
                storeType='Item'
        if table:
            self.attributes['table'] = table
        elif 'table' in self.attributes:
            table = self.attributes['table']
        if table:
            tblattr = dict(self.page.db.table(table).attributes)
            tblattr.pop('tag',None)
            self.data('.controller.table',table,**tblattr)
        return self.child('formStore',childname='store',storeCode=storeCode,table=table,
                            nodeId = nodeId or '%s_store' %storeCode,storeType=storeType,
                            parentStore=parentStore,handler=handler,**kwargs)
                            
    def formstore_handler(self, action, handler_type=None, **kwargs):
        """TODO Return the formstore handler
        
        :param action: TODO
        :param handler_type: TODO"""
        return self.child('formstore_handler',childname=action,action=action,handler_type=handler_type,**kwargs)
        
    def formstore_handler_addcallback(self, cb, **kwargs):
        """TODO
        
        :param cb: TODO"""
        self.child('callBack',childcontent=cb,**kwargs)
        return self

    def iframe(self, childcontent=None, main=None, **kwargs):
        """Create an :ref:`iframe` and returns it
        
        :param childcontent: the html content
        :param main: TODO"""
        if main:
            self.attributes.update(dict(overflow='hidden'))
            kwargs['height'] = '100%'
            kwargs['width'] = '100%'
            kwargs['border'] = 0
        return self.htmlChild('iframe', childcontent=childcontent, main=main, **kwargs)
    
    def htmlform(self,childcontent=None,**kwargs):
        return self.htmlChild('form', childcontent=childcontent, **kwargs)

    def h1(self, childcontent=None, **kwargs):
        return self.htmlChild('h1', childcontent=childcontent, **kwargs)
        
    def h2(self, childcontent=None, **kwargs):
        return self.htmlChild('h2', childcontent=childcontent, **kwargs)
        
    def h3(self, childcontent=None, **kwargs):
        return self.htmlChild('h3', childcontent=childcontent, **kwargs)
        
    def h4(self, childcontent=None, **kwargs):
        return self.htmlChild('h4', childcontent=childcontent, **kwargs)
        
    def h5(self, childcontent=None, **kwargs):
        return self.htmlChild('h5', childcontent=childcontent, **kwargs)
        
    def h6(self, childcontent=None, **kwargs):
        return self.htmlChild('h6', childcontent=childcontent, **kwargs)
        
    def li(self, childcontent=None, **kwargs):
        return self.htmlChild('li', childcontent=childcontent, **kwargs)
        
    def td(self, childcontent=None, **kwargs):
        return self.htmlChild('td', childcontent=childcontent, **kwargs)
        
    def th(self, childcontent=None, **kwargs):
        return self.htmlChild('th', childcontent=childcontent, **kwargs)
        
    def span(self, childcontent=None, **kwargs):
        return self.htmlChild('span', childcontent=childcontent, **kwargs)
        
    def pre(self, childcontent=None, **kwargs):
        return self.htmlChild('pre', childcontent=childcontent, **kwargs)
        
    def div(self, childcontent=None, **kwargs):
        return self.htmlChild('div', childcontent=childcontent, **kwargs)
        
    def style(self,childcontent=None,**kwargs):
        return self.htmlChild('style', childcontent=childcontent, **kwargs)

    def a(self, childcontent=None, **kwargs):
        return self.htmlChild('a', childcontent=childcontent, **kwargs)
        
    def dt(self, childcontent=None, **kwargs):
        return self.htmlChild('dt', childcontent=childcontent, **kwargs)
        
    def option(self, childcontent=None, **kwargs):
        return self.child('option', childcontent=childcontent, **kwargs)
        
    def caption(self, childcontent=None, **kwargs):
        return self.htmlChild('caption', childcontent=childcontent, **kwargs)
        
    def button(self, caption=None, **kwargs):
        return self.child('button', caption=caption, **kwargs)
        
   #def column(self, label='', field='', expr='', name='', **kwargs):
   #    if not 'columns' in self:
   #        self['columns'] = Bag()
   #    if not field:
   #        field = label.lower()
   #    columns = self['columns']
   #    name = 'C_%s' % str(len(columns))
   #    columns.setItem(name, None, label=label, field=field, expr=expr, **kwargs)
        
    def tooltip(self, label='', **kwargs):
        """Create a :ref:`tooltip` and return it
        
        :param label: the tooltip text"""
        return self.child('tooltip', label=label, **kwargs)
        
    def data(self, *args, **kwargs):
        """Create a :ref:`data` and returns it. ``data`` allows to define
        variables from server to client
        
        :param \*args: args[0] includes the path of the value, args[1] includes the value
        :param \*\*kwargs: in the kwargs you can insert the ``_serverpath`` attribute. For more
                           information, check the :ref:`data_serverpath` example"""
        value = None
        className = None
        path = None
        if len(args) == 1:
            if not kwargs:
                value = args[0]
                path = None
            else:
                path = args[0]
                value = None
        elif len(args) == 0 and kwargs:
            path = None
            value = None
        elif len(args) > 1:
            value = args[1]
            path = args[0]
        if isinstance(value, dict):
            value = Bag(value)
        if isinstance(value, Bag):
            className = 'bag'
        serverpath = kwargs.pop('serverpath',None) or kwargs.pop('_serverpath',None)
       #dbenv = kwargs.get('dbenv')
       #if dbenv and not serverpath:
       #    serverpath = 'dbenv.%s' %path.split('.')[-1]
        if serverpath:
            self.page.addToContext(serverpath=serverpath,value=value,attr=kwargs)
            kwargs['serverpath'] = serverpath
        return self.child('data', __cls=className,childcontent=value,_returnStruct=False, path=path, **kwargs)
        
    def script(self, content='', **kwargs):
        """Handle the <script> html tag and return it
        
        :param content: the <script> content"""
        return self.child('script', childcontent=content, **kwargs)
        
    def remote(self, method, lazy=True, cachedRemote=None,**kwargs):
        """TODO
        
        :param method: TODO
        :param lazy: boolean. TODO"""
        if callable(method):
            handler = method
        else:
            handler = self.page.getPublicMethod('remote', method)
        if handler:
            kwargs_copy = copy(kwargs)
            parentAttr = self.parentNode.getAttr()
            parentAttr['remote'] = 'remoteBuilder'
            parentAttr['remote_handler'] = method
            if cachedRemote:
                parentAttr['_cachedRemote'] = cachedRemote
            for k, v in kwargs.items():
                if k.endswith('_path'):
                    v = u'§%s' % v
                parentAttr['remote_%s' % k] = v
                kwargs.pop(k)
            if not lazy:
                onRemote = kwargs_copy.pop('_onRemote', None)
                if onRemote:
                    self.dataController(onRemote, _onStart=True)
                handler(self, **kwargs_copy)
                
    def func(self, name, pars='', funcbody=None, **kwargs):
        """TODO
        
        :param name: TODO
        :param pars: TODO
        :param funcbody: TODO"""
        if not funcbody:
            funcbody = pars
            pars = ''
        return self.child('func', childname=name, pars=pars, childcontent=funcbody, **kwargs)
        
    def connect(self, event='', pars='', funcbody=None, **kwargs):
        """TODO
        
        :param event: TODO
        :param pars: TODO
        :param funcbody: TODO"""
        if not (funcbody and pars):
            funcbody = event
            event = ''
            pars = ''
        elif not funcbody:
            funcbody = pars
            pars = ''
        return self.child('connect', event=event, pars=pars, childcontent=funcbody, **kwargs)
        
    def subscribe(self, what, event, func=None, **kwargs):
        """TODO
        
        :param what: TODO
        :param event: TODO
        :param func: TODO"""
        objPath = None
        if not isinstance(what, basestring):
            objPath = what.fullpath
            what = None
        return self.child('subscribe', obj=what, objPath=objPath, event=event, childcontent=func, **kwargs)
        


    def css(self, rule, styleRule=''):
        """Handle the CSS rules
        
        :param rule: dict or list of CSS rules
        :param styleRule: TODO"""
        if ('{' in rule):
            styleRule = rule
            rule = styleRule.split('{')[0]
            rule = rule.strip()
        else:
            if not styleRule.endswith(';'):
                styleRule = styleRule + ';'
            styleRule = '%s {%s}' % (rule, styleRule)
        return self.child('css', childcontent=styleRule)
        
    def styleSheet(self, cssText=None, cssTitle=None, href=None):
        """Create the styleSheet
        
        :param cssText: TODO
        :param cssTitle: TODO
        :param href: TODO"""
        self.child('stylesheet',childname=None, childcontent=cssText, href=href, cssTitle=cssTitle)
        
    def cssrule(self, selector=None, **kwargs):
        """TODO"""
        selector_replaced = selector.replace('.', '_').replace('#', '_').replace(' ', '_')
        self.child('cssrule',childname=selector_replaced, selector=selector, **kwargs)
        
    def macro(self, name='', source='', **kwargs):
        """TODO
        
        :param name: TODO
        :param source: TODO"""
        return self.child('macro', childname=name, childcontent=source, **kwargs)
        
    
    def getMainFormBuilder(self):
        return getattr(self.parentNode,'_mainformbuilder',None)
        
    def formbuilder(self, cols=1, table=None, tblclass='formbuilder',
                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
                    colswidth=None,
                    lblalign=None, lblvalign='top',
                    fldalign=None, fldvalign='top', disabled=False,
                    rowdatapath=None, head_rows=None, **kwargs):
        """In :ref:`formbuilder` you can put dom and widget elements; its most classic usage is to create
        a :ref:`form` made by fields and layers, and that's because formbuilder can manage automatically
        fields and their positioning
        
        :param cols: set the number of columns
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param tblclass: the standard class for the formbuilder. Default value is ``'formbuilder'``,
                         that actually it is the unique defined CSS class
        :param lblclass: set CSS label style
        :param lblpos: set label position: ``L``: set label on the left side of text field
                       ``T``: set label on top of text field
        :param _class: for CSS style
        :param fieldclass: the CSS class appended to every formbuilder's child
        :param lblalign: Set horizontal label alignment (It seems broken... TODO)
        :param lblvalign: set vertical label alignment
        :param fldalign: set field horizontal align
        :param fldvalign: set field vertical align
        :param disabled: If ``True``, user can't act on the object (write, drag...). For more information,
                         check the :ref:`disabled` attribute
        :param rowdatapath: TODO
        :param head_rows: TODO
        :param \*\*kwargs: for the complete list of the ``**kwargs``, check the :ref:`fb_kwargs` section"""
        commonPrefix = ('lbl_', 'fld_', 'row_', 'tdf_', 'tdl_')
        commonKwargs = dict([(k, kwargs.pop(k)) for k in kwargs.keys() if len(k) > 4 and k[0:4] in commonPrefix])
        tbl = self.child('table', _class='%s %s' % (tblclass, _class), **kwargs).child('tbody')
        dbtable = table or kwargs.get('dbtable') or self.getInheritedAttributes().get('table') or self.page.maintable
        formNode = self.parentNode.attributeOwnerNode('formId') if self.parentNode else None
        if formNode:
            if not hasattr(formNode,'_mainformbuilder'):
                formNode._mainformbuilder = tbl
        tbl.fbuilder = GnrFormBuilder(tbl, cols=int(cols), dbtable=dbtable,
                                      lblclass=lblclass, lblpos=lblpos, lblalign=lblalign, fldalign=fldalign,
                                      fieldclass=fieldclass,
                                      lblvalign=lblvalign, fldvalign=fldvalign, rowdatapath=rowdatapath,
                                      head_rows=head_rows, commonKwargs=commonKwargs)
        inattr = self.getInheritedAttributes()
        if hasattr(self.page,'_legacy'):
            tbl.childrenDisabled = disabled
        if colswidth:
            colswidth = colswidth.split(',')
            if len(colswidth)==1:
                colsvalue=colswidth[0]
                if colsvalue == 'auto':
                    x = 100. / cols
                    colsvalue ='%s%%' % x
                colswidth = [colsvalue]

            for w in range(cols):
                k=w if w <len(colswidth) else len(colswidth) -1
                tbl.div(tdf_width=colswidth[k],tdl_height='0px', tdl_border='0',tdf_border='0', tdf_height='0px',min_height='0px', padding_top='0px')

        return tbl
        
    def place(self, fields):
        """TODO
        
        :param fields: TODO"""
        if hasattr(self, 'fbuilder'):
            self.fbuilder.setFields(fields)
            
    def getField(self, fld):
        """TODO
        
        :param fld: TODO"""
        result = {}
        if '.' in fld:
            x = fld.split('.')
            fld = x.pop()
            tblobj = self.page.db.table('.'.join(x), pkg=self.page.packageId)
        else:
            tblobj = self.tblobj
            result['value'] = '^.%s' % fld
            
        fieldobj = tblobj.column(fld)
        if fieldobj is None:
            raise GnrDomSrcError('Not existing field %s' % fld)
        dtype = result['dtype'] = fieldobj.dtype
        result['lbl'] = fieldobj.name_long
        result['size'] = 20
        result.update(dict([(k, v) for k, v in fieldobj.attributes.items() if k.startswith('validate_')]))
        relcol = fieldobj.relatedColumn()
        if relcol != None:
            lnktblobj = relcol.table
            linktable = lnktblobj.fullname
            result['tag'] = 'DbSelect'
            result['dbtable'] = linktable
            result['dbfield'] = lnktblobj.rowcaption
            result['recordpath'] = ':@*'
            result['keyfield'] = relcol.name
            result['_class'] = 'linkerselect'
            if hasattr(lnktblobj, 'zoomUrl'):
                zoomPage = lnktblobj.zoomUrl()
                
            else:
                zoomPage = linktable.replace('.', '/')
            result['lbl_href'] = '^.%s?zoomUrl' % fld
            result['zoomPage'] = zoomPage
        #elif attr.get('mode')=='M':
        #    result['tag']='bagfilteringtable'
        elif dtype == 'A':
            result['size'] = fieldobj.print_width or 10
            result['tag'] = 'input'
            result['_type'] = 'text'
        elif dtype == 'B':
            result['tag'] = 'checkBox'
        elif dtype == 'T':
            result['size'] = fieldobj.print_width or 40
            result['tag'] = 'input'
        elif dtype == 'D':
            result['tag'] = 'dropdowndatepicker'
        else:
            result['tag'] = 'input'
            
        return result
        
class GnrDomSrc_dojo_11(GnrDomSrc):
    """TODO"""
    htmlNS = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
              'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
              'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'frame', 'frameset',
              'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe','htmliframe', 'img', 'input',
              'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
              'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp',
              'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
              'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'audio', 'video', 'var', 'embed','canvas']
              
    dijitNS = ['CheckBox', 'RadioButton', 'ComboBox', 'CurrencyTextBox', 'DateTextBox',
               'InlineEditBox', 'NumberSpinner', 'NumberTextBox', 'HorizontalSlider', 'VerticalSlider', 'Textarea',
               'TextBox', 'TimeTextBox',
               'ValidationTextBox', 'AccordionContainer', 'AccordionPane', 'ContentPane', 'LayoutContainer',
               'BorderContainer',
               'SplitContainer', 'StackContainer', 'TabContainer', 'Button', 'ToggleButton', 'ComboButton',
               'DropDownButton', 'FilteringSelect',
               'Menu', 'Menubar', 'MenuItem', 'Toolbar', 'Dialog', 'ProgressBar', 'TooltipDialog',
               'TitlePane', 'Tooltip', 'ColorPalette', 'Editor', 'Tree', 'SimpleTextarea', 'MultiSelect','ToolbarSeparator']
               
    dojoxNS = ['FloatingPane', 'Dock', 'RadioGroup', 'ResizeHandle', 'SizingPane', 'BorderContainer',
               'FisheyeList', 'Loader', 'Toaster', 'FileInput', 'fileInputBlind', 'FileInputAuto', 'ColorPicker',
               'SortList', 'TimeSpinner', 'Iterator', 'ScrollPane',
               'Gallery', 'Lightbox', 'SlideShow', 'ThumbnailPicker', 'Chart',
               'Deck', 'Slide', 'GoogleMap', 'Calendar', 'GoogleChart', 'GoogleVisualization',
               'DojoGrid', 'VirtualGrid', 'VirtualStaticGrid']
               
    #gnrNS=['menu','menuBar','menuItem','Tree','Select','DbSelect','Combobox','Data',
    #'Css','Script','Func','BagFilteringTable','DbTableFilter','TreeCheck']
    gnrNS = ['DbSelect', 'DbComboBox', 'DbView', 'DbForm', 'DbQuery', 'DbField',
             'dataFormula', 'dataScript', 'dataRpc', 'dataController', 'dataRemote',
             'gridView', 'viewHeader', 'viewRow', 'script', 'func',
             'staticGrid', 'dynamicGrid', 'fileUploader', 'gridEditor', 'ckEditor', 
             'tinyMCE', 'protovis','MultiButton','PaletteGroup','DocumentFrame','bagEditor','PagedHtml','DocItem', 'PalettePane','PaletteMap','VideoPickerPalette','GeoCoderField','StaticMap','ImgUploader','TooltipPane','MenuDiv', 'BagNodeEditor',
             'PaletteBagNodeEditor','StackButtons', 'Palette', 'PaletteTree','CheckBoxText','RadioButtonText','ComboArrow','ComboMenu', 'SearchBox', 'FormStore',
             'FramePane', 'FrameForm','FieldsTree', 'SlotButton','TemplateChunk']
    genroNameSpace = dict([(name.lower(), name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(), name) for name in dijitNS]))
    genroNameSpace.update(dict([(name.lower(), name) for name in dojoxNS]))
    genroNameSpace.update(dict([(name.lower(), name) for name in gnrNS]))
        
    #def framePane(self,slots=None,**kwargs):
    #    self.child('FramePane',slots='top,left,bottom,right',**kwargs)
        
    def dataFormula(self, path, formula, **kwargs):
        """Create a :ref:`dataformula` and returns it. dataFormula allows to calculate
        a value through a formula.
        
        :param path: the dataFormula's path
        :param formula: the dataFormula's formula
        :param \*\*kwargs: formula parameters and other ones (:ref:`css`, etc)
        """
        return self.child('dataFormula', path=path, formula=formula, **kwargs)
        
    def dataScript(self, path, script, **kwargs):
        """.. warning:: deprecated since version 0.7. It has been substituted
                        by :ref:`datacontroller` and :ref:`dataformula`
        """
        return self.child('dataScript', path=path, script=script, **kwargs)
        
    def dataController(self, script=None, **kwargs):
        """Create a :ref:`datacontroller` and returns it. dataController allows to
        execute Javascript code
        
        :param script: the Javascript code that ``datacontroller`` has to execute. 
        :param \*\*kwargs: *_init*, *_onStart*, *_timing*. For more information,
                       check the controllers' :ref:`controllers_attributes` section
        """
        return self.child('dataController', script=script, **kwargs)
        
    def dataRpc(self, path, method, **kwargs):
        """Create a :ref:`datarpc` and returns it. dataRpc allows the client to make a call
        to the server to perform an action and returns it.
        
        :param path: MANDATORY - it contains the folder path of the result of the ``dataRpc`` action;
                     you have to write it even if you don't return any value in the ``dataRpc``
                     (in this situation it will become a "mandatory but dummy" parameter)
        :param method: the name of your ``dataRpc`` method
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section
        """
        return self.child('dataRpc', path=path, method=method, **kwargs)
        
    def selectionstore_addcallback(self, *args, **kwargs):
        """TODO"""
        self.datarpc_addcallback(*args,**kwargs)
        
    def datarpc_addcallback(self, cb, **kwargs):
        """TODO
        
        :param cb: TODO
        :param \*\*kwargs: TODO"""
        self.child('callBack',childcontent=cb,**kwargs)
        return self
        
    def datarpc_adderrback(self, cb, **kwargs):
        """TODO
        
        :param cb: TODO
        """
        self.child('callBack',childcontent=cb,_isErrBack=True,**kwargs)
        return self
        
    def slotButton(self, label=None, **kwargs):
        """Return a :ref:`slotbutton`. A slotbutton is a :ref:`button` with some preset attributes
        to create rapidly a button with an icon (set through the *iconClass* attribute) and with
        a label that works only as a tooltip: for example you can use a slotButton when you handle
        a :ref:`toolbar <toolbars>` or a :ref:`palette <palette>`
        
        :param label: the button's :ref:`tooltip` (or its label, if no *iconClass* is set)
        :param kwargs:
        
                       * **action**: allow to execute a javascript callback. For more information,
                         check the :ref:`action_attr` section
                       * **iconClass**: the button icon. For more information, check the :ref:`iconclass` section
                       * **showLabel**: boolean. If ``True``, show the button label
                       * **value**: specify the path of the widget's value. For more information,
                         check the :ref:`datapath` page
        """
        return self.child(tag='SlotButton',label=label,**kwargs)
        
    def virtualSelectionStore(self, table=None, storeCode=None, storepath=None, columns=None, **kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param storeCode: TODO
        :param storepath: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        """
        self.selectionStore(storeCode=storeCode,table=table, storepath=storepath,columns=columns,**kwargs)
        
    def selectionStore(self,table=None,storeCode=None,storepath=None,columns=None,handler=None,**kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param storeCode: TODO
        :param storepath: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        """
        attr = self.attributes
        parentTag = attr.get('tag')
        #columns = columns or '==gnr.getGridColumns(this);'
        parent = self
        if parentTag:
            parentTag = parentTag.lower()
        #storepath = storepath or attr.get('storepath') or '.grid.store'
        if storeCode:
            storepath = storepath or 'gnr.stores.%s.data' %storeCode            
        
        if parentTag =='includedview' or  parentTag =='newincludedview':
            attr['table'] = table
            storepath = storepath or attr.get('storepath') or '.store'
            
            storeCode = storeCode or attr.get('nodeId') or  attr.get('frameCode') 
            attr['store'] = storeCode
            parent = self.parent
              
        if parentTag == 'palettegrid':            
            storeCode=storeCode or attr.get('paletteCode')
            attr['store'] = storeCode
            attr['table'] = table
            storepath = storepath or attr.get('storepath') or '.store'
        nodeId = '%s_store' %storeCode
        return parent.child('SelectionStore',storepath=storepath, table=table, nodeId=nodeId,columns=columns,handler=handler,**kwargs)
        #ds = parent.dataSelection(storepath, table, nodeId=nodeId,columns=columns,**kwargs)
        #ds.addCallback('this.publish("loaded",{itemcount:result.attr.rowCount}')
    

    def bagStore(self,table=None,storeCode=None,storepath=None,columns=None,**kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param storeCode: TODO
        :param storepath: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        """
        attr = self.attributes
        parentTag = attr.get('tag')
        #columns = columns or '==gnr.getGridColumns(this);'
        parent = self
        if parentTag:
            parentTag = parentTag.lower()
        #storepath = storepath or attr.get('storepath') or '.grid.store'

        if parentTag =='includedview' or  parentTag =='newincludedview':
            attr['table'] = table
            storepath = storepath or attr.get('storepath') or '.store'
            storeCode = storeCode or attr.get('nodeId') or  attr.get('frameCode') 
            attr['store'] = storeCode
            attr['tag'] = 'newincludedview'
            parent = self.parent
        if parentTag == 'palettegrid':            
            storeCode=storeCode or attr.get('paletteCode')
            attr['store'] = storeCode
            attr['table'] = table
            storepath = storepath or attr.get('storepath') or '.store'
        nodeId = '%s_store' %storeCode
        #self.data(storepath,Bag())
        return parent.child('BagStore',storepath=storepath, nodeId=nodeId,**kwargs)

    def onDbChanges(self, action=None, table=None, **kwargs):
        """TODO
        
        :param action: the :ref:`action_attr` attribute
        :param table: the :ref:`database table <table>`"""
        self.page.subscribeTable(table,True)
        self.dataController(action,dbChanges="^gnr.dbchanges.%s" %table.replace('.','_'),**kwargs)
    
    def dataSelection(self, path, table=None, method='app.getSelection', columns=None, distinct=None,
                      where=None, order_by=None, group_by=None, having=None, columnsFromView=None, **kwargs):
        """Create a :ref:`dataselection` and returns it. dataSelection allows... TODO
        
        :param path: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param method: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section.
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param group_by: the sql "GROUP BY" clause. For more information check the
                         :ref:`sql_group_by` section
        :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
        :param columnsFromView: TODO
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section
        """
        if 'name' in kwargs:
            kwargs['_name'] = kwargs.pop('name')
        if 'content' in kwargs:
            kwargs['_content'] = kwargs.pop('content')
        if not columns:
            if columnsFromView:
                print 'columnsFromView is deprecated'
                columns = '=grids.%s.columns' % columnsFromView #it is the view id
            else:
                columns = '*'
                
        return self.child('dataRpc', path=path, table=table, method=method, columns=columns,
                          distinct=distinct, where=where, order_by=order_by, group_by=group_by,
                          having=having, **kwargs)
                          
    def directoryStore(self, rootpath=None, storepath='.store', **kwargs):
        """TODO
        
        :param rootpath: TODO
        :param storepath: TODO
        """
        store = DirectoryResolver(rootpath or '/', **kwargs)()
        self.data(storepath, store)
        
    def tableAnalyzeStore(self, table=None, where=None, group_by=None, storepath='.store.root',caption='Store',**kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where`
                      section
        :param group_by: the sql "GROUP BY" clause. For more information check the
                         :ref:`sql_group_by` section
        :param storepath: TODO
        """
        self.data('.store',Bag(),caption=caption)
        self.dataRpc(storepath,'app.tableAnalyzeStore',table=table,where=where,group_by=group_by,**kwargs)

        
    def dataRecord(self, path, table, pkey=None, method='app.getRecord', **kwargs):
        """Create a :ref:`datarecord` and returns it. dataRecord allows... TODO
        
        :param path: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`
        :param method: TODO
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section
        """
        return self.child('dataRpc', path=path, table=table, pkey=pkey, method=method, **kwargs)
        
    def dataRemote(self, path, method, **kwargs):
        """Create a :ref:`dataremote` and returns it. dataRemote is a synchronous :ref:`datarpc`:
        it calls a (specified) dataRspc as its resolver. When ``dataRemote`` is brought to the
        client, it will be changed in a Javascript resolver that at the desired path perform
        the rpc (indicated with the ``remote`` attribute).
        
        :param path: the path where the dataRemote will save the result of the rpc
        :param method: the rpc name that has to be executed
        :param \*\*kwargs: *cacheTime=NUMBER*: The cache stores the retrieved value and keeps
                           it for a number of seconds equal to ``NUMBER``
        """
        return self.child('dataRemote', path=path, method=method, **kwargs)
        
    def dataResource(self, path, resource=None, ext=None, pkg=None):
        """Create a :ref:`dataresource` and returns it. dataResource is a :ref:`dataRemote`
        that allows... TODO
        
        :param path: TODO
        :param resource: TODO
        :param ext: TODO
        :param pkg: the :ref:`package <packages>` object
        """
        self.dataRemote(path,'getResourceContent',resource=resource,ext=ext, pkg=pkg)
        
    def paletteGroup(self, groupCode, **kwargs):
        """Return a :ref:`palettegroup`
        
        :param groupCode: TODO
        """
        return self.child('PaletteGroup',groupCode=groupCode,**kwargs)


    def docItem(self, store=None,key=None,contentpath=None,**kwargs):        
        return self.child('DocItem',store=store,key=key,contentpath=contentpath,**kwargs)

    def ckeditor(self,stylegroup=None,**kwargs):
        style_table = self.page.db.table('adm.ckstyle')
        if style_table:
            cs = dict()
            cs.update(style_table.query(where="$stylegroup IS NULL OR $stylegroup=''",g=stylegroup,columns='$name,$element,$styles,$attributes').fetchAsDict('name'))
            if stylegroup:
                for st in stylegroup.split(','):
                    cs.update(style_table.query(where='$stylegroup=:g',g=stylegroup,columns='$name,$element,$styles,$attributes').fetchAsDict('name'))
            if cs:
                kwargs['customStyles'] = [dict(v) for v in cs.values()]

        return self.child('ckEditor',**kwargs)

    def palettePane(self, paletteCode, datapath=None, **kwargs):
        """Return a :ref:`palettepane`
        
        :param paletteCode: TODO. If no *datapath* is specified, the *paletteCode* will be used as *datapath*
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        """
        datapath= 'gnr.palettes.%s' %paletteCode if datapath is None else datapath
        return self.child('PalettePane',paletteCode=paletteCode,datapath=datapath,**kwargs)
        
    def paletteTree(self, paletteCode, datapath=None, **kwargs):
        """Return a :ref:`palettetree`
        
        :param paletteCode: TODO. If no *datapath* is specified, the *paletteCode* will be used as *datapath*
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        """
        datapath= datapath or 'gnr.palettes.%s' %paletteCode if datapath is None else datapath
        palette = self.child('PaletteTree',paletteCode=paletteCode,datapath=datapath,
                             autoslots='top,left,right,bottom',**kwargs)
        return palette
        
    def paletteGrid(self, paletteCode=None, struct=None, columns=None, structpath=None, datapath=None, **kwargs):
        """Return a :ref:`palettegrid`
        
        :param paletteCode: create the paletteGrid :ref:`nodeid` (if no *gridId* is defined)
                            and create the paletteGrid :ref:`datapath` (if no *datapath* is defined)
        :param struct: the name of the method that defines the :ref:`struct`
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param structpath: TODO
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param kwargs: in the kwargs you find:
                       
                       * *dockButton*: boolean. if ``True``, TODO
                       * *grid_filteringGrid*: the path of the :ref:`grid` that handle the :ref:`struct`.
                         For example, in the :ref:`th` component the standard path for a grid is ``th.view.grid``
                       * *grid_filteringColumn*: allow the sincronization between the choosen columns and the
                         not choosen ones (so, if user drag a column in a grid, then this column doesn't appear
                         anymore in the palette)
                         
                         The syntax is::
                         
                            grid_filteringColumn='id:COLUMN'
                            
                         Where ``COLUMN`` is the name of a :ref:`column` TODO
                            
                       * *title*: the title of the paletteGrid
        """
        datapath= datapath or 'gnr.palettes.%s' %paletteCode if datapath is None else datapath
        structpath = structpath or '.grid.struct'
        kwargs['gridId'] = kwargs.get('gridId') or '%s_grid' %paletteCode
        paletteGrid = self.child('paletteGrid',paletteCode=paletteCode,
                                structpath=structpath,datapath=datapath,
                                autoslots='top,left,right,bottom',**kwargs)
        if struct or columns or not structpath:
            paletteGrid.gridStruct(struct=struct,columns=columns)
        return paletteGrid


        
    def includedview_draganddrop(self,dropCodes=None,**kwargs):
        ivattr = self.attributes
        if dropCodes:
            for dropCode in dropCodes.split(','):
                mode = 'grid'
                if ':' in dropCode:
                    dropCode, mode = dropCode.split(':')
                dropmode = 'dropTarget_%s' % mode
                ivattr[dropmode] = '%s,%s' % (ivattr[dropmode], dropCode) if dropmode in ivattr else dropCode
                ivattr['onDrop_%s' % dropCode] = 'SET .droppedInfo_%s = dropInfo; FIRE .dropped_%s = data;' % (dropCode,dropCode)
                #ivattr['onCreated'] = """dojo.connect(widget,'_onFocus',function(){genro.publish("show_palette_%s")})""" % dropCode
                
    def newincludedview_draganddrop(self,dropCodes=None,**kwargs):
        self.includedview_draganddrop(dropCodes=dropCodes,**kwargs)
        
    def includedview(self, *args, **kwargs):
        """The :ref:`includedview` component"""
        frameCode = kwargs.get('parentFrame') or self.attributes.get('frameCode')
        if frameCode and not kwargs.get('parentFrame')==False:
            kwargs['frameCode'] = frameCode
            return self.includedview_inframe(*args,**kwargs)
        else:
            return self.includedview_legacy(*args,**kwargs)
            
    def includedview_inframe(self, frameCode=None, struct=None, columns=None, storepath=None, structpath=None,
                             datapath=None, nodeId=None, configurable=True, _newGrid=False, childname=None, **kwargs):
        """TODO
        
        :param frameCode: TODO
        :param struct: the :ref:`struct` object
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param storepath: TODO
        :param structpath: the :ref:`struct` path
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page
        :param configurable: boolean. TODO
        :param _newGrid: boolean. TODO
        :param childname: the :ref:`childname`
        """
        nodeId = nodeId or '%s_grid' %frameCode
        if datapath is False:
            datapath = None
        elif storepath:
            datapath = datapath or '#FORM.%s' %nodeId 
        else:
            datapath = '.grid'
        structpath = structpath or '.struct'
        self.attributes['target'] = nodeId
        wdg = 'NewIncludedView' if _newGrid else 'includedView'
        relativeWorkspace = kwargs.pop('relativeWorkspace',True)
        childname=childname or 'grid'
        frameattributes = self.attributes
        if not self.attributes.get('frameCode'):
            frameattributes = self.root.getNodeByAttr('frameCode',frameCode).attr
        frameattributes['target'] = nodeId
        iv =self.child(wdg,frameCode=frameCode, datapath=datapath,structpath=structpath, nodeId=nodeId,
                     childname=childname,
                     relativeWorkspace=relativeWorkspace,configurable=configurable,storepath=storepath,**kwargs)
        if struct or columns or not structpath:
            iv.gridStruct(struct=struct,columns=columns)
        return iv
        
    def includedview_legacy(self, storepath=None, structpath=None, struct=None, columns=None, table=None,
                            nodeId=None, relativeWorkspace=None, **kwargs):
        """TODO
        
        :param storepath: TODO
        :param structpath: the :ref:`struct` path
        :param struct: the :ref:`struct` object
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param nodeId: the :ref:`nodeid`
        :param relativeWorkspace: TODO
        """
        nodeId = nodeId or self.page.getUuid()
        prefix = 'grids.%s' %nodeId if not relativeWorkspace else ''
        structpath = structpath or '%s.struct' % prefix
        iv =self.child('includedView', storepath=storepath, structpath=structpath, nodeId=nodeId, table=table,
                          relativeWorkspace=relativeWorkspace,**kwargs)
        source = struct or columns
        if struct or columns or not structpath:
            iv.gridStruct(struct=struct,columns=columns)
        return iv
            
    def gridStruct(self, struct=None, columns=None):
        """TODO
        
        :param struct: the :ref:`struct` object
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        """
        gridattr=self.attributes
        structpath = gridattr.get('structpath')
        table = gridattr.get('table')
        gridId= gridattr.get('nodeId') 
        storepath = gridattr.get('storepath')
        source = struct or columns
        page = self.page
        struct = page._prepareGridStruct(source=source,table=table,gridId=gridId)
        if struct:
            self.data(structpath, struct)
            return struct
        elif (source and not table) or not storepath:
            def getStruct(source=None,gridattr=None,gridId=None):
                storeCode = gridattr.get('store') or gridattr.get('nodeId') or gridattr.get('gridId')
                storeNode = page.pageSource('%s_store' %storeCode)
                table = gridattr.get('table')
                if storeNode:
                    table = storeNode.attr.get('table')
                    gridattr['table'] = table
                    #gridattr['storepath'] = '#%s_store.%s' %(storeCode,storeNode.attr.get('storepath'))
                return page._prepareGridStruct(source=source,table=table,gridId=gridId)
            struct = BagCbResolver(getStruct, source=source,gridattr=gridattr,gridId=gridId)
            struct._xmlEager=True
            self.data(structpath, struct)
        
    def slotToolbar(self,*args,**kwargs):
        """Create a :ref:`slotToolbar <slotbar>` and returns it
        
        .. note:: a slotToolbar is a :ref:`slotBar <slotbar>` with some css preset
        """
        kwargs['toolbar'] = True
        return self.slotBar(*args,**kwargs)
        
    def slotFooter(self,*args,**kwargs):
        """TODO"""
        kwargs['_class'] = 'frame_footer'
        return self.slotBar(*args,**kwargs)
        
    def _addSlot(self,slot,prefix=None,frame=None,frameCode=None,namespace=None,toolbarArgs=None):
        s=self.child('slot',childname=slot)
        s.frame = frame
        parameter = None
        slotCode = slot
        if '@' in slot:
            slotCode = slot.replace('@','_')
            slot,parameter = slot.split('@')
        slothandle = getattr(s,'%s_%s' %(prefix,slot),None)
        if not slothandle:
            if namespace:
                slothandle = getattr(s,'slotbar_%s_%s' %(namespace,slot),None)
            if not slothandle:
                slothandle = getattr(s,'slotbar_%s' %slot,None)
        if slothandle:
            kw = dict()
            kw[slot] = toolbarArgs.pop(slot,parameter)
            kw.update(dictExtract(toolbarArgs,'%s_' %slotCode,True))
            kw['frameCode'] = frameCode
            slothandle(**kw)
            
    def slotBar(self, slots=None, slotbarCode=None, namespace=None, childname='bar', **kwargs):
        """Create a :ref:`slotBar <slotbar>` and returns it. A slotBar is a Genro
        :ref:`toolbar <toolbars>`
        
        :param slots: MANDATORY. Create a configurable UI inside the div or :ref:`contentpane`
                      in which the slotToolbar is defined. For more information, check the
                      :ref:`slotbar_slots` section
        :param slotbarCode: autocreate a :ref:`nodeid` for the slotToolbar AND autocreate
                            hierarchic nodeIds for every slotToolbar child
        :param namespace: TODO
        :param childname: the slotBar :ref:`childname`
        """
        namespace = namespace or self.parent.attributes.get('namespace')
        tb = self.child('slotBar',slotbarCode=slotbarCode,slots=slots,childname=childname,**kwargs)
        toolbarArgs = tb.attributes
        slots = gnrstring.splitAndStrip(str(slots))
        frame = self.parent
        frameCode = self.getInheritedAttributes().get('frameCode')
        prefix = slotbarCode or frameCode
        for slot in slots:
            if slot!='*' and slot!='|' and not slot.isdigit():
                tb._addSlot(slot,prefix=prefix,frame=frame,frameCode=frameCode,namespace=namespace,toolbarArgs=toolbarArgs)
        return tb
        
        #se ritorni la toolbar hai una toolbar vuota 
    
    def slotbar_updateslotsattr(self,**kwargs):
        self.attributes.update(kwargs)
        toolbarArgs = self.attributes
        slotstr = toolbarArgs['slots']
        slots = slotstr.split(',')
        slotbarCode= toolbarArgs.get('slotbarCode')
        inattr = self.getInheritedAttributes()
        frameCode = inattr.get('frameCode')
        namespace = inattr.get('namespace')
        frame = self.parent.parent
        prefix = slotbarCode or frameCode
        for slot in slots:
            if slot!='*' and slot!='|' and not slot.isdigit():
                self.pop(slot)
                self._addSlot(slot,prefix=prefix,frame=frame,frameCode=frameCode,namespace=namespace,toolbarArgs=toolbarArgs)

    def slotbar_replaceslots(self, toReplace, replaceStr,**kwargs):
        """Allow to redefine the preset bars of the :ref:`slotBars <slotbar>` and the
        :ref:`slotToolbars <slotbar>`
        
        :param toReplace: MANDATORY. A string with the list of the slots to be replaced.
                          Use ``#`` to replace all the slots
        :param replaceStr: MANDATORY. A string with the list of the slots to add
        """
        self.attributes.update(kwargs)
        toolbarArgs = self.attributes
        slotstr = toolbarArgs['slots']
        slotbarCode= toolbarArgs.get('slotbarCode')
        if toReplace=='#':
            toReplace = slotstr
        replaceStr = replaceStr.replace('#',slotstr)
        slotstr = slotstr.replace(toReplace,replaceStr)
        toolbarArgs['slots'] = slotstr
        slots = slotstr.split(',')
        inattr = self.getInheritedAttributes()
        frameCode = inattr.get('frameCode')
        namespace = inattr.get('namespace')
        frame = self.parent.parent
        prefix = slotbarCode or frameCode
        for slot in slots:
            if slot!='*' and slot!='|' and not slot.isdigit():
                if not self.getNode(slot):
                    self._addSlot(slot,prefix=prefix,frame=frame,frameCode=frameCode,namespace=namespace,toolbarArgs=toolbarArgs)
        return self
                    
    def button(self, label=None, **kwargs):
        """The :ref:`button` is a :ref:`dojo-improved form widget <dojo_improved_widgets>`: through
        the *action* attribute you can add Javascript callbacks
        
        :param label: the label of the widget
        :param kwargs:
        
                       * **action**: allow to execute a javascript callback. For more information,
                         check the :ref:`action_attr` section
                       * **iconClass**: the button icon. For more information, check the :ref:`iconclass` section
                       * **showLabel**: boolean. If ``True``, show the button label
        """
        return self.child('button', label=label, **kwargs)
        
    def togglebutton(self, label=None, **kwargs):
        """A toggle button is a button that represents a setting with two states:
        ``True`` and ``False``. Use the *iconclass* attribute to allow the user
        to know (see) the current status
        
        :param label: the button's label
        :param kwargs: 
        
                       * **iconClass**: the button icon. For more information, check the :ref:`iconclass` section
                       * **showLabel**: boolean. If ``True``, show the button label
        """
        return self.child('togglebutton', label=label, **kwargs)
        
    def radiobutton(self, label=None, **kwargs):
        """:ref:`Radiobuttons <radiobutton>` are used when you want to let the user select
        one - and just one - option from a set of choices (if more options are to be allowed
        at the same time you should use :ref:`checkboxes <checkbox>` instead)
        
        :param label: the radiobutton label
        :param kwargs: 
                       
                       * *group*: allow to create a radiobutton group. To create a group, give
                         the same string to the *group* attribute of many radiobuttons. You can
                         obviously create more than a group giving a different string to the *group*
                         attribute (for more information, check the :ref:`rb_examples_group`)
        """
        return self.child('radiobutton', label=label, **kwargs)
        
    def checkbox(self, label=None, value=None, **kwargs):
        """Return a :ref:`checkbox`: setting the value to true will check the box
        while false will uncheck it
        
        :param label: the checkbox label
        :param value: the checkbox path for value. For more information, check the
                      :ref:`datapath` section
        """
        return self.child('checkbox', value=value, label=label, **kwargs)
        
    def dropdownbutton(self, label=None, **kwargs):
        """The :ref:`dropdownbutton` can be used to build a :ref:`menu`
        
        :param label: the button label
        :param kwargs: 
                       
                       * **iconClass**: the button icon. For more information, check the :ref:`iconclass` section
                       * **showLabel**: boolean. If ``True``, show the button label
        """
        return self.child('dropdownbutton', label=label, **kwargs)
        
    def menuline(self, label=None, **kwargs):
        """A line of a :ref:`menu`
        
        :param label: the menuline label. Set it to "``-``" to create a dividing line
                      in the menu: ``menuline('-')``
        :param kwargs:
                       
                       * *action*: allow to execute a javascript callback. For more information, check
                         the :ref:`action_attr` page
                       * *checked*: boolean (by default is ``False``). If ``True``, allow to set a "V"
                         mark on the left side of the *menuline*
        """
        return self.child('menuline', label=label, **kwargs)
        
    def pluggedFields(self):
        tblobj = self.parentfb.tblobj
        collist = tblobj.model['columns']
        pluggedCols = [(col,collist[col].attributes.get('_pluggedBy')) for col in collist if collist[col].attributes.get('plugToForm')]
        for f,pluggedBy in pluggedCols:
            kwargs = dict()
            if pluggedBy:
                handler = getattr(self.page.db.table(pluggedBy),'onPlugToForm',None)
                if handler:
                    kwargs = handler(f)
            if kwargs is False:
                continue
            self.field(f,**kwargs)



    def field(self, field=None, **kwargs):
        """``field`` is used to view, select and modify data included in a database :ref:`table`.

        Its type is inherited from :ref:`the type of data <datatype>` contained in the table to which
        ``field`` refers. For example, if the ``field`` is related to a column with the dtype set
        to "L" (integer number), then the relative widget is a :ref:`numbertextbox`, if the related
        column has a dtype set to "D", then the relative widget is a :ref:`datetextbox`, and so on

        .. note:: ``field`` MUST be a child of the :ref:`formbuilder` form widget, and
                  ``formbuilder`` itself MUST have a :ref:`datapath` for inner relative path gears
        
        :param field: MANDATORY - the column name to which field refers to. For more information,
                      check the :ref:`field_attr_field` section
        :param kwargs:
        
                       * **lbl**: Set the label of the field. If you don't specify it, then
                         ``field`` will inherit it from the :ref:`name_long` attribute of the requested data
                       * **rowcaption**: the textual representation of a record in a user query.
                         For more information, check the :ref:`rowcaption` section
        """
        newkwargs = self._fieldDecode(field, **kwargs)
        kwargs.pop('lbl',None) #inside _fielddecode routine
        newkwargs.update(kwargs)
        tag = newkwargs.pop('tag')
        handler = getattr(self,tag)
        return handler(**newkwargs)
        
    def placeFields(self, fieldlist=None, **kwargs):
        """TODO"""
        for field in fieldlist.split(','):
            kwargs = self._fieldDecode(field)
            tag = kwargs.pop('tag')
            self.child(tag, **kwargs)
        return self
        
    def radiogroup(self, labels, group, cols=1, datapath=None, **kwargs):
        """.. warning:: deprecated since version 0.7"""
        if isinstance(labels, basestring):
            labels = labels.split(',')
        pane = self.div(datapath=datapath, **kwargs).formbuilder(cols=cols)
        for label in labels:
            if(datapath):
                pane.radioButton(label, group=group, datapath=':%s' % label)
            else:
                pane.radioButton(label, group=group)

    def _fieldDecode(self, fld, **kwargs):
        parentfb = self.parentfb
        tblobj = None
        if '.' in fld and not fld.startswith('@'):
            x = fld.split('.', 2)
            maintable = '%s.%s' % (x[0], x[1])
            tblobj = self.page.db.table(maintable)
            fld = x[2]
        elif parentfb:
            assert hasattr(parentfb,'tblobj'),'missing default table. HINT: are you using a formStore in a bad place?'
            tblobj = parentfb.tblobj
        else:
            raise GnrDomSrcError('No table')
                
        fieldobj = tblobj.column(fld)
        if fieldobj is None:
            raise GnrDomSrcError('Not existing field %s' % fld)
        wdgattr = self.wdgAttributesFromColumn(fieldobj, fld=fld,**kwargs)     
        if fieldobj.getTag() == 'virtual_column' or (('@' in fld ) and fld != tblobj.fullRelationPath(fld)):
            wdgattr.setdefault('readOnly', True)
            wdgattr['_virtual_column'] = fld
           
        if wdgattr['tag']in ('div', 'span'):
            wdgattr['innerHTML'] = '^.%s' % fld
        elif wdgattr['tag'] == 'tree':
            wdgattr['storepath'] = '.%s' % fld
            wdgattr['_fired'] ='^.%s' % fld
        else:
            wdgattr['value'] = '^.%s' % fld
        return wdgattr
        
    def wdgAttributesFromColumn(self, fieldobj,fld=None, **kwargs):
        """TODO
        
        :param fieldobj: TODO
        """
        lbl = kwargs.pop('lbl',None) 
        lbl =  fieldobj.name_long if lbl is None else lbl
        result = {'lbl': lbl,'field_name_long':fieldobj.name_long, 'dbfield': fieldobj.fullname}
        dtype = result['dtype'] = fieldobj.dtype
        fldattr =  dict(fieldobj.attributes or dict())

        if dtype in ('A', 'C'):
            size = fldattr.get('size', '20')
            if ':' in size:
                size = size.split(':')[1]
            size = int(size)
        else:
            size = 5
        result.update(dictExtract(fldattr,'validate_',slice_prefix=False))
        result.update(dictExtract(fldattr,'wdg_'))
        if 'unmodifiable' in fldattr:
            result['unmodifiable'] = fldattr['unmodifiable']
        if 'protected' in fldattr:
            result['protected'] = fldattr['protected']
        relcol = fieldobj.relatedColumn()
        if not relcol is None:
            lnktblobj = relcol.table
            isLookup = lnktblobj.attributes.get('lookup') or False
            joiner = fieldobj.relatedColumnJoiner()
            onerelfld = joiner['one_relation'].split('.')[2]
            if dtype in ('A', 'C'):
                size = lnktblobj.attributes.get('size', '20')
                if ':' in size:
                    size = size.split(':')[1]
                size = int(size)
            else:
                size = 5
            defaultZoom = self.page.pageOptions.get('enableZoom', True)
            result['lbl'] = lbl or fieldobj.table.dbtable.relationName('@%s' % fieldobj.name)
            if kwargs.get('zoom', defaultZoom):
                if hasattr(self.page,'_legacy'):
                    if hasattr(lnktblobj.dbtable, 'zoomUrl'):
                        zoomPage = lnktblobj.dbtable.zoomUrl()
                    else:
                        zoomPage = lnktblobj.fullname.replace('.', '/')
                    result['lbl_href'] = "=='/%s?pkey='+pkey" % zoomPage
                    result['lbl_pkey'] = '^.%s' %fld
                else:
                    if hasattr(lnktblobj.dbtable, 'zoomUrl'):
                        pass
                    else:
                        zoomKw = dictExtract(kwargs,'zoom_')
                        forcedTitle = zoomKw.pop('title', None)
                        zoomKw.setdefault('formOnly',False)
                        result['lbl__zoomKw'] = zoomKw #,slice_prefix=False)
                        result['lbl__zoomKw_table'] = lnktblobj.fullname
                        result['lbl__zoomKw_lookup'] = isLookup
                        result['lbl__zoomKw_title'] = forcedTitle or lnktblobj.name_plural or lnktblobj.name_long
                        result['lbl__zoomKw_pkey'] = '=.%s' %fld
                        result['lbl_connect_onclick'] = "genro.dlg.zoomPaletteFromSourceNode(this,$1);"  
                result['lbl'] = '<span class="gnrzoomicon">&nbsp;&nbsp;&nbsp;&nbsp;</span><span>%s</span>' %self.page._(result['lbl'])
                result['lbl_class'] = 'gnrzoomlabel'
            result['tag'] = 'DbSelect'
            result['dbtable'] = lnktblobj.fullname
            if '_storename' in joiner:
                result['_storename'] = joiner['_storename']
            elif 'storefield' in joiner:
                result['_storename'] = False if joiner['storefield'] is False else '=.%(storefield)s' %joiner
            #result['columns']=lnktblobj.rowcaption
            result['_class'] = 'linkerselect'
            result['searchDelay'] = 300
            result['ignoreCase'] = True
            result['method'] = 'app.dbSelect'
            result['size'] = size
            result['_guess_width'] = '%iem' % (int(size * .7) + 2)
            result.setdefault('hasDownArrow',isLookup)
            if(onerelfld != relcol.table.pkey):
                result['alternatePkey'] = onerelfld
        #elif attr.get('mode')=='M':
        #    result['tag']='bagfilteringtable'
        elif dtype in ('A', 'T') and fldattr.get('values', False):
            values = fldattr['values']
            result['tag'] = 'filteringselect' if ':' in values else 'combobox'
            result['values'] = values
        elif dtype == 'A':
            result['maxLength'] = size
            result['tag'] = 'textBox'
            result['_type'] = 'text'
            result['_guess_width'] = '%iem' % (int(size * .7) + 2)
        elif dtype == 'B':
            result['tag'] = 'checkBox'
            if 'autospan' in kwargs:
                kwargs['colspan'] = kwargs['autospan']
                del kwargs['autospan']
        elif dtype == 'T':
            result['tag'] = 'textBox'
            result['_guess_width'] = '%iem' % int(size * .5)
        elif dtype == 'R':
            result['tag'] = 'numberTextBox'
            result['width'] = '7em'
        elif dtype == 'N':
            result['tag'] = 'numberTextBox'
            result['_guess_width'] = '7em'
        elif dtype == 'L' or dtype == 'I':
            result['tag'] = 'numberTextBox'
            result['_guess_width'] = '7em'
        elif dtype == 'D':
            result['tag'] = 'dateTextBox'
            result['_guess_width'] = '9em'
        elif dtype == 'H':
            result['tag'] = 'timeTextBox'
            result['_guess_width'] = '7em'
        elif dtype =='X':
            result['tag'] = 'tree'         
        else:
            result['tag'] = 'textBox'
        if kwargs:
            if kwargs.get('autospan', False):
                kwargs['colspan'] = kwargs.pop('autospan')
                kwargs['width'] = '99%'
            result.update(kwargs)
        return result
        
class GnrFormBuilder(object):
    """The class that handles the creation of the :ref:`formbuilder` widget"""
    def __init__(self, tbl, cols=None, dbtable=None, fieldclass=None,
                 lblclass='gnrfieldlabel', lblpos='L', lblalign=None, fldalign=None,
                 lblvalign='top', fldvalign='top', rowdatapath=None, head_rows=None, commonKwargs=None):
        self.commonKwargs = commonKwargs or {}
        self.lblalign = lblalign or {'L': 'right', 'T': 'left'}[lblpos] # jbe?  why is this right and not left?
        self.fldalign = fldalign or {'L': 'left', 'T': 'center'}[lblpos]
        self.lblvalign = lblvalign
        self.fldvalign = fldvalign
        self.lblclass = lblclass
        self.fieldclass = fieldclass
        self.colmax = cols
        self.lblpos = lblpos
        self.rowlast = -1
        #self._tbl=weakref.ref(tbl)
        self._tbl = tbl
        self.maintable = dbtable
        if self.maintable:
            self.tblobj = self.page.db.table(self.maintable)
        self.rowcurr = -1
        self.colcurr = 0
        self.row = -1
        self.col = -1
        self.rowdatapath = rowdatapath
        self.head_rows = head_rows or 0
        
    def br(self):
        #self.row=self.row+1
        self.col = 999
        return self.tbl
        
    def _get_page(self):
        return self.tbl.page
        
    page = property(_get_page)
            
    def _get_tbl(self):
        #return self._tbl()
        return self._tbl
        
    tbl = property(_get_tbl)
        
    def place(self, **fieldpars):
        """TODO"""
        return self.setField(fieldpars)
        
    def setField(self, field, row=None, col=None):
        """TODO
        
        :param field: TODO
        :param row: TODO
        :param col: TODO
        """
        field = dict(field)
        if 'pos' in field:
            rc = ('%s,0' % field.pop('pos')).split(',')
            if rc[0] == '*':
                rc[0] = str(self.row)
            elif rc[0] == '+':
                rc[0] = str(self.row + 1)
            row, col = int(rc[0]), int(rc[1])
                
        if row is None:
            row = self.row
            col = self.col
        if col < 0:
            col = self.colmax + col
        self.row, self.col = self.nextCell(row, col)
        if 'fld' in field:
            fld_dict = self.tbl.getField(field.pop('fld'))
            fld_dict.update(field)
            field = fld_dict
        return self._formCell(self.row, self.col, field)
        
    def setFields(self, fields, rowstart=0, colstart=0):
        """TODO
        
        :param fields: TODO
        :param rowstart: TODO
        :param colstart: TODO
        """
        for field in fields:
            self.setField(field)
                
    def _fillRows(self, r):
        if r > self.rowlast:
            for j in range(self.rowlast, r):
                self._formRow(j + 1)
                
    def setRowAttr(self, r, attrs):
        """TODO
        
        :param r: the row to set
        :param attrs: TODO
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl.setAttr('r_%i' % r, attrs)
        else:
            return (self.tbl.setAttr('r_%i_l' % r, attrs), self.tbl.setAttr('r_%i_f' % r, attrs))
                
    def getRowNode(self, r):
        """TODO
        
        :param r: the row from which to get node
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl.getNode('r_%i' % r)
        else:
            return (self.tbl.getNode('r_%i_l' % r), self.tbl.getNode('r_%i_f' % r))
                
    def getRow(self, r):
        """TODO
        
        :param r: the row to get
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl['r_%i' % r]
        else:
            return (self.tbl['r_%i_l' % r], self.tbl['r_%i_f' % r])
                
    def nextCell(self, r, c):
        """Get the current row (*r* attribute) and the current cell (*c* attribute)
        of the :ref:`struct` and return the correct next row and cell
        
        :param r: a row
        :param c: a cell
        """
        def nc(row, r, c):
            c = c + 1
            if c >= self.colmax:
                c = 0
                r = r + 1
                row = self.getRow(r)
            return row, r, c
                
        row = self.getRow(r)
        row, r, c = nc(row, r, c)
        if self.lblpos == 'L':
            while not 'c_%i_l' % c in row.keys():
                row, r, c = nc(row, r, c)
        else:
            while not 'c_%i' % c in row[0].keys():
                row, r, c = nc(row, r, c)
        return r, c
                
    def setRow(self, fields, row=None):
        """TODO
        
        :param fields: TODO
        :param row: TODO
        """
        colcurr = -1
        if row is None:
            row = self.rowcurr = self.rowcurr + 1
        if row > self.rowlast:
            for r in range(self.rowlast, row):
                self._formRow(r + 1)
        self._formRow(row)
                
        for f in fields:
            if not 'col' in f:
                col = colcurr = colcurr + 1
            else:
                col = int(f.pop('col'))
            if col <= self.colmax:
                self.setField(f, row, col)
                
    def _formRow(self, r):
        if self.rowdatapath and r >= self.head_rows:
            rdp = '.r_%i' % (r - self.head_rows, )
        else:
            rdp = None
        if self.lblpos == 'L':
            self.tbl.tr(childname='r_%i' % r, datapath=rdp)
                
        elif self.lblpos == 'T':
            self.tbl.tr(childname='r_%i_l' % r, datapath=rdp)
            self.tbl.tr(childname='r_%i_f' % r, datapath=rdp)
        self.rowlast = max(self.rowlast, r)
                
        for c in range(self.colmax):
            self._formCell(r, c)
                
    def _formCell(self, r, c, field=None):
        row = self.getRow(r)
        row_attributes = dict()
        td_field_attr = dict()
        td_lbl_attr = dict()
        lbl = ''
        lblvalue = None
        tag = None
        rowspan, colspan = 1, 1
        lblalign, fldalign = self.lblalign, self.fldalign
        lblvalign, fldvalign = self.lblvalign, self.fldvalign
        lbl_kwargs = {}
        lblhref = None
        if field is not None:
            f = dict(self.commonKwargs)
            f.update(field)
            field = f
            lbl = field.pop('lbl', '')
            if not '_valuelabel' in field and not lbl.startswith('=='):  #BECAUSE IT CANNOT CALCULATE ON THE FIELD SOURCENODE SCOPE
                field['_valuelabel'] = lbl
            if 'lbl_href' in field:
                lblhref = field.pop('lbl_href')
                lblvalue = lbl
                lbl = None
            for k in field.keys():
                attr_name = k[4:]
                if attr_name == 'class':
                    attr_name = '_class'
                if k.startswith('row_'):
                    row_attributes[attr_name] = field.pop(k)
                elif k.startswith('lbl_'):
                    lbl_kwargs[attr_name] = field.pop(k)
                elif k.startswith('fld_'):
                    v = field.pop(k)
                    if not attr_name in field:
                        field[attr_name] = v
                elif k.startswith('tdf_'):
                    td_field_attr[attr_name] = field.pop(k)
                elif k.startswith('tdl_'):
                    td_lbl_attr[attr_name] = field.pop(k)
                    
            if field.pop('html_label',None) and field.get('dtype') =='B':
                field['label'] = lbl
                lbl = None
            lblalign, fldalign = field.pop('lblalign', lblalign), field.pop('fldalign', fldalign)
            lblvalign, fldvalign = field.pop('lblvalign', lblvalign), field.pop('fldvalign', fldvalign)
            tag = field.pop('tag', None)
            rowspan = int(field.pop('rowspan', '1'))
            cspan = int(field.pop('colspan', '1'))
            if cspan > 1:
                for cs in range(c + 1, c + cspan):
                    if ((self.lblpos == 'L') and ('c_%i_l' % cs in row.keys())) or (
                    (self.lblpos == 'T') and ('c_%i' % cs in row[0].keys())):
                        colspan = colspan + 1
                    else:
                        break
                        
        kwargs = {}
        if self.lblpos == 'L':
            if rowspan > 1:
                kwargs['rowspan'] = str(rowspan)
            lbl_kwargs.update(kwargs)
            lblvalign = lbl_kwargs.pop('vertical_align', lblvalign)
            lblalign = lbl_kwargs.pop('align', lblalign)
            if '_class' in lbl_kwargs:
                lbl_kwargs['_class'] = self.lblclass + ' ' + lbl_kwargs['_class']
            else:
                lbl_kwargs['_class'] = self.lblclass
            if lblhref:
                cell = row.td(childname='c_%i_l' % c, childcontent=lbl, align=lblalign, vertical_align=lblvalign, **td_lbl_attr)
                if lblvalue:
                    lbl_kwargs['tabindex'] = -1 # prevent tab navigation to the zoom link
                    cell.a(childcontent=lblvalue, href=lblhref, **lbl_kwargs)
            else:
                cell = row.td(childname='c_%i_l' % c, align=lblalign, vertical_align=lblvalign, **td_lbl_attr)
                if lbl:
                    cell.div(childcontent=lbl, **lbl_kwargs)
            for k, v in row_attributes.items():
                # TODO: warn if row_attributes already contains the attribute k (and it has a different value)
                row.parentNode.attr[k] = v
            if colspan > 1:
                kwargs['colspan'] = str(colspan * 2 - 1)
            kwargs.update(td_field_attr)
            td = row.td(childname='c_%i_f' % c, align=fldalign, vertical_align=fldvalign, _class='%s tag_%s' %(self.fieldclass,tag), **kwargs)
            if colspan > 1:
                for cs in range(c + 1, c + colspan):
                    row.delItem('c_%i_l' % cs)
                    row.delItem('c_%i_f' % cs)
            if rowspan > 1:
                for rs in range(r + 1, r + rowspan):
                    row = self.getRow(rs)
                    for cs in range(c, c + colspan):
                        row.delItem('c_%i_l' % cs)
                        row.delItem('c_%i_f' % cs)
        elif self.lblpos == 'T':
            if colspan > 1:
                kwargs['colspan'] = str(colspan)
            lbl_kwargs.update(kwargs)
            lblvalign = lbl_kwargs.pop('vertical_align', lblvalign)
            lblalign = lbl_kwargs.pop('align', lblalign)
            if '_class' in lbl_kwargs:
                lbl_kwargs['_class'] = self.lblclass + ' ' + lbl_kwargs['_class']
            else:
                lbl_kwargs['_class'] = self.lblclass
            row[0].td(childname='c_%i' % c, childcontent=lbl, align=lblalign, vertical_align=lblvalign, **lbl_kwargs)
            td = row[1].td(childname='c_%i' % c, align=fldalign, vertical_align=fldvalign, **kwargs)
            for k, v in row_attributes.items():
                # TODO: warn if row_attributes already contains the attribute k (and it has a different value)
                row[0].parentNode.attr[k] = v
                row[1].parentNode.attr[k] = v
                
            if colspan > 1:
                for cs in range(c + 1, c + colspan):
                    row[0].delItem('c_%i' % cs)
                    row[1].delItem('c_%i' % cs)
                        
        if tag:
            field['placeholder'] = field.get('placeholder',field.pop('ghost', None))
            obj = td.child(tag, **field)
            return obj
                
class GnrDomSrc_dojo_14(GnrDomSrc_dojo_11):
    pass
    
class GnrDomSrc_dojo_15(GnrDomSrc_dojo_11):
    pass
    
class GnrDomSrc_dojo_18(GnrDomSrc_dojo_11):
    pass
    
class GnrGridStruct(GnrStructData):
    """This class handles the creation of a :ref:`struct`"""
    
    def makeRoot(cls, page, maintable=None, source=None):
        """TODO
        
        :param cls: TODO
        :param page: TODO
        :param maintable: the :ref:`database table <table>` to which the :ref:`struct` refers to.
                          For more information, check the :ref:`maintable` section
        :param source: TODO
        """
        root = GnrStructData.makeRoot(source=source, protocls=cls)
        #root._page = weakref.ref(page)
        root._page = page
        root._maintable = maintable
        return root
        
    makeRoot = classmethod(makeRoot)
        
    def _get_page(self):
        #return self.root._page()
        return self.root._page
        
    page = property(_get_page)
        
    def _get_maintable(self):
        return self.root._maintable
        
    maintable = property(_get_maintable)
        
    def _get_tblobj(self):
        maintable = self.root.maintable
        if maintable:
            return self.page.db.table(maintable)
        else:
            return None #self.page.tblobj
                
    tblobj = property(_get_tblobj)
        
    def view(self, tableobj=None, **kwargs):
        """TODO
        
        :param tableobj: the :ref:`database table <table>` object"""
        self.tableobj = tableobj
        return self.child('view', **kwargs)
        
    def rows(self, classes=None, cellClasses=None, headerClasses=None, **kwargs):
        """TODO
        
        :param classes: TODO
        :param cellClasses: TODO
        :param headerClasses: TODO"""
        return self.child('rows', classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
        
    def cell(self, field=None, name=None, width=None, dtype=None, classes=None, cellClasses=None, headerClasses=None,
             **kwargs):
        """Return a :ref:`cell`
        
        :param field: TODO
        :param name: TODO
        :param width: the width of the cell
        :param dtype: the :ref:`datatype`
        :param classes: TODO
        :param cellClasses: TODO
        :param headerClasses: TODO"""
        return self.child('cell', childcontent='', field=field, name=name or field, width=width, dtype=dtype,
                          classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
                          
    
    def checkboxcolumn(self,field='_checked',checkedId=None,radioButton=False,calculated=True,name=None,
                        checkedField=None,action=None,action_delay=None,remoteUpdate=False,**kwargs):
        calculated = not remoteUpdate
        self.cell(field=field,checkBoxColumn=dict(checkedId=checkedId,radioButton=radioButton,checkedField=checkedField,action=action,
                                                  action_delay=action_delay,remoteUpdate=remoteUpdate),calculated=calculated,name=name,
                                                  **kwargs)
        
    def checkboxcell(self, field=None, falseclass=None,
                     trueclass=None,nullclass=None, classes='row_checker', action=None, name=' ',
                     calculated=False, radioButton=False,threestate=None, **kwargs):
        """Return a :ref:`checkboxcell`
        
        :param field: TODO
        :param falseclass: the css class for the false state
        :param trueclass: the css class for the true state
        :param nullclass: the css class for the null state, the optional third state that you can
                          specify through the **threestate** parameter
        :param classes: TODO
        :param action: allow to execute a javascript callback. For more information, check the
                       :ref:`action_attr` page
        :param name: TODO
        :param calculated: boolean. TODO
        :param radioButton: boolean. TODO
        :param threestate: boolean. If ``True``, create a third state (the "null" state) besides the ``True``
                           and the ``False`` state"""
        if not field:
            field = '_checked'
            calculated = True
        falseclass = falseclass or ('checkboxOff' if not radioButton else falseclass or 'radioOff')
        trueclass = trueclass or ('checkboxOn' if not radioButton else trueclass or 'radioOn')
        
        threestate = threestate or False
        if threestate is True:
            nullclass = nullclass or ('checkboxOnOff' if not radioButton else nullclass or 'radioOnOff')
        elif threestate == 'disabled':
            nullclass = 'dimmed checkboxOnOff'
        elif threestate == 'hidden':
            nullclass = 'hidden'
        self.cell(field, name=name, format_trueclass=trueclass, format_falseclass=falseclass,format_nullclass=nullclass,
                  classes=classes, calculated=calculated, format_onclick="""
                                                                    var threestate ='%(threestate)s';

                                                                    var rowpath = '#'+this.widget.absIndex(kw.rowIndex);
                                                                    var sep = this.widget.datamode=='bag'? '.':'?';
                                                                    var valuepath=rowpath+sep+'%(field)s';
                                                                    var storebag = this.widget.storebag();                                                                    
                                                                    var blocked = this.form? this.form.isDisabled() : !this.widget.editorEnabled;
                                                                
                                                                    var checked = storebag.getItem(valuepath);
                                                                    if (blocked || ((checked===null) && (threestate=='disabled'))){
                                                                        return;
                                                                    }
                                                                    if(threestate=='True'){
                                                                        checked = checked===false?true:checked===true?null:false;
                                                                    }else{
                                                                        checked = !checked;
                                                                    }
                                                                    storebag.setItem(valuepath, checked);
                                                                    this.publish('checked_%(field)s',{row:this.widget.rowByIndex(kw.rowIndex),
                                                                                                      pkey:this.widget.rowIdByIndex(kw.rowIndex),
                                                                                                      checked:checked});
                                                                    %(action)s
                                                                    """ % dict(field=field, action=action or '',threestate=threestate)
                  , dtype='B', **kwargs)
                  

    def templatecell(self,field,name=None,template=None,table=None,**kwargs):
        table = table or self.tblobj.fullname
        tpl = self.page.loadTemplate('%s:%s' %(table,template))
        tplattr = tpl.getAttr('main')
        return self.cell(field,name=name,calculated=True,template_columns=('%(columns)s,%(virtual_columns)s' %tplattr).strip(','),template=template)


    def fieldcell(self, field, 
                _as=None, name=None, width=None, dtype=None,
                  classes=None, cellClasses=None, headerClasses=None,
                   zoom=False,template_name=None,table=None,**kwargs):
        tableobj = self.tblobj
        if table:
            tableobj = self.page.db.table(table)
            _as = field
            field = tableobj.pkey
            tbl_caption_field = tableobj.attributes.get('caption_field')
            caption_field = kwargs.get('caption_field') or '%s_caption' %_as
            kwargs['related_table'] = table
            kwargs['caption_field'] = caption_field
            kwargs['rowcaption'] = tbl_caption_field
            kwargs['relating_column'] = _as
            kwargs['related_column'] = tbl_caption_field


        if not tableobj:
            self.root._missing_table = True
            return
        fldobj = tableobj.column(field)
        cellpars = cellFromField(field,tableobj)
        cellpars.update(kwargs)
        template_name = template_name or fldobj.attributes.get('template_name')
        if template_name:
            tpl = self.page.loadTemplate('%s:%s' %(tableobj.fullname,template_name))
            tplattr = tpl.getAttr('main')
            cellpars['template_columns'] = ('%(columns)s,%(virtual_columns)s' %tplattr).strip(',')
        loc = locals()
        for attr in ('name','width','dtype','classes','cellClasses','headerClasses'):
            cellpars[attr] = loc[attr] or cellpars.get(attr)
        if zoom:
            zoomtbl = fldobj.table
            relfldlst = tableobj.fullRelationPath(field).split('.')
            if len(relfldlst) > 1:
                if zoom is True:
                    ridx = -2
                else:
                    ridx = relfldlst.index('@%s' % zoom)
                zoomtbl = tableobj.column('.'.join(relfldlst[0:ridx + 1])).parent
                relfldlst[ridx] = relfldlst[ridx][1:]
                cellpars['zoom_pkey'] = cellpars.get('zoom_pkey') or '.'.join(relfldlst[0:ridx + 1])
            elif fldobj.relatedTable():
                zoomtbl = fldobj.relatedTable()
                cellpars['zoom_pkey'] = field
            if hasattr(zoomtbl.dbtable, 'zoomUrl'):
                zoomPage = zoomtbl.dbtable.zoomUrl()
                cellpars['zoom_page'] = zoomPage
            cellpars['zoom_table'] = zoomtbl.dbtable.fullname
        return self.cell(field=_as or field, **cellpars)

    def fields(self, columns, unit='em', totalWidth=None):
        """TODO
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param unit: the field unit
        :param totalWidth: TODO
        
        r.fields('name/Name:20,address/My Addr:130px....')"""
        tableobj = self.tblobj
        if isinstance(columns, basestring):
            columns = columns.replace('\n', '').replace('\t', '')
            col_list = gnrstring.splitAndStrip(columns, ',')
            if '[' in columns:
                maintable = []
                columns = []
                for col in col_list:
                    if '[' in col:
                        tbl, col = col.split('[')
                        maintable = [tbl]
                    columns.append('.'.join(maintable + [col.rstrip(']')]))
                    if col.endswith(']'):
                        maintable = []
            else:
                columns = col_list
        fields = []
        names = []
        widths = []
        dtypes = []
        fld_kwargs = []
        wtot = 0
        for field in columns:
            field, width = gnrstring.splitAndStrip(field, sep=':', n=2, fixed=2)
            field, name = gnrstring.splitAndStrip(field, sep='/', n=2, fixed=2)
            fldobj = tableobj.column(field)
            if fldobj is None:
                raise Exception("Unknown field %s in table %s" % (
                field, tableobj.fullname)) # FIXME: use a specific exception class
            fields.append(field)
            names.append(name or fldobj.name_long)
            if r'%' in width:
                unit='%'
                width = width.replace('%','')
            width = int(width  or fldobj.print_width)
            widths.append(width)
            wtot = wtot + width
            dtypes.append(fldobj.dtype)
            fld_kwargs.append(dict()) #PROVVISORIO
            
        if totalWidth:
            for j, w in enumerate(widths):
                widths[j] = int(w * totalWidth / wtot)
        for j, field in enumerate(fields):
            #self.child('cell', field=field, childname=names[j], width='%i%s'%(widths[j],unit), dtype=dtypes[j])
            self.cell(field=field, name=names[j], width='%i%s' % (widths[j], unit), dtype=dtypes[j], **fld_kwargs[j])
            
    def getFieldNames(self, columns=None):
        """TODO
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section"""
        if columns is None:
            columns = []
        for v, fld in self.digest('#v,#a.field'):
            if fld:
                if not fld[0] in ('$', '@'):
                    fld = '$%s' % fld
                columns.append(fld)
            if isinstance(v, Bag):
                v.getFieldNames(columns)
        return ','.join(columns)
        
    fieldnames = property(getFieldNames)
        
if __name__ == '__main__':
    from gnr.app.gnrapp import GnrApp
        
    class PageStub(object):
        def __init__(self, apppath, pkgid):
            app = GnrApp(apppath)
            self.db = app.db
            self.packageId = pkgid
            
    page = PageStub('/usr/local/genro/data/instances/assopy', 'conference')
    root = GnrDomSrc_dojo_11.makeRoot(page)
    page.maintable = 'conference.speaker'
    fb = root.formbuilder(cols=1, dbtable=page.maintable)
    fb.field('area')
    fb.field('@card_id.name')
    fb.field('.address')
    a = root.toXml()
    print a