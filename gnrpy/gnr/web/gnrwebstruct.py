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
from gnr.core.gnrbag import Bag
from gnr.core.gnrstructures import GnrStructData
from gnr.core import gnrstring

from copy import copy

class GnrDomSrcError(Exception):
    pass
    
class GnrDomElem(object):
    def __init__(self,obj,tag):
        self.obj=obj
        self.tag=tag
        
    def __call__(self,*args,**kwargs):
        child=self.obj.child(self.tag,*args, **kwargs)
        return child
        
class GnrDomSrc(GnrStructData):
    """GnrDomSrc class"""
    def makeRoot(cls, page, source=None):
        root=GnrStructData.makeRoot(source=source, protocls=cls)
        #root._page=weakref.ref(page)
        root._page=page
        return root
    makeRoot = classmethod(makeRoot)
    
    def _get_page(self):
        #return self.root._page()
        return self.root._page
    page=property(_get_page)
    
    def _get_parentfb(self):
        if hasattr(self,'fbuilder'):
            return self.fbuilder
        elif self.parent:
            return self.parent.parentfb
    parentfb = property(_get_parentfb)
    
    def __getattr__(self,fname):
        fnamelower=fname.lower()
        if (fname != fnamelower) and hasattr(self,fnamelower) :
            return getattr(self,fnamelower)
        elif fnamelower in self.genroNameSpace:
            return GnrDomElem(self,'%s' % (self.genroNameSpace[fnamelower]))
        else:
            raise AttributeError("object has no attribute '%s'" % fname)
            
    def child(self, tag, name=None, envelope=None, **kwargs):
        if 'fld' in kwargs:
            fld_dict=self.getField(kwargs.pop('fld'))
            fld_dict.update(kwargs)
            kwargs=fld_dict
            t=kwargs.pop('tag',tag)
            if tag=='input':
                tag=t
            
        if hasattr(self,'fbuilder'):
            if not tag in ('tr','data','script','func','connect','dataFormula','dataScript','dataRpc','dataRemote','dataRecord','dataSelection', 'dataController'):
                if tag=='br':
                    return self.fbuilder.br()
                if not 'disabled' in kwargs:
                    kwargs['disabled']=self.childrenDisabled
                if 'unmodifiable' in kwargs and not 'readOnly' in kwargs:
                    kwargs['readOnly'] = '==!_newrecord'
                    kwargs['_newrecord'] = '^.?_newrecord'
                return self.fbuilder.place(tag=tag,name=name,**kwargs)
        if envelope:
            obj = GnrStructData.child(self, 'div', name='*_#', **envelope)
        else:
            obj = self
        return GnrStructData.child(obj, tag, name=name, **kwargs)
        
    def htmlChild(self,tag,content,value=None,**kwargs):
        if content and content.startswith('^'):
            kwargs['innerHTML']=content
            content=None
        elif value and value.startswith('^'):
            kwargs['innerHTML']=value
            value=None
        return self.child(tag,content=content,**kwargs)
        
    def nodeById(self,id):
        """docstring for findNode"""
        return self.findNodeByAttr('nodeId',id)
        
    def h1(self,content=None,**kwargs):
        return self.htmlChild('h1',content=content,**kwargs)

    def h2(self,content=None,**kwargs):
        return self.htmlChild('h2',content=content,**kwargs)

    def h3(self,content=None,**kwargs):
        return self.htmlChild('h3',content=content,**kwargs)

    def h4(self,content=None,**kwargs):
        return self.htmlChild('h4',content=content,**kwargs)

    def h5(self,content=None,**kwargs):
        return self.htmlChild('h5',content=content,**kwargs)

    def h6(self,content=None,**kwargs):
        return self.htmlChild('h6',content=content,**kwargs)
       
    def li(self,content=None,**kwargs):
        return self.htmlChild('li',content=content,**kwargs)
               
    def td(self,content=None,**kwargs):
        return self.htmlChild('td',content=content,**kwargs)
        
    def th(self,content=None,**kwargs):
        return self.htmlChild('th',content=content,**kwargs)
    
    def span(self,content=None,**kwargs):
        return self.htmlChild('span',content=content,**kwargs)
        
    def pre(self,content=None,**kwargs):
        return self.htmlChild('pre',content=content,**kwargs)
        
    def div(self,content=None,**kwargs):
        return self.htmlChild('div',content=content,**kwargs)

    
    def a(self,content=None,**kwargs):
        return self.htmlChild('a',content=content,**kwargs)  

    def dt(self,content=None,**kwargs):
        return self.htmlChild('dt',content=content,**kwargs)
    
    def option(self,content=None,**kwargs):
        return self.child('option',content=content,**kwargs) 
    
    def caption(self,content=None,**kwargs):
        return self.htmlChild('caption',content=content,**kwargs) 
   
    def button(self,caption=None,**kwargs):
        return self.child('button',caption=caption,**kwargs)
        
    def column(self, label='',field='',expr='',name='',**kwargs):
        if not 'columns' in self:
            self['columns']=Bag()
        if not field :
            field=label.lower()
        columns=self['columns']
        name ='C_%s' % str(len(columns))
        columns.setItem(name, None, label=label, field=field, expr=expr, **kwargs)
        
    def tooltip(self,label='',**kwargs):
        return self.child('tooltip',label=label,**kwargs)
        
    def data(self, *args, **kwargs):
        value = None
        className=None
        path=None
        if len(args)==1:
            if not kwargs:
                value=args[0]
                path=None
            else:
                path=args[0]
                value=None
        elif len(args)==0 and kwargs:
            path=None
            value=None
        elif len(args)>1:
            value=args[1]
            path=args[0]
        if isinstance(value,dict):
            value=Bag(value)
        if isinstance(value,Bag):
            className='bag'
        if '_serverpath' in kwargs:
            with self.page.pageStore() as store:
                store.setItem(kwargs['_serverpath'],value)
                store.subscribe_path(kwargs['_serverpath'])
        return self.child('data', __cls=className, content=value, path=path, **kwargs)
        
    def script(self, content='', **kwargs):
        return self.child('script',content=content, **kwargs)
        
    def remote(self, method, lazy=True, **kwargs):
        handler = self.page.getPublicMethod('remote',method)
        if handler:
            kwargs_copy = copy(kwargs)
            parentAttr = self.parentNode.getAttr()
            parentAttr['remote'] = 'remoteBuilder'
            parentAttr['remote_handler'] = method
            for k,v in kwargs.items():
                if k.endswith('_path'):
                    v = u'§%s' %v
                parentAttr['remote_%s' %k] = v
                kwargs.pop(k)
            if not lazy:
                onRemote = kwargs_copy.pop('_onRemote', None)
                if onRemote:
                    self.dataController(onRemote, _onStart=True)
                handler(self, **kwargs_copy)
        
    def func(self,name, pars='',funcbody=None, **kwargs):
        if not funcbody:
            funcbody=pars
            pars=''
        return self.child('func',name=name,pars=pars,content=funcbody, **kwargs)

    def connect(self, event='', pars='', funcbody=None, **kwargs):
        if not (funcbody and pars) :
            funcbody=event
            event=''
            pars=''
        elif not funcbody :
            funcbody=pars
            pars=''
        return self.child('connect',event=event,pars=pars,content=funcbody, **kwargs)
        
    def subscribe(self, what, event, func=None, **kwargs):
        objPath = None
        if not isinstance(what, basestring):
            objPath = what.fullpath
            what = None
        return self.child('subscribe', obj=what, objPath=objPath, event=event, content=func, **kwargs)

    def css(self, rule, styleRule=''):
        if ('{' in rule):
            styleRule=rule
            rule=styleRule.split('{')[0]
            rule=rule.strip()
        else:
            if not styleRule.endswith(';'):
                styleRule=styleRule+';'
            styleRule='%s {%s}'% (rule,styleRule)
        return self.child('css',name=None,content=styleRule)
    
    def styleSheet(self,cssText=None,cssTitle=None,href=None):
        self.child('stylesheet',name=None,content=cssText,href=href,cssTitle=cssTitle)
    
    def cssrule(self,selector=None,**kwargs):
        selector_replaced = selector.replace('.','_').replace('#','_').replace(' ','_')
        self.child('cssrule',name=selector_replaced,selector=selector,**kwargs)

    def macro(self,name='',source='',**kwargs):
        return self.child('macro',name=name,content=source,**kwargs)
        
    def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
                    lblalign=None, lblvalign='middle',
                    fldalign=None, fldvalign='middle', disabled=False,
                    rowdatapath=None, head_rows=None, **kwargs):
        """
        In formbuilder you can put dom and widget elements; its most classic usage is to create a form made by fields and layers,
        and that's because formbuilder can manage automatically fields and their positioning.
        
        * `cols`: set columns number. Default value is ``1``.
        * `dbtable`: set the database table. For more details, see :ref:`genro-dbtable`. Default value is ``None``.
        * `tblclass`: the standard class for the formbuilder. Default value is ``'formbuilder'`` (actually it is the unique defined class).
        * `lblclass`: set label style. Default value is ``'gnrfieldlabel'``.
        * `lblpos`: set label position. Default value is ``'L'``.
            Parameters:
            
            ``L``: set label on the left side of text field
            
            ``T``: set label on top of text field
        * `_class`: for CSS style.
        * `fieldclass`: CSS class appended to every formbuilder's child. Default value is ``gnrfield``.
        * `lblalign`: It seems broken ??? Set horizontal label alignment. Default value is ``None``.
        * `lblvalign`: set vertical label alignment. Default value is ``'middle'``.
        * `fldalign`: set field horizontal align. Default value is ``None``.
        * `fldvalign`: set field vertical align. Default value is ``'middle'``.
        * `disabled`: Add a description ???. Default value is ``False``.
        * `rowdatapath`: Add a description ???. Default value is ``None``.
        * `head_rows`: Add a description ???. Default value is ``None``.
        * `**kwargs`: allow to insert some additional paramaters:
            * `datapath`: set path for data. For more details, see :ref:`genro-datapath`.
            * `fld_` + CSSexpression: set a CSS expression to every formbuilder's field.
            (example: fld_color='red', fld_width='100%')
            * `lbl_` + CSSexpression: set a CSS expression to every lbl's field.
            (example: lbl_width='10em')
        """
        commonPrefix = ('lbl_','fld_','row_','tdf_','tdl_')
        commonKwargs = dict([(k,kwargs.pop(k)) for k in kwargs.keys() if len(k)>4 and k[0:4] in commonPrefix])
        tbl = self.child('table', _class='%s %s' % (tblclass, _class), **kwargs).child('tbody')
        tbl.fbuilder = GnrFormBuilder(tbl, cols=int(cols), dbtable=dbtable,
                lblclass=lblclass,lblpos=lblpos,lblalign=lblalign,fldalign=fldalign,fieldclass=fieldclass,
                lblvalign=lblvalign,fldvalign=fldvalign, rowdatapath=rowdatapath, head_rows=head_rows, commonKwargs=commonKwargs)
        tbl.childrenDisabled=disabled
        return tbl
        
    def place(self,fields):
        if hasattr(self,'fbuilder'):
            self.fbuilder.setFields(fields)
        
    def getField(self, fld):
        result={}
        if '.' in fld:
            x=fld.split('.')
            fld=x.pop()
            tblobj=self.page.db.table('.'.join(x), pkg=self.page.packageId)            
        else:
            tblobj=self.tblobj
            result['value']='^.%s' % fld
            
        fieldobj=tblobj.column(fld)
        if fieldobj is None:
            raise GnrDomSrcError('Not existing field %s' % fld)
        dtype=result['dtype']=fieldobj.dtype
        result['lbl']=fieldobj.name_long
        result['size']=20
        result.update(dict([(k,v) for k,v in fieldobj.attributes.items() if k.startswith('validate_')]))
        relcol = fieldobj.relatedColumn()
        
        if relcol != None: 
            lnktblobj = relcol.table
            linktable = lnktblobj.fullname
            result['tag']='DbSelect'
            result['dbtable']=linktable
            result['dbfield']=lnktblobj.rowcaption
            result['recordpath']=':@*'
            result['keyfield']=relcol.name
            result['_class']='linkerselect'
            if hasattr(lnktblobj,'zoomUrl'):
                zoomPage=lnktblobj.zoomUrl()
                
            else:
                zoomPage=linktable.replace('.','/')
            result['lbl_href']='^.%s?zoomUrl' % fld
            result['zoomPage']=zoomPage
        #elif attr.get('mode')=='M':
        #    result['tag']='bagfilteringtable'
        elif dtype == 'A':
            result['size'] = fieldobj.print_width or 10
            result['tag']='input'
            result['_type']='text'
        elif dtype == 'B':
            result['tag']='checkBox'
        elif dtype == 'T':
            result['size'] = fieldobj.print_width or 40
            result['tag']='input' 
        elif dtype == 'D':
            result['tag']='dropdowndatepicker'
        else:
            result['tag']='input'
        
        return result



class GnrDomSrc_dojo_11(GnrDomSrc):
    htmlNS=['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
                   'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
                   'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset', 
                   'h1', 'h2', 'h3','h4','h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input', 
                   'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
                   'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp', 
                   'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
                   'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul','audio','video','var','embed']

                                        
                                        
    dijitNS=['CheckBox','RadioButton','ComboBox','CurrencyTextBox','DateTextBox','FilteringSelect',
             'InlineEditBox','NumberSpinner','NumberTextBox','HorizontalSlider','VerticalSlider','Textarea','TextBox','TimeTextBox',
             'ValidationTextBox','AccordionContainer','AccordionPane','ContentPane','LayoutContainer','BorderContainer',
             'SplitContainer','StackContainer','TabContainer','Button','ToggleButton','ComboButton','DropDownButton','FilteringSelect',
             'Menu','Menubar','MenuItem','Toolbar','Dialog','ProgressBar','TooltipDialog',
             'TitlePane','Tooltip','ColorPalette','Editor','Tree','SimpleTextarea','MultiSelect']
    
    dojoxNS=['FloatingPane','Dock','RadioGroup','ResizeHandle','SizingPane','BorderContainer',
             'FisheyeList','Loader','Toaster','FileInput','fileInputBlind','FileInputAuto','ColorPicker',
             'SortList','TimeSpinner','Iterator','ScrollPane',
             'Gallery','Lightbox','SlideShow','ThumbnailPicker','Chart',
             'Deck','Slide','GoogleMap','Calendar','GoogleChart','GoogleVisualization',
             'Grid','VirtualGrid','VirtualStaticGrid']
    
    #gnrNS=['menu','menuBar','menuItem','Tree','Select','DbSelect','Combobox','Data',
           #'Css','Script','Func','BagFilteringTable','DbTableFilter','TreeCheck']
    gnrNS=['DbSelect','DbComboBox','DbView','DbForm','DbQuery','DbField','dataFormula','dataScript','dataRpc', 'dataController',
           'dataRemote','gridView','viewHeader','viewRow','script','func',
           'staticGrid','dynamicGrid','fileUploader','gridEditor','ckEditor','tinyMCE']
    genroNameSpace=dict([(name.lower(),name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(),name) for name in dijitNS]))
    genroNameSpace.update(dict([(name.lower(),name) for name in dojoxNS]))
    genroNameSpace.update(dict([(name.lower(),name) for name in gnrNS]))
    
    def dataFormula(self, path, formula, **kwargs):
        return self.child('dataFormula', path=path, formula=formula, **kwargs)
        
    def dataScript(self, path, script, **kwargs):
        return self.child('dataScript', path=path, script=script, **kwargs)
        
    def dataController(self, script=None, **kwargs):
        return self.child('dataController', script=script, **kwargs)
        
    def dataRpc(self, path, method, **kwargs):
        return self.child('dataRpc', path=path, method=method, **kwargs)
        
    def dataSelection(self, path, table=None, method='app.getSelection',columns=None,distinct=None,
                            where=None,order_by=None, group_by=None,having=None, columnsFromView=None, **kwargs):
        if 'name' in kwargs:
            kwargs['_name']=kwargs.pop('name')
        if 'content' in kwargs:
            kwargs['_content']=kwargs.pop('content')
        if not columns:
            if columnsFromView:
                columns='=grids.%s.columns' % columnsFromView #it is the view id
            else:
                columns='*'
            
        return self.child('dataRpc', path=path, table=table, method=method,columns=columns,
                                    distinct=distinct,where=where,order_by=order_by,group_by=group_by,
                                    having=having, **kwargs)

        
    def dataRecord(self, path, table, pkey=None, method='app.getRecord', **kwargs):
        return self.child('dataRpc', path=path,table=table, pkey=pkey, method=method, **kwargs)
               
    def dataRemote(self, path, method, **kwargs):
        return self.child('dataRemote', path=path, method=method, **kwargs)

    def includedview(self, storepath=None, structpath=None, struct=None,table=None,
                    nodeId = None, columns=None,**kwargs):
        nodeId = nodeId or self.page.getUuid()
        structpath = structpath or 'grids.%s.struct' %nodeId
        if not struct:
            struct=getattr(self.page,'%s_struct'%nodeId,None)
        if table and not struct:
            columns = columns or self.page.db.table(table).baseViewColumns()
            struct = self.page.newGridStruct(maintable=table)
            rows = struct.view().rows()
            rows.fields(columns)
        elif callable(struct) and not isinstance(struct,Bag):
            struct_cb = struct
            struct = self.page.newGridStruct(maintable=table)
            struct_cb(struct)
        if struct:
            self.data(structpath,struct)
        return self.child('includedView', storepath=storepath, structpath=structpath, nodeId=nodeId, table=table,**kwargs)
        
    def button(self,label=None,**kwargs):
        return self.child('button',label=label,**kwargs)
    
    def togglebutton(self,label=None,**kwargs):
        return self.child('togglebutton',label=label,**kwargs)
    
    def radiobutton(self,label=None,**kwargs):
        return self.child('radiobutton',label=label, **kwargs)
        
    def checkbox(self, label=None, value=None, **kwargs):
        return self.child('checkbox',value=value, label=label, **kwargs)

    def dropdownbutton(self,label=None,**kwargs):
        return self.child('dropdownbutton',label=label,**kwargs)
    
    def menuline(self, label=None, **kwargs):
        return self.child('menuline',label=label,**kwargs)
        
    def field(self, field=None, **kwargs):
        kwargs =self._fieldDecode(field,**kwargs)
        tag=kwargs.pop('tag')
        return self.child(tag,**kwargs)
    
    def placeFields(self, fieldlist=None, **kwargs):
        for field in fieldlist.split(','):
            kwargs =self._fieldDecode(field)
            tag=kwargs.pop('tag')
            self.child(tag,**kwargs)
        return self
        
    def radiogroup(self,labels,group,cols=1,datapath=None, **kwargs):
        if isinstance(labels,basestring):
            labels=labels.split(',')
        pane=self.div(datapath=datapath,**kwargs).formbuilder(cols=cols)
        for label in labels:
            if(datapath):
                pane.radioButton(label,group=group,datapath=':%s' % label)
            else:
                pane.radioButton(label,group=group)

    def checkboxgroup(self,labels,cols=1,datapath=None, **kwargs):
        if isinstance(labels,basestring):
            labels=labels.split(',')
        pane=self.div(datapath=datapath,**kwargs).formbuilder(cols=cols)
        for label in labels:
            if(datapath):
                pane.checkbox(label,datapath=':%s' % label)
            else:
                pane.checkbox(label)
        
    def _fieldDecode(self, fld, **kwargs):
        parentfb = self.parentfb
        tblobj = None
        if '.' in fld and not fld.startswith('@'):
            x=fld.split('.',2)
            maintable = '%s.%s' % (x[0],x[1])
            tblobj = self.page.db.table(maintable)
            fld=x[2]
        elif parentfb:
            tblobj = parentfb.tblobj
        else:
            raise GnrDomSrcError('No table')
        
        fieldobj=tblobj.column(fld)
        if fieldobj is None:
            raise GnrDomSrcError('Not existing field %s' % fld)
        wdgattr = self.wdgAttributesFromColumn(fieldobj,**kwargs)
        if fieldobj.getTag() == 'virtual_column' or (('@' in fld )and fld!=tblobj.fullRelationPath(fld)):
            wdgattr['readOnly'] = True
            wdgattr['_virtual_column'] = fld
        if wdgattr['tag']in ('div','span'):
            wdgattr['innerHTML']='^.%s' % fld
        else:
            wdgattr['value']='^.%s' % fld
        return wdgattr
        
    def wdgAttributesFromColumn(self, fieldobj, **kwargs):
        result= {'lbl': fieldobj.name_long, 'dbfield': fieldobj.fullname}
        dtype=result['dtype']=fieldobj.dtype
        if dtype in ('A','C'):
            size=fieldobj.attributes.get('size','20')
            if ':' in size:
                size=size.split(':')[1]
            size=int(size)
        else:
            size = 5
        result.update(dict([(k,v) for k,v in fieldobj.attributes.items() if k.startswith('validate_')]))
        if 'unmodifiable' in fieldobj.attributes:
            result['unmodifiable'] = fieldobj.attributes.get('unmodifiable')
        relcol = fieldobj.relatedColumn()
        if not relcol is None: 
            lnktblobj = relcol.table
            onerelfld=fieldobj.relatedColumnJoiner()['one_relation'].split('.')[2]
            if dtype in ('A','C'):
                size=lnktblobj.attributes.get('size','20')
                if ':' in size:
                    size=size.split(':')[1]
                size=int(size)
            else:
                size = 5
            defaultZoom=self.page.pageOptions.get('enableZoom',True)
            if kwargs.get('zoom',defaultZoom) :
                if hasattr(lnktblobj.dbtable,'zoomUrl'):
                    zoomPage=lnktblobj.dbtable.zoomUrl()
                else :
                    zoomPage=lnktblobj.fullname.replace('.','/')
                result['lbl_href']="=='/%s?pkey='+pkey" % zoomPage
                result['lbl_pkey']='^.%s' % fieldobj.name
                result['lbl__class']='gnrzoomlabel'
            result['lbl']=fieldobj.table.dbtable.relationName('@%s' % fieldobj.name)
            result['tag']='DbSelect'
            result['dbtable']=lnktblobj.fullname
            #result['columns']=lnktblobj.rowcaption
            result['_class']='linkerselect'
            result['searchDelay']=300
            result['ignoreCase']=True
            result['method']='app.dbSelect'
            result['size']=size
            result['_guess_width']='%iem' % (int(size*.7)+2)
            if(onerelfld != relcol.table.pkey):
                result['alternatePkey']=onerelfld
        #elif attr.get('mode')=='M':
        #    result['tag']='bagfilteringtable'
        elif dtype in ('A','T') and fieldobj.attributes.get('values', False):
            result['tag'] = 'filteringselect'
            result['values'] = fieldobj.attributes.get('values',[])
        elif dtype == 'A' :
            result['maxLength'] = size
            result['tag']='textBox'
            result['_type']='text'
            result['_guess_width']='%iem' % (int(size*.7)+2)
        elif dtype == 'B':
            result['tag']='checkBox'
            if 'autospan' in kwargs:
                kwargs['colspan'] = kwargs['autospan']
                del kwargs['autospan']
        elif dtype == 'T':
            result['tag']='textBox'
            result['_guess_width']='%iem' % int(size*.5)
        elif dtype == 'R':
            result['tag']='numberTextBox'
            result['width']='7em' 
        elif dtype == 'N':
            result['tag']='numberTextBox'
            result['_guess_width']='7em' 
        elif dtype == 'L' or dtype == 'I':
             result['tag']='numberTextBox'
             result['_guess_width']='7em' 
        elif dtype == 'D':
            result['tag']='dateTextBox'
            result['_guess_width']='9em' 
        elif dtype == 'H':
            result['tag'] = 'timeTextBox'
            result['_guess_width'] ='7em'
        else:
            result['tag']='textBox'
        if kwargs:
            if kwargs.get('autospan',False):
                kwargs['colspan'] = kwargs.pop('autospan')
                kwargs['width'] = '100%'
            result.update(kwargs)
        
        return result

class GnrFormBuilder(object):
    def __init__(self, tbl, cols=None, dbtable=None,fieldclass=None,
                lblclass='gnrfieldlabel',lblpos='L',lblalign=None,fldalign=None,
                lblvalign='middle',fldvalign='middle', rowdatapath=None, head_rows=None, commonKwargs=None):
        self.commonKwargs = commonKwargs or {}
        self.lblalign=lblalign or {'L':'right','T':'center'}[lblpos] # jbe?  why is this right and not left?
        self.fldalign=fldalign or {'L':'left','T':'center'}[lblpos]
        self.lblvalign=lblvalign
        self.fldvalign=fldvalign
        self.lblclass=lblclass
        self.fieldclass=fieldclass
        self.colmax=cols
        self.lblpos=lblpos
        self.rowlast=-1
        #self._tbl=weakref.ref(tbl)
        self._tbl=tbl
        self.maintable = dbtable or self.page.maintable
        if self.maintable:
            self.tblobj = self.page.db.table(self.maintable)
        self.rowcurr=-1
        self.colcurr=0
        self.row=-1
        self.col=-1
        self.rowdatapath = rowdatapath
        self.head_rows = head_rows or 0
        
    def br(self):
        #self.row=self.row+1
        
        self.col=999
        return self.tbl
        
    def _get_page(self):
        return self.tbl.page
    page = property(_get_page)
    
    def _get_tbl(self):
        #return self._tbl()
        return self._tbl
    tbl = property(_get_tbl)

    def place(self,**fieldpars):
        return self.setField(fieldpars)
        
        
    def setField(self, field, row=None, col=None):
        field=dict(field)
        if 'pos' in field:
            rc=('%s,0' % field.pop('pos')).split(',')
            if rc[0]=='*':
                rc[0]=str(self.row)
            elif rc[0]=='+':
                rc[0]=str(self.row+1)
            row,col=int(rc[0]),int(rc[1])
        
        if row is None:
            row = self.row
            col = self.col
        if col<0:
            col=self.colmax+col
        self.row, self.col=self.nextCell(row,col)
        if 'fld' in field:
            fld_dict=self.tbl.getField(field.pop('fld'))
            fld_dict.update(field)
            field=fld_dict
        return self._formCell(self.row, self.col, field)
        
        
    def setFields(self,fields,rowstart=0,colstart=0):
        for field in fields:      
            self.setField(field)
    
    def _fillRows(self, r):
        if r>self.rowlast:
            for j in range(self.rowlast,r):
                self._formRow(j+1)
                
    def setRowAttr(self, r, attrs):
        self._fillRows(r)
        if self.lblpos=='L':
            return self.tbl.setAttr('r_%i' % r, attrs)
        else:
            return (self.tbl.setAttr('r_%i_l' % r, attrs), self.tbl.setAttr('r_%i_f'% r, attrs))
        
    def getRowNode(self, r):
        self._fillRows(r)
        if self.lblpos=='L':
            return self.tbl.getNode('r_%i' % r)
        else:
            return (self.tbl.getNode('r_%i_l'% r), self.tbl.getNode('r_%i_f'% r))
        
    def getRow(self, r):
        self._fillRows(r)
        if self.lblpos=='L':
            return self.tbl['r_%i'% r]
        else:
            return (self.tbl['r_%i_l'% r], self.tbl['r_%i_f'% r])
            
    def nextCell(self, r, c):
        def nc(row,r,c):
            c=c+1
            if c>=self.colmax:
                c=0
                r=r+1
                row=self.getRow(r)
            return row,r,c
        row=self.getRow(r)
        row,r,c=nc(row,r,c)
        if self.lblpos=='L':
            while not 'c_%i_l'%c in row.keys():
                row,r,c=nc(row,r,c)
        else:
            while not 'c_%i'%c in row[0].keys():
                row,r,c=nc(row,r,c)
        return r,c
        
    def setRow(self, fields, row=None):
        colcurr=-1
        if row is None:
            row=self.rowcurr=self.rowcurr+1
        if row>self.rowlast:
            for r in range(self.rowlast,row):
                self._formRow(r+1)
        self._formRow(row)

        for f in fields:
            if not 'col' in f:
                col=colcurr=colcurr+1
            else:
                col=int(f.pop('col'))
            if col<=self.colmax:
                self.setField(f,row,col)
            
    def _formRow(self,r):
        if self.rowdatapath and r >= self.head_rows:
            rdp = '.r_%i' % (r - self.head_rows, )
        else:
            rdp = None
        if self.lblpos=='L':
            self.tbl.tr(name='r_%i' % r, datapath=rdp)
            
        elif self.lblpos=='T':
            self.tbl.tr(name='r_%i_l' % r, datapath=rdp)
            self.tbl.tr(name='r_%i_f' % r, datapath=rdp)
        self.rowlast=max(self.rowlast,r)
        
        for c in range(self.colmax):
            self._formCell(r,c)
            
    def _formCell(self, r, c, field=None):
        row=self.getRow(r)
        row_attributes = dict()
        td_field_attr = dict()
        td_lbl_attr = dict()
        lbl=''
        lblvalue=None
        tag=None
        rowspan,colspan=1,1
        lblalign, fldalign = self.lblalign, self.fldalign
        lblvalign, fldvalign = self.lblvalign, self.fldvalign
        lbl_kwargs={}
        lblhref=None
        if field is not None:
            f=dict(self.commonKwargs)
            f.update(field)
            field=f
            lbl=field.pop('lbl','')
            if 'lbl_href' in field:
                lblhref=field.pop('lbl_href')
                lblvalue=lbl
                lbl=None
            for k in field.keys():
                attr_name = k[4:] 
                if attr_name == 'class':
                    attr_name = '_class'
                if k.startswith('row_'):
                    row_attributes[attr_name] = field.pop(k)
                elif k.startswith('lbl_'):
                    lbl_kwargs[attr_name]= field.pop(k)
                elif k.startswith('fld_'):
                    v = field.pop(k)
                    if not attr_name in field:
                        field[attr_name] = v
                elif k.startswith('tdf_'):
                    td_field_attr[attr_name] = field.pop(k)
                elif k.startswith('tdl_'):
                    td_lbl_attr[attr_name] = field.pop(k)
                    
                
            
            lblalign, fldalign = field.pop('lblalign',lblalign), field.pop('fldalign',fldalign)
            lblvalign, fldvalign = field.pop('lblvalign',lblvalign), field.pop('fldvalign',fldvalign)
            tag=field.pop('tag',None)
            rowspan=int(field.pop('rowspan','1'))
            cspan=int(field.pop('colspan','1'))
            if cspan>1:
                for cs in range(c+1,c+cspan):
                    if ((self.lblpos=='L') and ('c_%i_l'%cs in row.keys())) or ((self.lblpos=='T') and ('c_%i' %cs in row[0].keys())):
                        colspan=colspan+1
                    else:
                        break
                        
        kwargs={}
        if self.lblpos=='L':
            if rowspan>1:
                kwargs['rowspan']=str(rowspan)
            lbl_kwargs.update(kwargs)
            lblvalign=lbl_kwargs.pop('vertical_align', lblvalign)
            lblalign=lbl_kwargs.pop('align', lblalign)
            if '_class' in lbl_kwargs:
                lbl_kwargs['_class']=self.lblclass+' '+lbl_kwargs['_class']
            else:
                lbl_kwargs['_class']=self.lblclass
            if lblhref:
                cell=row.td(name='c_%i_l' % c, content=lbl,align=lblalign,vertical_align=lblvalign,**td_lbl_attr)
                if lblvalue:
                    lbl_kwargs['tabindex'] = -1 # prevent tab navigation to the zoom link
                    cell.a(content=lblvalue,href=lblhref,**lbl_kwargs)
            else:
                
                cell=row.td(name='c_%i_l' % c,align=lblalign,vertical_align=lblvalign,**td_lbl_attr)
                if lbl:
                    cell.div(content=lbl,**lbl_kwargs)
            for k,v in row_attributes.items():
                # TODO: warn if row_attributes already contains the attribute k (and it has a different value)
                row.parentNode.attr[k] = v
            if colspan>1:
                kwargs['colspan']=str(colspan*2-1)
            kwargs.update(td_field_attr)
            td=row.td(name='c_%i_f' % c, align=fldalign,vertical_align=fldvalign,_class=self.fieldclass,**kwargs)
            if colspan>1:
                for cs in range(c+1,c+colspan):
                    row.delItem('c_%i_l' %cs)
                    row.delItem('c_%i_f' %cs)  
            if rowspan>1:
                for rs in range(r+1,r+rowspan):
                    row=self.getRow(rs)
                    for cs in range(c,c+colspan):
                        row.delItem('c_%i_l' %cs)
                        row.delItem('c_%i_f' %cs)                                 
        elif self.lblpos=='T':
            if colspan>1:
                kwargs['colspan']=str(colspan)
            lbl_kwargs.update(kwargs)
            row[0].td(name='c_%i' %c, content=lbl, align=lblalign, vertical_align=lblvalign,**lbl_kwargs)
            td=row[1].td(name='c_%i' %c,align=fldalign, vertical_align=fldvalign,**kwargs)
            for k,v in row_attributes.items():
                # TODO: warn if row_attributes already contains the attribute k (and it has a different value)
                row[0].parentNode.attr[k] = v
                row[1].parentNode.attr[k] = v
                
            if colspan>1:
                for cs in range(c+1,c+colspan):
                    row[0].delItem('c_%i' %cs)
                    row[1].delItem('c_%i' %cs)
            
        if tag:
            ghost = field.pop('ghost',None)
            if ghost:
                if ghost is True:
                    ghost = lbl
                field['id'] = field.get('id',None) or self.page.getUuid()
                td.label(_for=field['id'],_class='ghostlabel',id=field['id']+'_label').span(ghost)
                field['hasGhost'] = True
                #field['connect__onMouse'] = 'genro.dom.ghostOnEvent($1);' 
                #field['connect__onKeyPress'] = 'genro.dom.ghostOnEvent($1);' 
                #field['connect_setDisplayedValue'] = 'genro.dom.ghostOnEvent("setvalue");' 
            obj = td.child(tag,**field)
            return obj

class GnrDomSrc_dojo_14(GnrDomSrc_dojo_11):
    pass
    
class GnrDomSrc_dojo_15(GnrDomSrc_dojo_11):
    pass
    
class GnrGridStruct(GnrStructData):
    """
    r=struct.child('view').child('rows',classes='df_grid',cellClasses='df_cells',headerClasses='df_headers')
    r.child('cell',field='protocollo',width='9em',name='Protocollo')
    """
    def makeRoot(cls, page, maintable=None, source=None):
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
            return self.page.tblobj
    tblobj = property(_get_tblobj)

    def view(self, tableobj=None, **kwargs):
        self.tableobj = tableobj
        return self.child('view', **kwargs)

    def rows(self, classes=None, cellClasses=None, headerClasses=None, **kwargs):
        return self.child('rows', classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)

    def cell(self, field=None, name=None, width=None, dtype=None, classes=None, cellClasses=None, headerClasses=None, **kwargs):
        return self.child('cell', content= '', field=field, _name=name or field, width=width, dtype=dtype, 
                          classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
                          
    def checkboxcell(self,field=None,falseclass=None,
                        trueclass=None,classes='row_checker',action=None,name=' ',
                        calculated=False, radioButton=False, **kwargs):
        if not field:
            field='_checked'
            calculated = True
        falseclass= falseclass or ('checkboxOff' if not radioButton else falseclass or 'radioOff')
        trueclass= trueclass or ('checkboxOn' if not radioButton else trueclass or 'radioOn')
        
        self.cell(field,name=name,format_trueclass=trueclass,format_falseclass=falseclass,
                 classes=classes,calculated=calculated,format_onclick="""var idx = kw.rowIndex;
                                                                    var rowpath = '#'+idx;
                                                                    var sep = this.widget.gridEditor? '.':'?';
                                                                    var valuepath=rowpath+sep+'%s';
                                                                    var disabledpath = rowpath+'?disabled';
                                                                    var storebag = this.widget.storebag();
                                                                    if (storebag.getItem(disabledpath)){
                                                                        return;
                                                                    }
                                                                    var currval = storebag.getItem(valuepath);
                                                                    
                                                                    storebag.setItem(valuepath,!currval);
                                                                    
                                                                    """%field
                                                                    ,dtype='B', **kwargs)
                 
    def defaultArgsForDType(self, dtype):
        if dtype == 'B':
            return dict(format_trueclass="checkboxOn", format_falseclass="checkboxOff")
        else:
            return dict()
                 
    def fieldcell(self, field, _as=None, name=None, width=None, dtype=None, 
                  classes=None, cellClasses=None, headerClasses=None, zoom=False, **user_kwargs):
        tableobj = self.tblobj
        fldobj = tableobj.column(field)
        
        name = name or fldobj.name_long
        dtype = dtype or fldobj.dtype
        width = width or '%iem' % fldobj.print_width
        kwargs = self.defaultArgsForDType(dtype)
        kwargs.update(user_kwargs)
        if zoom:
            zoomtbl=fldobj.table
            relfldlst=tableobj.fullRelationPath(field).split('.')
            if len(relfldlst)>1:
                if zoom is True:
                    ridx=-2
                else:
                    ridx = relfldlst.index('@%s'% zoom)
                zoomtbl = tableobj.column('.'.join(relfldlst[0:ridx+1])).parent
                relfldlst[ridx]=relfldlst[ridx][1:]
                kwargs['zoomPkey']='.'.join(relfldlst[0:ridx+1])
            elif fldobj.relatedTable():
                zoomtbl = fldobj.relatedTable()
                kwargs['zoomPkey']=field
                    
            if hasattr(zoomtbl.dbtable,'zoomUrl'):
                zoomPage=zoomtbl.dbtable.zoomUrl()
            else:
                zoomPage=zoomtbl.fullname.replace('.','/')
            kwargs['zoomPage']=zoomPage
        return self.cell(field=_as or field, name=name, width=width, dtype=dtype, 
                          classes=classes, cellClasses=cellClasses, headerClasses=headerClasses, **kwargs)
     
     
    def fields(self, columns, unit='em',totalWidth=None):
        """
        r.fields('name/Name:20,address/My Addr:130px....')
        """
        tableobj = self.tblobj
        if isinstance(columns,basestring):
            columns=columns.replace('\n','').replace('\t','')
            col_list=gnrstring.splitAndStrip(columns,',')
            if '[' in columns:
                maintable=[]
                columns=[]
                for col in col_list:
                    if '[' in col:
                        tbl,col=col.split('[')
                        maintable=[tbl]
                    columns.append('.'.join(maintable+[col.rstrip(']')]))
                    if col.endswith(']'):
                        maintable=[]
            else:
                columns=col_list
        fields=[]
        names=[]
        widths=[]
        dtypes=[]
        fld_kwargs = []
        wtot=0
        for field in columns:
            field,width=gnrstring.splitAndStrip(field, sep=':', n=2, fixed=2)
            field,name=gnrstring.splitAndStrip(field, sep='/', n=2, fixed=2)
            fldobj = tableobj.column(field)
            if fldobj is None:
                raise Exception("Unknown field %s in table %s" % (field, tableobj.fullname)) # FIXME: use a specific exception class
            fields.append(field)
            names.append(name or fldobj.name_long)
            width=int(width  or fldobj.print_width)
            widths.append(width)
            wtot=wtot+width
            dtypes.append(fldobj.dtype)
            fld_kwargs.append(self.defaultArgsForDType(fldobj.dtype))

        if totalWidth:
            for j,w in enumerate(widths):
                widths[j]=int(w*totalWidth/wtot)
        for j,field in enumerate(fields):
            #self.child('cell', field=field, _name=names[j], width='%i%s'%(widths[j],unit), dtype=dtypes[j])
            self.cell(field=field, name=names[j], width='%i%s'%(widths[j],unit), dtype=dtypes[j], **fld_kwargs[j])
            
    def getFieldNames(self, columns=None):
        if columns is None:
            columns = []
        for v, fld in self.digest('#v,#a.field'):
            if fld:
                if not fld[0] in ('$','@'):
                    fld = '$%s' % fld
                columns.append(fld)
            if isinstance(v, Bag):
                v.getFieldNames(columns)
        return ','.join(columns)
    fieldnames=property(getFieldNames)
    
if __name__=='__main__':
    from gnr.app.gnrapp import GnrApp


    class PageStub(object):
        def __init__(self,apppath,pkgid):
            app = GnrApp(apppath)
            self.db=app.db
            self.packageId=pkgid
            
    page=PageStub('/usr/local/genro/data/instances/assopy','conference') 
    root=GnrDomSrc_dojo_11.makeRoot(page) 
    page.maintable = 'conference.speaker'
    fb=root.formbuilder(cols=1,dbtable=page.maintable)
    fb.field('area')
    fb.field('@card_id.name')
    fb.field('.address')
    a=root.toXml()
    print a
    
