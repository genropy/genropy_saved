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

Description
===========
    
    The datastore is a Genro :ref:`bag_intro` used to keep track of data.

.. _datastore_syntax:

Datastore syntax
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

Access to the datastore from javascript
=======================================

    The possible operations on the datastore include some macros, that are:
    
    * :ref:`set`
    * :ref:`put`
    * :ref:`get`
    * :ref:`fire`
    
    They can be specified in the javascript events associated with an interface, and the framework deals
    gnrjs to the expansion of these macros. Check the :ref:`macro` page for further details.

.. _datastore_debugger:

inspector
=========

    You can access to its graphic interface from any Genro webpage by clicking ``ctrl+shift+D`` [#]_:
    
    .. image:: ../_images/datastore.png

**Footnotes**

.. [#] For Mac and Windows users. For Linux users, click ... ???