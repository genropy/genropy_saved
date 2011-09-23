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
    
        A decorator. add???
        
        **Parameters**:
        
                        * **_adapter** - add???
                        * **_dictkwargs** - add???
                        * **extract_kwargs** - add???
                        
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
            