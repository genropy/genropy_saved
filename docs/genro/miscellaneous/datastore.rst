.. _datastore:

=========
datastore
=========
    
    *Last page update*: |today|
    
    * :ref:`datastore_description`
    * :ref:`datastore_syntax`
    * :ref:`datastore_access`
    * :ref:`datastore_debugger`

.. _datastore_description:

description
===========
    
    The datastore is a Genro :ref:`bag` used to keep track of data

.. _datastore_syntax:

datastore syntax
================
    
    The path followed by the syntax in the datastore:
    
    * ``path`` --> absolute path in datastore
    * ``.path`` --> relative path in datastore
    * ``#ID`` --> path relative to the ID
    
    The path indicates the access path to data to every element of the datastore (it is implemented by
    reading the Bag interface, and thus includes many things: for example, you can also specify the CSS
    classes of an HTML element linking them to an element of the datastore), using the prefixes:

    * "^" (circumflex accent): ``^access.to.resolver``, setting an observer at this node. The component
      will be informed of changes to the datastore
    * equal: ``=accessed.from.resolver``, reads the datastore content.
    
    For more information on absolute and relative paths, check the :ref:`datapath` page.

.. _datastore_access:

javascript datastore access
===========================

    The possible operations on the datastore include some :ref:`macro` (like :ref:`set` and :ref:`get`)
    
    They can be specified in the javascript events associated with an interface, and the framework
    deals gnrjs to the expansion of these macros
    
.. _datastore_debugger:

inspector
=========

    We call "inspector" the graphic interface of the :ref:`datastore`.
    
    You can access it directly from your browser when you are in a :ref:`webpage`
    by clicking ``ctrl+shift+D``:
    
        *The inspector*
        
        .. image:: ../_images/datastore.png
        