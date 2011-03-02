.. _genro_macro:

============
Genro macros
============

    We list here the four Genro macro: these operations can be specified in the javascript events associated with an interface, and the framework deals gnrjs to the expansion of these macros. It can be accessed from its datastore javascript code (ie from code written in .JS file and then read without macro-expansion) using simple javascript functions.

.. _genro_set:

SET
===

    state a value and triggers any associated events (ie any observers or resolver connected by "^")
    
.. _genro_put:

PUT
===
    
    set a value, but does not trigger the events associated
    
.. _genro_get:
    
GET
===

    read the contents of a value in the datastore

.. _genro_fire:

FIRE
====

    set a value in the datastore, and then trigger the events associated. After that reset the value to zero (without triggering events [#]_). It is used when you need to trigger events through a temporary parameter to the Observers.
	
**Footnotes:**

.. [#] In this way the trigger can be used more than once time.