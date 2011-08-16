.. _macro:

============
Genro macros
============
    
    *Last page update*: |today|
    
    We list here the four Genro macro: these operations can be specified in the javascript events associated with an interface, and the framework deals gnrjs to the expansion of these macros. It can be accessed from its datastore javascript code (ie from code written in .JS file and then read without macro-expansion) using simple javascript functions.

.. _set:

SET
===

    State a value and triggers any associated events (ie any observers or resolver connected by "^").
    
    **Example**: ``SET goofy='aaa'`` is a shortcut for the following command::
    
        this.setRelativeData("goofy",aaa);
        
.. _put:

PUT
===
    
    Set a value, but does not trigger the events associated.
    
.. _get:
    
GET
===

    Read the contents of a value in the :ref:`datastore`
    
    **Example**: ``GET goofy`` is a shortcut for the following command::
    
        this.getRelativeData("goofy");
        
.. _fire:

FIRE
====

    Set a value in the ``datastore``, and then trigger the events associated. After that reset the
    value to zero (without triggering events [#]_). It is used when you need to trigger events through
    a temporary parameter to the Observers (add???).
    
    **Example**: ``FIRE goofy='aaa'`` is a shortcut for the following commands::
    
        this.setRelativeData("goofy",aaa)
        this.setRelativeData("goofy",null)
        
**Footnotes:**

.. [#] In this way the trigger can be used more than once time.