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
        """add???"""
        return self.js_sourceNode('w')
    
    @property
    def js_domNode(self):
        """add???"""
        return self.js_sourceNode('d')
        
    @property
    def js_form(self):
        """add???"""
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
    
    def checkNodeId(self,nodeId):
        assert not nodeId in self.register_nodeId,'%s is duplicated' %nodeId
        self.page._register_nodeId[nodeId] = self
            
    @property
    def register_nodeId(self):
        if not hasattr(self.page,'_register_nodeId'):
            register = dict()
            self.page._register_nodeId = register
        return  self.page._register_nodeId
        
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
        raise AttributeError("object has no attribute '%s':Provide another nodeId" % fname)
    
    @deprecated
    def getAttach(self, childname):
        """.. deprecated:: 0.7"""
        childnode = self.getNode(childname)
        if childnode:
            return childnode._value
        
    def child(self, tag, childname=None,childcontent=None, envelope=None, **kwargs):
        """Set a new item of the ``tag`` type into the current structure through
        the :meth:`child() <gnr.core.gnrstructures.GnrStructData.child>` and return it
        
        :param tag: add???
        :param childname: the :ref:`childname`
        :param envelope: add???"""
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
        return GnrStructData.child(obj, tag, childname=childname, childcontent=childcontent,**kwargs)

        
    def htmlChild(self, tag, childcontent, value=None, **kwargs):
        """Create an html child and return it
        
        :param tag: the html tag
        :param childcontent: the html content
        :param value: add???"""
        if childcontent :
            kwargs['innerHTML'] = childcontent
            childcontent = None
        elif value:
            kwargs['innerHTML'] = value
            value = None
        return self.child(tag, childcontent=childcontent, **kwargs)
        
    def nodeById(self, id):
        """add???
        
        :param id: the node Id"""
        return self.findNodeByAttr('nodeId', id)
        
    def framepane(self, frameCode=None, centerCb=None, **kwargs):
        """Create a :ref:`framepane` and return it. A framePane is a :ref:`bordercontainer`
        with :ref:`frame_sides` attribute added: these sides follow the Dojo borderContainer
        suddivision: there is indeed the *top*, *bottom*, *left*, *right* and *center* regions
        
        :param frameCode: the framepane code
        :param centerCb: add???"""
        frameCode = frameCode or 'frame_#'
        if '#' in frameCode:
            frameCode = frameCode.replace('#',self.page.getUuid())
        frame = self.child('FramePane',frameCode=frameCode,autoslots='top,bottom,left,right,center',**kwargs)
        if callable(centerCb):
            centerCb(frame)
        return frame
        
    @property
    def record(self):
        """add???"""
        assert self.attributes['tag'] == 'FrameForm','only on FrameForm'
        return self.center.contentPane(datapath='.record')
        
    @extract_kwargs(store=True)
    def frameform(self,formId=None,frameCode=None,store=None,storeCode=None,slots=None,table=None,store_kwargs=None,**kwargs):
        """A decorator - :ref:`extract_kwargs`. add???
        
        :param formId: add???
        :param frameCode: add???
        :param store: add???
        :param storeCode: add???
        :param slots: add???
        :param table: the :ref:`table` name
        :param store_kwargs: add???"""
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
        
    def formstore(self,handler='recordCluster',nodeId=None,table=None,storeType=None,parentStore=None,**kwargs):
        """add???
        
        :param storepath: add???
        :param handler: add???. Default value is ``recordCluster``
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page
        :param table: the :ref:`table` name
        :param storeType: add???
        :param parentStore: add???
        :returns: the formstore"""
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
                            
    def formstore_handler(self,action,handler_type=None,**kwargs):
        """add???
        
        :param action: add???
        :param handler_type: add???. 
        :returns: the formstore handler
        """
        return self.child('formstore_handler',childname=action,action=action,handler_type=handler_type,**kwargs)
        
    def formstore_handler_addcallback(self,cb,**kwargs):
        """add???
        
        :param cb: add???
        :returns: add???
        """
        self.child('callBack',childcontent=cb,**kwargs)
        return self

    def iframe(self, childcontent=None, main=None, **kwargs):
        """Create an :ref:`iframe` and returns it
        
        :param childcontent: the html content
        :param main: add???"""
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
        """Create a :ref:`data` and returns it. ``data`` allows to define variables from server
        to client
        
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
        if '_serverpath' in kwargs:
            with self.page.pageStore() as store:
                store.setItem(kwargs['_serverpath'], value)
                store.subscribe_path(kwargs['_serverpath'])
        return self.child('data', __cls=className,childcontent=value,_returnStruct=False, path=path, **kwargs)
        
    def script(self, content='', **kwargs):
        """Handle the <script> html tag
        
        :param content: the <script> content. 
        :returns: the <script> html tag
        """
        return self.child('script', childcontent=content, **kwargs)
        
    def remote(self, method, lazy=True, **kwargs):
        """add???
        
        :param method: add???
        :param lazy: boolean. add???. Default value is ``True``
        """
        if callable(method):
            handler = method
        else:
            handler = self.page.getPublicMethod('remote', method)
        if handler:
            kwargs_copy = copy(kwargs)
            parentAttr = self.parentNode.getAttr()
            parentAttr['remote'] = 'remoteBuilder'
            parentAttr['remote_handler'] = method
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
        """add???
        
        :param name: add???
        :param pars: add???. Default value is ``''``
        :param funcbody: add???. 
        :returns: add???
        """
        if not funcbody:
            funcbody = pars
            pars = ''
        return self.child('func', childname=name, pars=pars, childcontent=funcbody, **kwargs)
        
    def connect(self, event='', pars='', funcbody=None, **kwargs):
        """add???
        
        :param event: add???. Default value is ``''``
        :param pars: add???. Default value is ``''``
        :param funcbody: add???. 
        :returns: add???
        """
        if not (funcbody and pars):
            funcbody = event
            event = ''
            pars = ''
        elif not funcbody:
            funcbody = pars
            pars = ''
        return self.child('connect', event=event, pars=pars, childcontent=funcbody, **kwargs)
        
    def subscribe(self, what, event, func=None, **kwargs):
        """add???
        
        :param what: add???
        :param event: add???
        :param func: add???. 
        :returns: add???
        """
        objPath = None
        if not isinstance(what, basestring):
            objPath = what.fullpath
            what = None
        return self.child('subscribe', obj=what, objPath=objPath, event=event, childcontent=func, **kwargs)
        
    def css(self, rule, styleRule=''):
        """Handle the CSS rules. add???
        
        :param rule: dict or list of CSS rules
        :param styleRule: add???. Default value is ``''``
        :returns: add???
        """
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
        
        :param cssText: add???. 
        :param cssTitle: add???. 
        :param href: add???. 
        :returns: add???
        """
        self.child('stylesheet',childname=None, childcontent=cssText, href=href, cssTitle=cssTitle)
        
    def cssrule(self, selector=None, **kwargs):
        """add???"""
        selector_replaced = selector.replace('.', '_').replace('#', '_').replace(' ', '_')
        self.child('cssrule',childname=selector_replaced, selector=selector, **kwargs)
        
    def macro(self, name='', source='', **kwargs):
        """add???
        
        :param name: add???. Default value is ``''``
        :param source: add???. Default value is ``''``
        :returns: add???"""
        return self.child('macro', childname=name, childcontent=source, **kwargs)
        
    def formbuilder(self, cols=1, table=None, tblclass='formbuilder',
                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
                    lblalign=None, lblvalign='middle',
                    fldalign=None, fldvalign='middle', disabled=False,
                    rowdatapath=None, head_rows=None, **kwargs):
        """In formbuilder you can put dom and widget elements; its most classic usage is to create
        a form made by fields and layers, and that's because formbuilder can manage automatically
        fields and their positioning.
        
        :param cols: set the number of columns.
        :param table: set the database :ref:`table`.
        :param tblclass: the standard class for the formbuilder. Default value is ``'formbuilder'``
                         (actually it is the unique defined class).
        :param lblclass: set label style.
        :param lblpos: set label position: ``L``: set label on the left side of text field.
                       ``T``: set label on top of text field. Default value is ``'L'``.
        :param _class: for CSS style.
        :param fieldclass: CSS class appended to every formbuilder's child.
        :param lblalign: Set horizontal label alignment (It seems broken... add???)
        :param lblvalign: set vertical label alignment.
        :param fldalign: set field horizontal align.
        :param fldvalign: set field vertical align. Default value is ``'middle'``.
        :param disabled: If ``True``, user can't act on the object (write, drag...).
        :param rowdatapath: add???
        :param head_rows: add???
        :param \*\*kwargs: for the complete list of the ``**kwargs``, check the :ref:`fb_kwargs` section"""
        commonPrefix = ('lbl_', 'fld_', 'row_', 'tdf_', 'tdl_')
        commonKwargs = dict([(k, kwargs.pop(k)) for k in kwargs.keys() if len(k) > 4 and k[0:4] in commonPrefix])
        tbl = self.child('table', _class='%s %s' % (tblclass, _class), **kwargs).child('tbody')
        dbtable = table or kwargs.get('dbtable') or self.getInheritedAttributes().get('table') or self.page.maintable
        tbl.fbuilder = GnrFormBuilder(tbl, cols=int(cols), dbtable=dbtable,
                                      lblclass=lblclass, lblpos=lblpos, lblalign=lblalign, fldalign=fldalign,
                                      fieldclass=fieldclass,
                                      lblvalign=lblvalign, fldvalign=fldvalign, rowdatapath=rowdatapath,
                                      head_rows=head_rows, commonKwargs=commonKwargs)
        inattr = self.getInheritedAttributes()
        if hasattr(self.page,'_legacy'):
            tbl.childrenDisabled = disabled
        return tbl
        
    def place(self, fields):
        """add???
        
        :param fields: add???"""
        if hasattr(self, 'fbuilder'):
            self.fbuilder.setFields(fields)
            
    def getField(self, fld):
        """add???
        
        :param fld: add???"""
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
    """add???"""
    htmlNS = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
              'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
              'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'frame', 'frameset',
              'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input',
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
             'tinyMCE', 'protovis', 'PaletteGroup', 'PalettePane','ImgUploader','TooltipPane', 'BagNodeEditor',
             'PaletteBagNodeEditor', 'Palette', 'PaletteTree', 'SearchBox', 'FormStore',
             'FramePane', 'FrameForm', 'SlotButton']
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
        :param \*\*kwargs: formula parameters and other ones (:ref:`css`, etc)"""
        return self.child('dataFormula', path=path, formula=formula, **kwargs)
        
    def dataScript(self, path, script, **kwargs):
        """.. deprecated:: 0.7

        .. warning:: The :ref:`datascript` has been substituted by :ref:`datacontroller`
                     and :ref:`dataformula`
                     
        :param path: the dataScript's path
        :param script: the dataScript's formula"""
        return self.child('dataScript', path=path, script=script, **kwargs)
        
    def dataController(self, script=None, **kwargs):
        """Create a :ref:`datacontroller` and returns it. dataController allows to
        execute Javascript code
        
        :param script: the Javascript code that ``datacontroller`` has to execute. 
        :param \*\*kwargs: *_init*, *_onStart*, *_timing*. For more information,
                       check the controllers' :ref:`controllers_attributes` section"""
        return self.child('dataController', script=script, **kwargs)
        
    def dataRpc(self, path, method, **kwargs):
        """Create a :ref:`datarpc` and returns it. dataRpc allows the client to make a call
        to the server to perform an action and returns it.
        
        :param path: MANDATORY - it contains the folder path of the result of the ``dataRpc`` action;
                     you have to write it even if you don't return any value in the ``dataRpc``
                     (in this situation it will become a "mandatory but dummy" parameter)
        :param method: the name of your ``dataRpc`` method
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section"""
        return self.child('dataRpc', path=path, method=method, **kwargs)
        
    def selectionstore_addcallback(self,*args,**kwargs):
        """add???
        
        :param args: add???
        :param \*\*kwargs: add???"""
        self.datarpc_addcallback(*args,**kwargs)
        
    def datarpc_addcallback(self,cb,**kwargs):
        """add???
        
        :param cb: add???
        :param \*\*kwargs: add???"""
        self.child('callBack',childcontent=cb,**kwargs)
        return self
        
    def datarpc_adderrback(self,cb,**kwargs):
        """add???
        
        :param cb: add???
        :param \*\*kwargs: add???"""
        self.child('callBack',childcontent=cb,_isErrBack=True,**kwargs)
        return self
        
    def slotButton(self,label=None,**kwargs):
        """add???"""
        return self.child(tag='SlotButton',label=label,**kwargs)
        
    def virtualSelectionStore(self,table=None,storeCode=None,storepath=None,columns=None,**kwargs):
        """add???
        
        :param storeCode: add???
        :param table: the :ref:`table` name
        :param storepath: add???
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section"""
        self.selectionStore(storeCode=storeCode,table=table, storepath=storepath,columns=columns,**kwargs)
        
    def selectionStore(self,table=None,storeCode=None,storepath=None,columns=None,**kwargs):
        """add???
        
        :param storeCode: add???. 
        :param table: the :ref:`table` name. 
        :param storepath: add???. 
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section. 
        :returns: the selectionStore"""
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
        return parent.child('SelectionStore',storepath=storepath, table=table, nodeId=nodeId,columns=columns,**kwargs)
        #ds = parent.dataSelection(storepath, table, nodeId=nodeId,columns=columns,**kwargs)
        #ds.addCallback('this.publish("loaded",{itemcount:result.attr.rowCount}')
    
    def onDbChanges(self,action=None,table=None,**kwargs):
        """add???"""
        self.page.subscribeTable(table,True)
        self.dataController(action,dbChanges="^gnr.dbchanges.%s" %table.replace('.','_'),**kwargs)
    
    def dataSelection(self, path, table=None, method='app.getSelection', columns=None, distinct=None,
                      where=None, order_by=None, group_by=None, having=None, columnsFromView=None, **kwargs):
        """Create a :ref:`dataselection` and returns it. dataSelection allows... add???
        
        :param path: add???
        :param table: the :ref:`table` name
        :param method: add???. Default value is ``app.getSelection``
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section.
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section. 
        :param group_by: the sql "GROUP BY" clause. For more information check the
                         :ref:`sql_group_by` section.
        :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
        :param columnsFromView: add???
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section"""
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
        """add???
        :param rootpath: add???
        :param storepath: add???. Default value is ``.store``"""
        store = DirectoryResolver(rootpath or '/', **kwargs)()
        self.data(storepath, store)
    
        
    def tableAnalyzeStore(self, table=None, where=None, group_by=None, storepath='.store', **kwargs):
        """add???
        
        :param pane: add???
        :param table: the :ref:`table` name
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where`
                      section
        :param group_by: the sql "GROUP BY" clause. For more information check the
                         :ref:`sql_group_by` section
        :param storepath: add???. Default value is ``.store``"""
        t0 = time()
        page = self.page
        tblobj = page.db.table(table)
        columns = [x for x in group_by if not callable(x)]
        selection = tblobj.query(where=where, columns=','.join(columns), **kwargs).selection()
        explorer_id = page.getUuid()
        freeze_path = page.site.getStaticPath('page:explorers', explorer_id)
        t1 = time()
        totalizeBag = selection.totalize(group_by=group_by, collectIdx=False)
        t2 = time()
        store = page.lazyBag(totalizeBag, name=explorer_id, location='page:explorer')()
        t3 = time()
        self.data(storepath, store, query_time=t1 - t0, totalize_time=t2 - t1, resolver_load_time=t3 - t2)
        
    def dataRecord(self, path, table, pkey=None, method='app.getRecord', **kwargs):
        """Create a :ref:`datarecord` and returns it. dataRecord allows... add???
        
        :param path: add???
        :param table: the :ref:`table` name
        :param pkey: the record primary key. 
        :param method: add???. Default value is ``app.getRecord``
        :param \*\*kwargs: *_onCalling*, *_onResult*, *sync*. For more information,
                           check the :ref:`rpc_attributes` section
        :returns: a dataRecord"""
        return self.child('dataRpc', path=path, table=table, pkey=pkey, method=method, **kwargs)
        
    def dataRemote(self, path, method, **kwargs):
        """Create a :ref:`dataremote` and returns it. dataRemote is a synchronous :ref:`datarpc`:
        it calls a (specified) dataRspc as its resolver. When ``dataRemote`` is brought to the
        client, it will be changed in a Javascript resolver that at the desired path perform
        the rpc (indicated with the ``remote`` attribute).
        
        :param path: the path where the dataRemote will save the result of the rpc
        :param method: the rpc name that has to be executed
        :param \*\*kwargs: *cacheTime=NUMBER*: The cache stores the retrieved value and keeps
                           it for a number of seconds equal to ``NUMBER``"""
        return self.child('dataRemote', path=path, method=method, **kwargs)
        
    def dataResource(self, path, resource=None, ext=None, pkg=None):
        """Create a :ref:`dataresource` and returns it. dataResource is a :ref:`dataRemote`
        that allows... add???
        
        :param path: add???
        :param resource: add???
        :param ext: add???
        :param pkg: add???"""
        self.dataRemote(path,'getResourceContent',resource=resource,ext=ext, pkg=pkg)
        
    def paletteGroup(self, groupCode, **kwargs):
        """add???
        
        :param groupCode: add???
        :returns: a paletteGroup"""
        return self.child('PaletteGroup',groupCode=groupCode,**kwargs)
        
    def palettePane(self, paletteCode, datapath=None, **kwargs):
        """add???
        
        :param paletteCode: add???. If no *datapath* is specified, the *paletteCode* will be used as *datapath*
        :param datapath: the path of data. For more information, check the :ref:`datapath` section"""
        datapath= 'gnr.palettes.%s' %paletteCode if datapath is None else datapath
        return self.child('PalettePane',paletteCode=paletteCode,datapath=datapath,**kwargs)
        
    def paletteTree(self, paletteCode, datapath=None, **kwargs):
        """add???
        
        :param paletteCode: add???. If no *datapath* is specified, the *paletteCode* will be used as *datapath*
        :param datapath: the path of data. For more information, check the :ref:`datapath` section
        :returns: a paletteTree"""
        datapath= datapath or 'gnr.palettes.%s' %paletteCode if datapath is None else datapath
        palette = self.child('PaletteTree',paletteCode=paletteCode,datapath=datapath,
                             autoslots='top,left,right,bottom',**kwargs)
        return palette
        
    def paletteGrid(self, paletteCode=None, struct=None, columns=None, structpath=None, datapath=None, **kwargs):
        """add???
        
        :param paletteCode: add???. If no *datapath* is specified, the *paletteCode* will be used as *datapath*
        :param struct: add???. 
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section. 
        :param structpath: add???. 
        :param datapath: the path of data. For more information, check the :ref:`datapath` section"""
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
                ivattr['onDrop_%s' % dropCode] = 'FIRE .dropped_%s = data' % dropCode
                ivattr['onCreated'] = """dojo.connect(widget,'_onFocus',function(){genro.publish("show_palette_%s")})""" % dropCode
                
    def newincludedview_draganddrop(self,dropCodes=None,**kwargs):
        self.includedview_draganddrop(dropCodes=dropCodes,**kwargs)
        
    def includedview(self, *args, **kwargs):
        """add???
        
        :param args: add???
        :param \*\*kwargs: add???
        :returns: add???"""
        frameCode = kwargs.get('parentFrame') or self.attributes.get('frameCode')
        if frameCode:
            kwargs['frameCode'] = frameCode
            return self.includedview_inframe(*args,**kwargs)
        else:
            return self.includedview_legacy(*args,**kwargs)
            
    def includedview_inframe(self, frameCode=None, struct=None, columns=None, storepath=None, structpath=None,
                             datapath=None, nodeId=None, configurable=True, _newGrid=False,childname=None,**kwargs):
        """add???
        
        :param frameCode: add???
        :param struct: add???
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param storepath: add???
        :param structpath: add???
        :param datapath: the path of data. For more information, check the :ref:`datapath` section
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page
        :param configurable: boolean. add???
        :param _newGrid: boolean. add???"""
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
        
    def includedview_legacy(self, storepath=None, structpath=None, struct=None,columns=None, table=None,
                            nodeId=None, relativeWorkspace=None, **kwargs):
        """add???
        
        :param storepath: add???
        :param structpath: add???
        :param struct: add???
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param table: the :ref:`table` name
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page
        :param relativeWorkspace: add???"""
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
        """add???
        
        :param struct: add???
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section"""
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
        """Create a :ref:`slotToolbar <toolbar>` and returns it.
        
        .. note:: a slotToolbar is a :meth:`slotBar` with some css preset. For more
                  information, check the :ref:`slotToolbar <toolbar>` page"""
        kwargs['toolbar'] = True
        return self.slotBar(*args,**kwargs)
        
    def slotFooter(self,*args,**kwargs):
        """add???
        
        :param \*args: add???
        :param \*\*kwargs: add???"""
        kwargs['_class'] = 'frame_footer'
        return self.slotBar(*args,**kwargs)
        
    def _addSlot(self,slot,prefix=None,frame=None,frameCode=None,namespace=None,**kwargs):
        s=self.child('slot',childname=slot)
        s.frame = frame
        slothandle = getattr(s,'%s_%s' %(prefix,slot),None)
        if not slothandle:
            if namespace:
                slothandle = getattr(s,'slotbar_%s_%s' %(namespace,slot),None)
            if not slothandle:
                slothandle = getattr(s,'slotbar_%s' %slot,None)
        if slothandle:
            kw = dict()
            kw[slot] = kwargs.pop(slot,None)
            kw.update(dictExtract(kwargs,'%s_' %slot,True))
            kw['frameCode'] = frameCode
            slothandle(**kw)
            
    def slotBar(self,slots=None,slotbarCode=None,namespace=None,childname='bar',**kwargs):
        """Create a :ref:`slotBar <toolbar>` and returns it
        
        :param slots: create a configurable UI inside the div or pane in which the
                      slotToolbar is defined. For more information, check the
                      :ref:`toolbar_slots` section
        :param slotbarCode: autocreate a :ref:`nodeid` for the slotToolbar AND autocreate
                            hierarchic nodeIds for every slotToolbar child
        :param namespace: add???
        :param childname: the slotBar :ref:`childname`"""
        namespace = namespace or self.parent.attributes.get('namespace')
        tb = self.child('slotBar',slotbarCode=slotbarCode,slots=slots,childname=childname,**kwargs)
        toolbarArgs = tb.attributes
        slots = gnrstring.splitAndStrip(str(slots))
        frame = self.parent
        frameCode = self.getInheritedAttributes().get('frameCode')
        prefix = slotbarCode or frameCode
        for slot in slots:
            if slot!='*' and slot!='|' and not slot.isdigit():
                tb._addSlot(slot,prefix=prefix,frame=frame,frameCode=frameCode,namespace=namespace,**toolbarArgs)
        return tb
        
        #se ritorni la toolbar hai una toolbar vuota 
    
    def slotbar_replaceslots(self, toReplace, replaceStr):
        """The :ref:`replaceslots` allows to redefine the preset bars of the :ref:`slotBars <toolbar>`
        and the :ref:`slotToolbars <toolbar>`
        
        :param toReplace: MANDATORY. A string with the list of the slots to be replaced.
                          Use ``#`` to replace all the slots
        :param replaceStr: MANDATORY. A string with the list of the slots to add"""
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
                    self._addSlot(slot,prefix=prefix,frame=frame,frameCode=frameCode,namespace=namespace,**toolbarArgs)
                    
    def button(self, label=None, **kwargs):
        return self.child('button', label=label, **kwargs)
        
    def togglebutton(self, label=None, **kwargs):
        return self.child('togglebutton', label=label, **kwargs)
        
    def radiobutton(self, label=None, **kwargs):
        return self.child('radiobutton', label=label, **kwargs)
        
    def checkbox(self, label=None, value=None, **kwargs):
        return self.child('checkbox', value=value, label=label, **kwargs)
        
    def dropdownbutton(self, label=None, **kwargs):
        return self.child('dropdownbutton', label=label, **kwargs)
        
    def menuline(self, label=None, **kwargs):
        return self.child('menuline', label=label, **kwargs)
        
    def field(self, field=None, **kwargs):
        """add???"""
        newkwargs = self._fieldDecode(field, **kwargs)
        newkwargs.update(kwargs)
        tag = newkwargs.pop('tag')
        return self.child(tag, **newkwargs)
        
    def placeFields(self, fieldlist=None, **kwargs):
        for field in fieldlist.split(','):
            kwargs = self._fieldDecode(field)
            tag = kwargs.pop('tag')
            self.child(tag, **kwargs)
        return self
        
    def radiogroup(self, labels, group, cols=1, datapath=None, **kwargs):
        if isinstance(labels, basestring):
            labels = labels.split(',')
        pane = self.div(datapath=datapath, **kwargs).formbuilder(cols=cols)
        for label in labels:
            if(datapath):
                pane.radioButton(label, group=group, datapath=':%s' % label)
            else:
                pane.radioButton(label, group=group)
                
    def checkboxtext(self, labels,value=None,separator=',',**kwargs):
        """A group of checkboxes that allow to compose a string with checkbox labels.
                
        :param labels: a string separated by comma set of words. For every words there will be
                       created a single checkbox
        :param value: the path of the checkboxtext value
        :param separator: the characters that separate the checkbox text"""
        labels = gnrstring.splitAndStrip(labels.replace('\n',','),',')
        action = """var actionNode = this.sourceNode.attributeOwnerNode('action');
                    var separator = actionNode.attr._separator;
                    var textvalue = actionNode.getAttributeFromDatasource('_textvalue');
                    var textvaluepath = actionNode.attr._textvalue;
                    var values = textvalue?textvalue.split(separator):[];
                    var k = dojo.indexOf(values,$1.label);
                    var v;
                    if(k<0){
                        values.push($1.label);
                        v = true;
                    }else{
                        values.splice(k,1);
                        v=false;
                    }
                    this.setAttribute('checked',v);
                    actionNode.setRelativeData(textvaluepath,values.join(separator),null,null,'cbgroup');
                """
        fb = self.formbuilder(_textvalue=value.replace('^','='),action=action,_separator=separator,**kwargs)
        self.dataController("""if(_triggerpars.kw.reason=='cbgroup'){return}
                                var values = textvalue? textvalue.split(separator):[];
                                var that = this;
                                var label;
                                var srcbag = fb._value;
                                srcbag.walk(function(n){if(n.attr.tag=='checkbox'){n.widget.setAttribute('checked',false)}});
                                var node;
                                dojo.forEach(values,function(n){
                                    node = srcbag.getNodeByAttr('label',n)
                                    if(node){
                                        node.widget.setAttribute('checked',true);
                                    }else{
                                        console.log('removed value  >'+n+'< from options');
                                    }
                                });
                            """,textvalue=value,separator=separator,fb=fb)
        for label in labels:
            fb.checkbox(label,_cbgroup=True)
                
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
        wdgattr = self.wdgAttributesFromColumn(fieldobj, **kwargs)
        if fieldobj.getTag() == 'virtual_column' or (('@' in fld )and fld != tblobj.fullRelationPath(fld)):
            wdgattr['readOnly'] = True
            wdgattr['_virtual_column'] = fld
        if wdgattr['tag']in ('div', 'span'):
            wdgattr['innerHTML'] = '^.%s' % fld
        else:
            wdgattr['value'] = '^.%s' % fld
        return wdgattr
        
    def wdgAttributesFromColumn(self, fieldobj, **kwargs):
        """add???
        
        :param fieldobj: add???
        :returns: add???
        """
        result = {'lbl': fieldobj.name_long, 'dbfield': fieldobj.fullname}
        dtype = result['dtype'] = fieldobj.dtype
        if dtype in ('A', 'C'):
            size = fieldobj.attributes.get('size', '20')
            if ':' in size:
                size = size.split(':')[1]
            size = int(size)
        else:
            size = 5
        result.update(dict([(k, v) for k, v in fieldobj.attributes.items() if k.startswith('validate_')]))
        if 'unmodifiable' in fieldobj.attributes:
            result['unmodifiable'] = fieldobj.attributes.get('unmodifiable')
        if 'protected' in fieldobj.attributes:
            result['protected'] = fieldobj.attributes.get('protected')
        relcol = fieldobj.relatedColumn()
        if not relcol is None:
            lnktblobj = relcol.table
            onerelfld = fieldobj.relatedColumnJoiner()['one_relation'].split('.')[2]
            if dtype in ('A', 'C'):
                size = lnktblobj.attributes.get('size', '20')
                if ':' in size:
                    size = size.split(':')[1]
                size = int(size)
            else:
                size = 5
            defaultZoom = self.page.pageOptions.get('enableZoom', True)
            if kwargs.get('zoom', defaultZoom):
                if hasattr(self.page,'_legacy'):
                    if hasattr(lnktblobj.dbtable, 'zoomUrl'):
                        zoomPage = lnktblobj.dbtable.zoomUrl()
                    else:
                        zoomPage = lnktblobj.fullname.replace('.', '/')
                    result['lbl_href'] = "=='/%s?pkey='+pkey" % zoomPage
                    result['lbl_pkey'] = '^.%s' % fieldobj.name
                else:
                    if hasattr(lnktblobj.dbtable, 'zoomUrl'):
                        pass
                    else:
                        zoomUrl = 'sys/thpage/%s' %lnktblobj.fullname.replace('.', '/')
                        result['lbl_zoomUrl'] = zoomUrl
                        result['lbl_pkey'] = '.%s' % fieldobj.name
                        result['lbl_connect_onclick'] = "genro.dlg.zoomPalette(this,$1);"                    
                result['lbl__class'] = 'gnrzoomlabel'
            result['lbl'] = fieldobj.table.dbtable.relationName('@%s' % fieldobj.name)
            result['tag'] = 'DbSelect'
            result['dbtable'] = lnktblobj.fullname
            #result['columns']=lnktblobj.rowcaption
            result['_class'] = 'linkerselect'
            result['searchDelay'] = 300
            result['ignoreCase'] = True
            result['method'] = 'app.dbSelect'
            result['size'] = size
            result['_guess_width'] = '%iem' % (int(size * .7) + 2)
            if(onerelfld != relcol.table.pkey):
                result['alternatePkey'] = onerelfld
        #elif attr.get('mode')=='M':
        #    result['tag']='bagfilteringtable'
        elif dtype in ('A', 'T') and fieldobj.attributes.get('values', False):
            result['tag'] = 'filteringselect'
            result['values'] = fieldobj.attributes.get('values', [])
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
        else:
            result['tag'] = 'textBox'
        if kwargs:
            if kwargs.get('autospan', False):
                kwargs['colspan'] = kwargs.pop('autospan')
                kwargs['width'] = '100%'
            result.update(kwargs)
                
        return result
        
class GnrFormBuilder(object):
    """add???"""
    def __init__(self, tbl, cols=None, dbtable=None, fieldclass=None,
                 lblclass='gnrfieldlabel', lblpos='L', lblalign=None, fldalign=None,
                 lblvalign='middle', fldvalign='middle', rowdatapath=None, head_rows=None, commonKwargs=None):
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
        """add???"""
        return self.setField(fieldpars)
        
    def setField(self, field, row=None, col=None):
        """add???
        
        :param field: add???
        :param row: add???. 
        :param col: add???. 
        :returns: add???
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
        """add???
        
        :param fields: add???
        :param rowstart: add???.
        :param colstart: add???."""
        for field in fields:
            self.setField(field)
                
    def _fillRows(self, r):
        if r > self.rowlast:
            for j in range(self.rowlast, r):
                self._formRow(j + 1)
                
    def setRowAttr(self, r, attrs):
        """add???
        
        :param r: add???
        :param attrs: add???
        :returns: add???
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl.setAttr('r_%i' % r, attrs)
        else:
            return (self.tbl.setAttr('r_%i_l' % r, attrs), self.tbl.setAttr('r_%i_f' % r, attrs))
                
    def getRowNode(self, r):
        """add???
        
        :param r: add???
        :returns: add???
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl.getNode('r_%i' % r)
        else:
            return (self.tbl.getNode('r_%i_l' % r), self.tbl.getNode('r_%i_f' % r))
                
    def getRow(self, r):
        """add???
        
        :param r: add???
        :returns: add???
        """
        self._fillRows(r)
        if self.lblpos == 'L':
            return self.tbl['r_%i' % r]
        else:
            return (self.tbl['r_%i_l' % r], self.tbl['r_%i_f' % r])
                
    def nextCell(self, r, c):
        """add???
        
        :param r: add???
        :param c: add???
        :returns: add???
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
        """add???
        
        :param fields: add???
        :param row: add???. 
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
            td = row.td(childname='c_%i_f' % c, align=fldalign, vertical_align=fldvalign, _class=self.fieldclass, **kwargs)
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
            field['placeholder'] = field.pop('ghost', None)
            #if ghost:
            #    if ghost is True:
            #        ghost = lbl
            #    field['id'] = field.get('id', None) or self.page.getUuid()
            #    td.label(_for=field['id'], _class='ghostlabel', id=field['id'] + '_label').span(ghost)
            #    field['hasGhost'] = True
                #field['connect__onMouse'] = 'genro.dom.ghostOnEvent($1);' 
                #field['connect__onKeyPress'] = 'genro.dom.ghostOnEvent($1);' 
                #field['connect_setDisplayedValue'] = 'genro.dom.ghostOnEvent("setvalue");' 
            obj = td.child(tag, **field)
            return obj
                
class GnrDomSrc_dojo_14(GnrDomSrc_dojo_11):
    pass
    
class GnrDomSrc_dojo_15(GnrDomSrc_dojo_11):
    pass
    
class GnrDomSrc_dojo_16(GnrDomSrc_dojo_11):
    pass
class GnrGridStruct(GnrStructData):
    """This class handles the creation of a :ref:`struct`
    
    add??? (introduce the example)
    
    ::
    
        r = struct.child('view').child('rows',classes='df_grid',cellClasses='df_cells',headerClasses='df_headers')
        r.child('cell',field='procedure',width='9em',name='Procedure')"""
        
    def makeRoot(cls, page, maintable=None, source=None):
        """add???
        
        :param cls: add???
        :param page: add???
        :param maintable: the table to which the struct refers to. For more information,
                          check the :ref:`webpages_maintable` section.
        :param source: add???. 
        :returns: add???
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
        """add???
        
        :param tableobj: add???. 
        :returns: add???
        """
        self.tableobj = tableobj
        return self.child('view', **kwargs)
        
    def rows(self, classes=None, cellClasses=None, headerClasses=None, **kwargs):
        """add???
        
        :param classes: add???. 
        :param cellClasses: add???. 
        :param headerClasses: add???. 
        :returns: add???
        """
        return self.child('rows', classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
        
    def cell(self, field=None, name=None, width=None, dtype=None, classes=None, cellClasses=None, headerClasses=None,
             **kwargs):
        """Return a :ref:`cell`.
        
        :param field: add???.
        :param name: add???.
        :param width: the width of the cell
        :param dtype: the :ref:`datatype`.
        :param classes: add???.
        :param cellClasses: add???.
        :param headerClasses: add???."""
        return self.child('cell', childcontent='', field=field, name=name or field, width=width, dtype=dtype,
                          classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
                          
    def checkboxcell(self, field=None, falseclass=None,
                     trueclass=None,nullclass=None, classes='row_checker', action=None, name=' ',
                     calculated=False, radioButton=False,threestate=False, **kwargs):
        """Return a boolean checkbox :ref:`cell`. add???
        
        :param field: add???.
        :param falseclass: the css class for the false state.
        :param trueclass: the css class for the true state.
        :param nullclass: the css class for the null state, the optional third state that you can
                          specify through the **threestate** parameter
        :param classes: add???. Default value is ``row_checker``
        :param action: allow to execute a javascript callback. For more information, check the
                       :ref:`action_attr` documentation page
        :param name: add???. Default value is ``' '``
        :param calculated: boolean. add???.
        :param radioButton: boolean. add???.
        :param threestate: boolean. If ``True``, create a third state (the "null" state) besides the ``True``
                           and the ``False`` state."""
        if not field:
            field = '_checked'
            calculated = True
        falseclass = falseclass or ('checkboxOff' if not radioButton else falseclass or 'radioOff')
        trueclass = trueclass or ('checkboxOn' if not radioButton else trueclass or 'radioOn')
        if threestate:
            nullclass = nullclass or ('checkboxOnOff' if not radioButton else nullclass or 'radioOnOff')

        self.cell(field, name=name, format_trueclass=trueclass, format_falseclass=falseclass,format_nullclass=nullclass,
                  classes=classes, calculated=calculated, format_onclick="""
                                                                    var threestate =('%(threestate)s' == 'True');
                                                                    var rowpath = '#'+this.widget.absIndex(kw.rowIndex);
                                                                    var sep = this.widget.gridEditor? '.':'?';
                                                                    var valuepath=rowpath+sep+'%(field)s';
                                                                    var storebag = this.widget.storebag();
                                                                    var blocked = this.form? (this.form.locked || this.form.isProtectWrite()) : !this.widget.editorEnabled;
                                                                    if (blocked){
                                                                        return;
                                                                    }
                                                                    var checked = storebag.getItem(valuepath);
                                                                    if(threestate){
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
                  

    def fieldcell(self, field, _as=None, name=None, width=None, dtype=None,
                  classes=None, cellClasses=None, headerClasses=None, zoom=False, **kwargs):
        """Return a :ref:`cell` that inherits every attribute from the :ref:`field` widget.

        :param field: MANDATORY - it contains the name of the :ref:`field` from which
                      the fieldcell inherits.
        :param _as: add???. 
        :param name: with *name* you can override the :ref:`name_long` of the
                     :ref:`field` form widget. 
        :param width: the fieldcell width. 
        :param dtype: the :ref:`datatype`. You can override the *dtype* of the :ref:`field` form widget.
        :param classes: add???. 
        :param cellClasses: add???. 
        :param headerClasses: add???. 
        :param zoom: a link to the object to which the fieldcell refers to.
                     For more information, check the :ref:`zoom` documentation page."""
        if not self.tblobj:
            self.root._missing_table = True
            return
        tableobj = self.tblobj
        fldobj = tableobj.column(field)
        
        name = name or fldobj.name_long
        dtype = dtype or fldobj.dtype
        width = width or '%iem' % fldobj.print_width
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
                kwargs['zoomPkey'] = '.'.join(relfldlst[0:ridx + 1])
            elif fldobj.relatedTable():
                zoomtbl = fldobj.relatedTable()
                kwargs['zoomPkey'] = field
                
            if hasattr(zoomtbl.dbtable, 'zoomUrl'):
                zoomPage = zoomtbl.dbtable.zoomUrl()
            else:
                zoomPage = zoomtbl.fullname.replace('.', '/')
            kwargs['zoomPage'] = zoomPage
        return self.cell(field=_as or field, name=name, width=width, dtype=dtype,
                         classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
                         
    def fields(self, columns, unit='em', totalWidth=None):
        """add???
        
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section.
        :param unit: the field unit. Default value is ``em``
        :param totalWidth: add???. 
        
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
        """add???
        
        :param columns: it represents the :ref:`table_columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section. """
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