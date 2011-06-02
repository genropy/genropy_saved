.. _genro_decorators:

==========
decorators
==========

    We describe here all the Python decorators you can find in Genro. They are:
    
    * the :ref:`deprecated` decorator
    * the :ref:`extract_kwargs` decorator
    * the :ref:`property` decorator
    * the :ref:`public_method` decorator
    * the :ref:`struct_method` decorator
    
.. _deprecated:
    
@deprecated
===========
    
    add???
    
.. _extract_kwargs:

@extract_kwargs
===============

    add???
    
.. _property:

@property
=========

    add???
    
.. _public_method:

@public_method
==============

    add???
    
.. _struct_method:

@struct_method
==============

    add???
    
    **doc draft**:
    
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