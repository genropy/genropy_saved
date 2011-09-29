.. _decorators:

==========
decorators
==========
    
    *Last page update*: |today|
    
    We describe here all the Python decorators you can find in Genro. They are:
    
    * the :ref:`deprecated` decorator
    * the :ref:`extract_kwargs` decorator
    * the :ref:`public_method` decorator
    * the :ref:`struct_method` decorator
    
.. _deprecated:
    
@deprecated
===========

    .. method:: gnr.core.gnrdecorator.deprecated(func)
    
        This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used
        
        **Parameters: func** - the function to deprecate
    
    To use it, import in your file::
    
        from gnr.core.gnrdecorator import deprecated
    
.. _extract_kwargs:

@extract_kwargs
===============

    .. method:: gnr.core.gnrdecorator.extract_kwargs(_adapter=None,_dictkwargs=None,**extract_kwargs)
    
        A decorator. Allow to extract some **kwargs creating some kwargs sub-families

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

            where "pane" is a :ref:`contentPane` to which you have attached your method
                        
    To use it, import in your file::
    
        from gnr.core.gnrdecorator import extract_kwargs
    
.. _public_method:

@public_method
==============

    .. method:: gnr.core.gnrdecorator.public_method(func)
    
        A decorator. It can be used to mark methods/functions as :ref:`datarpc`\s
        
        **Parameters: func** - the function to set as public method
        
    To use it, import in your file::
    
        from gnr.core.gnrdecorator import public_method
    
.. _struct_method:

@struct_method
==============

    .. method:: gnr.web.gnrwebstruct.struct_method(func_or_name)
    
        A decorator. Allow to register a new method (in a page or in a component)
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
                bc.bar(...)
        
    To use it, import in your file::
    
        from gnr.web.gnrwebstruct import struct_method
            