#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

from past.builtins import basestring
import os,sys,math
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrhtml import GnrHtmlSrc
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrstring import  splitAndStrip, slugify,templateReplace
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrbag import Bag


def page_proxy(*args,**metadata):
    """page proxy"""
    if metadata:
        def decore(cls):
            cls.is_proxy = True
            inherites =metadata.get('inherites',None)
            if inherites:
                py_requires = getattr(cls,'py_requires',None)
                inherites_requires = ['{req} AS _CURRENT_PROXY_'.format(req=req) for req in inherites.split(',')]
                inherites_requires = ','.join(inherites_requires)
                if py_requires:
                    py_requires = '{inherites_requires},{py_requires}'.format(inherites_requires=inherites_requires,
                                                            py_requires=py_requires)
                else:
                    py_requires = inherites_requires
                print('py_requires',py_requires)
                cls.py_requires = py_requires
            return cls
        return decore
    else:
        cls = args[0]
        cls.is_proxy = True 
        return cls


def page_mixin(func):
    """TODO
    
    :param func: TODO"""
    def decore(self, obj, *args, **kwargs):
        setattr(func, '_mixin_type', 'page')
        result = func(self, obj, *args, **kwargs)
        return result
        
    return decore

def zzzcomponent_hook(func_or_name):
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
        """TODO
        
        :param func:"""
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
        
class BaseComponent(object):
    """The base class for the :ref:`components`"""
    proxy_class = GnrBaseProxy
    def __onmixin__(self, _mixinsource, site=None):
        js_requires = splitAndStrip(getattr(_mixinsource, 'js_requires', ''), ',')
        css_requires = splitAndStrip(getattr(_mixinsource, 'css_requires', ''), ',')
        py_requires = splitAndStrip(getattr(_mixinsource, 'py_requires', ''), ',')
        for css in css_requires:
            if css and not css in self.css_requires:
                self.css_requires.append(css)
        for js in js_requires:
            if js and not js in self.js_requires:
                self.js_requires.append(js)
                
        #self.css_requires.extend(css_requires)
        #self.js_requires.extend(js_requires)
        if py_requires:
            if site:
                site.page_pyrequires_mixin(self, py_requires)
            elif hasattr(self, '_pyrequiresMixin'):
                self._pyrequiresMixin(py_requires)
                
    @classmethod
    def __on_class_mixin__(cls, _mixintarget, **kwargs):
        js_requires = [x for x in splitAndStrip(getattr(cls, 'js_requires', ''), ',') if x]
        css_requires = [x for x in splitAndStrip(getattr(cls, 'css_requires', ''), ',') if x]
        namespace = getattr(cls, 'namespace', None)
        if namespace:
            if not hasattr(_mixintarget, 'struct_namespaces'):
                _mixintarget.struct_namespaces = set()
            _mixintarget.struct_namespaces.add(namespace)
        if css_requires and not hasattr(_mixintarget, 'css_requires'):
            _mixintarget.css_requires=[] 
        for css in css_requires:
            if css and not css in _mixintarget.css_requires:
                _mixintarget.css_requires.append(css)
        if js_requires and not hasattr(_mixintarget, 'js_requires'):
            _mixintarget.js_requires=[]
        for js in js_requires:
            if js and not js in _mixintarget.js_requires:
                _mixintarget.js_requires.append(js)
                
    @classmethod
    def __py_requires__(cls, target_class, **kwargs):
        from gnr.web.gnrwsgisite import currentSite
        
        loader = currentSite().resource_loader
        return loader.py_requires_iterator(cls, target_class)

class BagFieldForm(BaseComponent):
    pass


class BaseForm(BaseComponent):
    """BaseForm class is the one used to define any FormResource"""
    
    pass

class BaseView(BaseComponent):
    """BaseView class is the one used to define any ViewResource"""
    

    def th_struct(self, struct):
        """Hook method that defines the structure of the tablehandler's grid.
           At least one method starting with namespace "th_struct" must be implemented.
           It's possible to define more than one structure implementing callables starting
           with the namespace "th_struct". I.E. th_struct_large, th_struct_small
           
           :param struct: this is the struct where the grid columns will be defined
           
           The grid structure must be composed with at least:
           * one view
           * one row
           * one cell (cell, fieldcell, checkboxcolumn)

           **Example**
           r = struct.view().rows()
           r.fieldcell('name',width='10em')
           r.fieldcell('age',width='7em')
        """
        raise Exception('th_struct method should be overridden') #maybe we could use a more specific Exception class (NotImplementedException)

    def th_order(self):
        """Hook method that defines the columns of the tablehandler's grid
        """
        pass

    def th_options(self):
        """#DANILO: cosa ci devo mettere?"""
        pass


class BaseResource(GnrObject):
    """Base class for a webpage resource"""
    proxy_class = GnrBaseProxy
    def __init__(self, **kwargs):
        for k, v in list(kwargs.items()):
            if v:
                setattr(self, k, v)
                
class BaseProxy(object):
    """Base class for a webpage proxy"""
        
    def __init__(self, **kwargs):
        for argname, argvalue in list(kwargs.items()):
            setattr(self, argname, argvalue)
            
class BaseWebtool(object):
    """TODO"""
    pass
        
class GnrTableScriptHtmlSrc(GnrHtmlSrc):
    def cellFromField(self, field=None, width=0, 
                content_class=None,
             lbl=None, lbl_class=None, 
             lbl_height=None, 
             cell_border=None,
             border_width=None, 
             **kwargs):
        tableScriptInstance = self.root._parentWrapper.parent
        if field:
            colobj = tableScriptInstance.tblobj.column(field)
            content = tableScriptInstance.field(field)
            lbl = lbl or colobj.attributes.get('name_long')
        lbl = tableScriptInstance.localize(lbl)
        self.cell(content=content, width=width, 
                        content_class=content_class,
                        lbl=lbl, lbl_class=lbl_class, 
                        lbl_height=lbl_height, 
                        cell_border=cell_border,
                        border_width=border_width, 
                        **kwargs)


class TableScriptToHtml(BagToHtml):
    """TODO"""
    rows_table = None
    virtual_columns = None
    html_folder = 'temp:html'
    pdf_folder = 'page:pdf'
    cached = None
    css_requires = 'print_stylesheet'
    client_locale = False
    row_relation = None
    subtotal_caption_prefix = '!![en]Totals'


    def __init__(self, page=None, resource_table=None, parent=None, **kwargs):
        super(TableScriptToHtml, self).__init__(srcfactory=GnrTableScriptHtmlSrc,**kwargs)
        self.parent = parent
        self.page = page
        self.site = page.site
        self.db = page.db
        self.locale = self.page.locale if self.client_locale else self.site.server_locale
        self.tblobj = resource_table
        self.maintable = resource_table.fullname if resource_table else None
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.thermo_wrapper = self.page.btc.thermo_wrapper
        self.print_handler = self.page.getService('htmltopdf')
        self.pdf_handler = self.page.getService('pdf')
        self.letterhead_sourcedata = None
        self._gridStructures = {}
        self.record = None
        

    def __call__(self, record=None, pdf=None, downloadAs=None, thermo=None,record_idx=None, resultAs=None,
                    language=None,locale=None,**kwargs):
        if not record:
            return
        self.thermo_kwargs = thermo
        self.record_idx = record_idx
        if record=='*':
            record = None
        else:
            record = self.tblobj.recordAs(record, virtual_columns=self.virtual_columns)
        html_folder = self.getHtmlPath(autocreate=True)
        if locale:
            self.locale = locale #locale forced
        self.language = language    
        if self.language:
            self.language = self.language.lower()
            self.locale = locale or '{language}-{languageUPPER}'.format(language=self.language,
                                        languageUPPER=self.language.upper())
        elif self.locale:
            self.language = self.locale.split('-')[0].lower()
        result = super(TableScriptToHtml, self).__call__(record=record, folder=html_folder, **kwargs)
        if not result:
            return False
        if not pdf:
            return self.getHtmlUrl(os.path.basename(self.filepath)) if resultAs=='url' else result
        if not isinstance(result, list):
            self.writePdf(docname=self.getDocName())
        else:
            self.writePdf(filepath=result,docname=self.getDocName())
        if downloadAs:
            with open(self.pdfpath, 'rb') as f:
                result = f.read()
            return result            
        else:
            return self.getPdfUrl(os.path.basename(self.pdfpath)) if resultAs=='url' else self.pdfpath
            #with open(temp.name,'rb') as f:
            #    result=f.read()

    def getDocName(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]

    @extract_kwargs(pdf=True)
    def writePdf(self,filepath=None, pdfpath=None,docname=None,pdf_kwargs=None,**kwargs):
        self.pdfpath = pdfpath or self.getPdfPath('%s.pdf' % docname, autocreate=-1)
        pdf_kw = dict([(k[10:],getattr(self,k)) for k in dir(self) if k.startswith('htmltopdf_')])
        pdf_kw.update(pdf_kwargs)
        filepath = filepath or self.filepath
        if not isinstance(filepath,list):
            self.print_handler.htmlToPdf(filepath or self.filepath, self.pdfpath, orientation=self.orientation(), page_height=self.page_height, 
                                        page_width=self.page_width,pdf_kwargs=pdf_kw)
            return
        pdfToJoin = []
        for fp in filepath:
            curPdfPath = os.path.splitext(fp)[0]+'.pdf'
            pdfToJoin.append(curPdfPath)
            self.print_handler.htmlToPdf(fp, curPdfPath, orientation=self.orientation(), page_height=self.page_height, 
                                        page_width=self.page_width,pdf_kwargs=pdf_kw)
            os.remove(fp)
        self.pdf_handler.joinPdf(pdfToJoin,self.pdfpath)
        for pdf in pdfToJoin:
            os.remove(pdf)

    def get_css_requires(self):
        """TODO"""
        css_requires = []
        for css_require in self.css_requires.split(','):
            if not css_require.startswith('http'):
                css_requires.extend(self.page.getResourceExternalUriList(css_require,'css'))
            else:
                css_requires.append(css_require)
        return css_requires
        
    def get_record_caption(self, item, progress, maximum, **kwargs):
        """TODO
        
        :param item: TODO
        :param progress: TODO
        :param maximum: TODO"""
        if self.rows_table:
            tblobj = self.db.table(self.rows_table)
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item.value), progress, maximum)
        else:
            caption = '%i/%i' % (progress, maximum)
        return caption

    def gridColumnsInfo(self,gridname=None):
        if self.grid_columns:
            return dict(columns=self.grid_columns,columnsets=self.grid_columnsets)
        struct = self.getStruct(gridname=gridname)
        self.structAnalyze(struct)
        return dict(columns=self.gridColumnsFromStruct(struct=struct),
                    columnsets=self.gridColumnsetsFromStruct(struct))
    
    def gridColumnsetsFromStruct(self,struct):
        if not struct['info.columnsets']: 
            return dict()
        return dict([(l[0],l[1]) for l in struct['info.columnsets'].digest('#k,#a')])
    
    def setStruct(self,struct=None,gridname=None):
        gridname = gridname or '_main_'  
        self._gridStructures[gridname] = struct

    def getStruct(self,gridname=None):
        gridname = gridname or '_main_'
        struct = self._gridStructures.get(gridname)
        if struct is None:
            struct = self.page.newGridStruct(maintable=self.gridTable())
            self.gridStruct(struct)
            self._gridStructures[gridname] = struct
        return struct

    def gridStruct(self,struct):
        pass

    def structAnalyze(self,struct,grid_width=None,grid_border_width=None):
        layoutPars = self.mainLayoutParameters()
        gridPars = self.gridLayoutParameters()
        calcGridWidth =  self.copyWidth() - \
                        layoutPars.get('left',0)-layoutPars.get('right',0) -\
                        gridPars.get('left',0) - gridPars.get('right',0)
        grid_width = grid_width or gridPars.get('width') or calcGridWidth
        columns = struct['view_0.rows_0'].digest('#a')
        min_grid_width =  sum([(col.get('mm_width') or col.get('mm_min_width') or  15) for col in columns])
        extra_space = grid_width-min_grid_width
        if extra_space>=0:
            return
        head_col_total_width = sum([(col.get('mm_width') or col.get('mm_min_width') or  15) for col in columns if col.get('headColumn')]) 
        grid_free_width = grid_width-head_col_total_width
        net_min_grid_width = min_grid_width-head_col_total_width
        sheet_count = int(math.ceil(float(net_min_grid_width)/grid_free_width))
        sheet_delta = 0
        while sheet_delta<3 and not self._structAnalyze_step(columns,net_min_grid_width,sheet_count+sheet_delta,grid_width):
            sheet_delta+=1
        self.sheets_counter =(max([i or 0 for i in struct['view_0.rows_0'].digest('#a.sheet')]) or 0)+1
    
    def _structAnalyze_step(self,columns,net_min_grid_width,sheet_count,grid_width):
        sheet_space_available = grid_width-float(net_min_grid_width)/ sheet_count
        s = -1
        tw = 0
        max_ncol = len(columns)-1
        ncol = -1
        while ncol<max_ncol:
            ncol+=1
            col = columns[ncol]
            if  col.get('headColumn'):
                continue
            columnset = col.get('columnset')
            k = ncol
            mm_width = 0
            grouped_cols = []
            nextcol = True
            while nextcol:
                col = columns[k]
                grouped_cols.append(col)
                mm_width += col['mm_width']
                if not columnset:
                    nextcol = False
                else:
                    k+=1
                    if k>max_ncol or columns[k].get('columnset')!=columnset:
                        nextcol = False
                        k-=1
            colonne = ','.join([c['name'] for c in grouped_cols])
            dd = dict(numero=ncol,titolo=columns[ncol]['name'],colset=columnset,mm_width=mm_width,colonne=colonne)
            #print (dd)
            ncol = k
            tw -= mm_width
            if tw<=0:
                tw += sheet_space_available
                s += 1
                if s>=sheet_count:
                    return False
            for c in grouped_cols:
                c['sheet'] = s
        return True
    
    def structFromResource(self,viewResource=None,table=None):
        table = table or self.rows_table or self.tblobj.fullname
        if not ':' in viewResource:
            viewResource = 'th_%s:%s' %(table.split('.')[1],viewResource)
        view = self.site.virtualPage(table=table,table_resources=viewResource)
        structbag = view.newGridStruct(maintable=table)
        view.th_struct(structbag)
        return structbag
    
    def gridColumnsFromStruct(self,struct=None):
        grid_columns = []
        cells = struct['view_0.rows_0'].nodes
        for n in cells:
            attr = n.attr
            field =  attr.get('caption_field') or attr.get('field')
            field_getter = attr.get('field_getter') or field
            if isinstance(field_getter,basestring):
                field_getter = self._flattenField(field_getter)
            group_aggr = attr.get('group_aggr')
            if group_aggr:
                field_getter = '%s_%s' %(field_getter,group_aggr)
            content_class = attr.get('cellClasses') or attr.get('content_class')
            lbl_class = attr.get('headerClasses') or attr.get('lbl_class')
            extra_kw = dictExtract(attr,'colextra_*')
            mm_width = attr.get('mm_width') 
            hidden = attr.get('hidden')
            if mm_width==-1: #shared structure visible in grid not in print
                mm_width = None
                hidden = True
            pars = dict(field=field,name=self.localize(attr.get('name')),field_getter=field_getter,
                        align_class=attr.get('align_class'), mm_width=mm_width,format=attr.get('format'),
                        white_space=attr.get('white_space','nowrap'),
                        subtotal=attr.get('subtotal'),
                        subtotal_order_by=attr.get('subtotal_order_by'),
                        style=attr.get('style'), content_class = content_class, lbl_class=lbl_class,
                        sqlcolumn=attr.get('sqlcolumn'),dtype=attr.get('dtype'),
                        columnset=attr.get('columnset'),sheet=attr.get('sheet','*'),
                        totalize=attr.get('totalize'),formula=attr.get('formula'),
                        background=attr.get('background'),color=attr.get('color'),
                        hidden=hidden,**extra_kw)
            if self.row_table:
                self._calcSqlColumn(pars)
            grid_columns.append(pars)
        return grid_columns

    def _calcSqlColumn(self,col):
        sqlcolumn = col.get('sqlcolumn')
        if sqlcolumn:
            return
        field = col['field']
        if field.startswith('@'):
            col['sqlcolumn'] = col['field']
        else:
            columnobj = self.db.table(self.row_table).column(field)
            if columnobj is not None:
                col['sqlcolumn'] = '${}'.format(field)
        if field!=col['field_getter']:
             col['sqlcolumn'] = '{} AS {}'.format(col['sqlcolumn'],col['field_getter'])
    
    def localize(self, value,language=None):
        return self.page.localize(value,language = language or self.language)

    def gridQueryParameters(self):
        #override
        return dict()
    
    def sortLines(self, lines):
        if self.grid_subtotal_order_by:
            return lines
        return super(TableScriptToHtml, self).sortLines(lines)


    def gridTable(self):
        if self.row_table:
            return self.row_table
        parameters = self.gridQueryParameters()
        if not parameters:
            return None
        self.row_table = parameters.get('table') or self._expandRowRelation(parameters['relation'])['table']
        return self.row_table

    def _expandRowRelation(self,relation):
        relation_attr = self.tblobj.model.relations.getAttr(relation, 'joiner')
        many = relation_attr['many_relation'].split('.')
        fkey = many.pop()
        return dict(table=str('.'.join(many)),condition='$%s=:_fkey' %fkey,condition__fkey=self.record[self.tblobj.pkey])


    def currentSelectionQueryParameters(self):
        rowtable_obj = self.db.table(self.row_table)
        return dict(condition='${pkey} IN :selectionPkeys'.format(pkey=rowtable_obj.pkey),
                    condition_selectionPkeys=self.record['selectionPkeys'])
    
    def gridData(self):
        #overridable
        self.row_mode = 'attribute'
        parameters = dict(self.gridQueryParameters())
        if self.record['selectionPkeys'] and (not parameters or self.parameter('use_current_selection')):
            parameters = self.currentSelectionQueryParameters()
        if not parameters:
            raise Exception('You must define gridQueryParameters or gridData or use_current_selection')
        condition_kwargs = dictExtract(parameters,'condition_',pop=True)
        parameters.update(condition_kwargs)
        condition = parameters.pop('condition',None)
        row_table = self.gridTable()
        relation = parameters.pop('relation',None)
        where = []
        if relation:
            relkw = self._expandRowRelation(relation)
            self.row_table = relkw.pop('table')
            where.append(relkw.pop('condition'))
            parameters.update(dictExtract(relkw,'condition_'))
        if condition:
            where.append(condition)
        columns = self.grid_sqlcolumns
        hidden_columns = parameters.get('hidden_columns')
        if hidden_columns:
            columns = '%s,%s' %(hidden_columns,columns)
        rowtblobj = self.db.table(self.row_table)
        if self.grid_subtotal_order_by:
            parameters['order_by'] = self.grid_subtotal_order_by
        sel = rowtblobj.query(columns=columns,where= ' AND '.join(where),**parameters
                                ).selection(_aggregateRows=True)


        if not parameters.get('order_by') and self.record['selectionPkeys']: #same case of line 493
            sel.data.sort(key = lambda r : self.record['selectionPkeys'].index(r['pkey']))
        return sel.output('grid',recordResolver=False)


    @property
    def grid_sqlcolumns(self):
        return ','.join(set([c['sqlcolumn'] for c in self.gridColumnsInfo()['columns'] if c.get('sqlcolumn')]))

    @property
    def grid_subtotal_order_by(self):
        return ','.join(set([c['subtotal_order_by'] for c in self.gridColumnsInfo()['columns'] if c.get('subtotal_order_by')]))
         
        
        
    def getHtmlPath(self, *args, **kwargs):
        """TODO"""
        return self.site.storageNode(self.html_folder, *args, **kwargs).internal_path
        
    def getPdfPath(self, *args, **kwargs):
        """TODO"""
        return self.site.storageNode(self.pdf_folder, *args, **kwargs).internal_path
        
    def getHtmlUrl(self, *args, **kwargs):
        """TODO"""
        return self.site.storageNode(self.html_folder, *args).url(**kwargs)
        
    def getPdfUrl(self, *args, **kwargs):
        """TODO"""
        return self.site.storageNode(self.pdf_folder, *args).url(**kwargs)
        
    def outputDocName(self, ext=''):
        """TODO
        :param ext: TODO"""
        if ext and not ext[0] == '.':
            ext = '.%s' % ext
        caption = ''
        if self.record is not None:
            caption = slugify(self.tblobj.recordCaption(self.record))
            idx = self.record_idx
            if idx is not None:
                caption = '%s_%i' %(caption,idx)
        doc_name = '%s_%s%s' % (self.tblobj.name, caption, ext)
        return doc_name

class TableTemplateToHtml(BagToHtml):
    def __init__(self, table=None,letterhead_sourcedata=None, **kwargs):
        super(TableTemplateToHtml, self).__init__(**kwargs)
        self.db = table.db
        self.site = self.db.application.site
        self.tblobj = table
        self.maintable = table.fullname
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.letterhead_sourcedata = letterhead_sourcedata
        self.print_handler = self.site.getService('htmltopdf')
        self.pdf_handler = self.site.getService('pdf')
        self.record = None

    def __call__(self,record=None,template=None, htmlContent=None, locale=None,**kwargs):
        if not htmlContent:
            htmlContent = self.contentFromTemplate(record,template,locale=locale)
            record = self.record
        return super(TableTemplateToHtml, self).__call__(record=record,htmlContent=htmlContent,**kwargs)

    def contentFromTemplate(self,record,template,locale=None,**kwargs):
        virtual_columns=None
        if isinstance(template,Bag):
            kwargs['locale'] = locale or template.getItem('main?locale')
            kwargs['masks'] = template.getItem('main?masks')
            kwargs['formats'] = template.getItem('main?formats')
            kwargs['df_templates'] = template.getItem('main?df_templates')
            kwargs['dtypes'] = template.getItem('main?dtypes')
            virtual_columns = template.getItem('main?virtual_columns')
        self.record = self.tblobj.recordAs(record,virtual_columns=virtual_columns)
        return templateReplace(template,self.record, safeMode=True,noneIsBlank=False,
                    localizer=self.db.application.localizer,urlformatter=self.site.externalUrl,
                    **kwargs)

    @extract_kwargs(pdf=True)
    def writePdf(self,pdfpath=None,docname=None,pdf_kwargs=None,**kwargs):
        pdfpath = pdfpath or self.filepath.replace('.html','.pdf')
        self.print_handler.htmlToPdf(self.filepath,pdfpath, orientation=self.orientation(),pdf_kwargs=pdf_kwargs)
        return pdfpath

        

