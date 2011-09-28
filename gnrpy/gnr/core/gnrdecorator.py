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

import warnings
from gnr.core.gnrdict import dictExtract


def metadata(**kwargs):
    """add???"""
    def decore(func):
        prefix = kwargs.pop('prefix',None)
        for k, v in kwargs.items():
            setattr(func, '%s_%s' %(prefix,k) if prefix else k, v)
        return func
        
    return decore
    
def public_method(func):
    """A decorator. It can be used to mark methods/functions as :ref:`datarpc`\s
    
    :param func: the function to set as public method"""
    func.is_rpc = True
    return func
    
def extract_kwargs(_adapter=None,_dictkwargs=None,**extract_kwargs):
    """A decorator. Allow to extract some **kwargs creating some kwargs sub-families
    
    :param _adapter: the adapter names for extracted attributes (prefixes for sub-families)
                     every adapter name defines a single extract kwargs sub-family
    :param _dictkwargs: a dict with the extracted kwargs
    :param \*\*extract_kwargs: others kwargs
    
    In the "extract_kwargs" definition line you have to follow this syntax::
    
        @extract_kwargs(adapterName=True)
        
    where:
    
    * ``adapterName`` is one or more prefixes that identify the kwargs sub-families
    
    In the method definition the method's attributes syntax is::
    
        adapterName_kwargs
        
    where:
    
    * ``adapterName`` is the name of the ``_adapter`` parameter you choose
    * ``_kwargs`` is a mandatory string
    
    When you call the decorated method, to specify the extracted kwargs you have to use the following syntax::
    
        methodName(adapterName_attributeName=value,adapterName_otherAttributeName=otherValue,...)
        
    where:
    
    * ``adapterName`` is the name of the ``_adapter`` parameter you choose
    * ``attributeName`` is the name of the attribute extracted
    * ``value`` is the value of the attribute
    
    **Example:**
    
        Let's define a method called ``my_method``::
        
            @extract_kwargs(palette=True,dialog=True,default=True)                    # in this line we define three families of kwargs,
                                                                                      #     indentified by the prefixes:
                                                                                      #     "palette", "dialog", "default"
            def my_method(self,pane,table=None,                                       # "standard" parameters
                          palette_kwargs=None,dialog_kwargs=None,default_kwargs=None, # extracted parameters from kwargs
                          **kwargs):                                                  # other kwargs
                          
        Now, if you call the ``my_method`` method you will have to use::
        
            pane.another_method(palette_height='200px',palette_width='300px',dialog_height='250px')
            
        where "pane" is a :ref:`contentPane` to which you have attached your method"""
    if _dictkwargs:
        extract_kwargs = _dictkwargs
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
        newFunc.__doc__=func.__doc__
        return newFunc
    return decore

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used

    :param func: the function to deprecate"""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc