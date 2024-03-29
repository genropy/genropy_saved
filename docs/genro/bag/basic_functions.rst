.. _bag_one:

===============
Basic functions
===============

    *Last page update*: |today|
    
    * :ref:`bag_instance`
    * :ref:`bag_set_get`
    * :ref:`bag_printing`
    * :ref:`bag_lists_dictionaries`
    * :ref:`bag_duplicated`
    * :ref:`bag_access_to_value`
    * :ref:`bag_setting_value_position`
    * :ref:`bag_dictionary_methods`
    
.. _bag_instance:

How to instantiate a Bag
========================

    To instantiate a Bag you have to call its constructor:
    
        >>> from gnr.core.gnrbag import Bag
        
    You can now instantiate an empty Bag:
        
        >>> mybag = Bag()
    
    The constructor may receive several kinds of initialization parameters; you can create a Bag:
    
    * starting from XML files, URL or file-system paths:
        
        >>> mybag = Bag('/data/myfile.xml')
        >>> mybag = Bag('http://www.foo.com')
    
    * parsing a text string
    * converting a dictionary into a Bag 
    * passing a list or a tuple just like for the builtin ``dict()`` command
    * using the instructions from the :meth:`gnr.core.gnrbag` module; in this case the code is
      similar to the construction of a dictionary (TODO)
    * using the :meth:`gnr.core.gnrstructures` module; in this case, the code consists of a set of
      python method calls. This subsequently supports the definition of the database model,
      in addition to the construction of webpages.
    
    For more information, check the :ref:`bag_from_to` section.
    
.. _bag_set_get:

Set and get values from a Bag
=============================

    You can read from a Bag's value using the :meth:`~gnr.core.gnrbag.Bag.getItem` method;
    to write on a Bag, you can use the :meth:`~gnr.core.gnrbag.Bag.setItem` method.
    
        >>> mybag = Bag()
        >>> mybag.setItem('a',1)
        >>> mybag.setItem('b',2)
        >>> first= mybag.getItem('a')
    
    Now the Bag will look like this:
    
        >>> print mybag
        0 - (int) a: 1
        1 - (int) b: 2
        
    .. note:: Any value inserted into a Bag through the :meth:`~gnr.core.gnrbag.Bag.setItem`
              method is inserted as the last element of a chain: every BagNode has its own position
              at the appropriate hierarchical level

    You can write on a Bag through a more compact notation:
    
        >>> mybag['b']=2
        >>> print mybag
        0 - (int) a: 1
        1 - (int) b: 2
    
    You can even read some values through the square-brackets notation:
        
        >>> second = mybag['b']
        >>> print second
        2
        
    You can use Bag as a hierarchical container, so you can create nested Bag with complex path:
    check :ref:`bag_path` section for more explanation.
    
    For advanced information, check the :ref:`bag_getting_values_advanced` section.

.. _bag_printing:

Printing a Bag
==============

    If you want to display a bag in your python shell you can use the built-in function ``print``:
    
    >>> print mybag
    0 - (int) a: 1
    1 - (int) b: 2
    
    We don't introduced the :ref:`bag_attributes` yet; however, if you print a Bag with attributes,
    you will get them included between angle brackets and separated by a single space, like::
    
        <createdOn='11-10-2010' createdBy='Niso'>.
    
    Bag representation makes a line for each value. The line is structured in the following way::
    
        numericIndex - (type) label: value <firstAttributeName='firstAttributeValue' secondAttributeName='secondAttributeValue' >
    
    Check the :ref:`bag_attributes_setItem` section for a complete example on printing a Bag with attributes.
    
    You have to know that when you use the built-in function ``print`` you call the
    :meth:`~gnr.core.gnrbag.Bag.asString` method:
    
        >>> mybag = Bag({'a':1,'b':2,'c':3,'d':4})
        >>> string = mybag.asString()
        >>> string
        '0 - (int) a: 1  \n1 - (int) c: 3  \n2 - (int) b: 2  \n3 - (int) d: 4  '
    
    For advanced information, check the :ref:`bag_printing_advanced` section.

.. _bag_lists_dictionaries:

Flat bags VS lists and dictionaries
===================================

    There are several analogies between a Bag's label and dictionary key; there are also some fundamental differences:
    
    * a Bag's label must be a string: numbers or complex types are not valid labels.
    * In ``dictionaries``, keys must be unique; in a Bag you can have different values tagged with the same label.
    
.. _bag_duplicated:

Duplicated labels
=================

    Let's check this example, in which we suppose that you want to insert some values with THE SAME label;
    if you follow this way:
    
        >>> beatles = Bag()
        >>> beatles.setItem('member','John')
        >>> beatles.setItem('member','Paul')
        >>> beatles.setItem('member','George')
        >>> beatles.setItem('member','Ringo')
        
    And check your Bag:
    
        >>> print beatles
        0 - (str) member: Ringo
        
    you will notice that with :meth:`~gnr.core.gnrbag.Bag.setItem` method you would set the
    new values on the existing one.
    
    So, if you want to add different values with the same label you have to use the
    :meth:`~gnr.core.gnrbag.Bag.addItem` method:
        
        >>> beatles = Bag()
        >>> beatles.setItem('member','John')    # alternatively, you could write beatles.addItem('member','John')
        >>> beatles.addItem('member','Paul')
        >>> beatles.addItem('member','George') 
        >>> beatles.addItem('member','Ringo')
        >>> print beatles
        0 - (str) member: John
        1 - (str) member: Paul
        2 - (str) member: George
        3 - (str) member: Ringo

.. _bag_access_to_value:

Access to values: the "#" label
===============================

    A Bag is an ordered container: it remembers the order of its children insertion [#]_ and allows the
    Bag to get its values with a numeric index representing an element's position. So, if you want to
    access data by its position, you have to use a particular label composed by ``#`` followed by the
    value's index:

        >>> first = beatles.getItem('#0')
        >>> print first
        John
        >>> second = beatles['#1']
        >>> print second
        Paul

    This feature is very useful when a Bag has several values with the same label, because the
    :meth:`~gnr.core.gnrbag.Bag.getItem` method returns only the first value tagged with the
    argument label. This means that the only way to access values with a duplicated label is by index:

        >>> print beatles.getItem('member')
        John
        >>> print beatles.getItem('#0') # obviously, with '#0' you will get the same value
        John
        >>> print beatles.getItem('#1')
        Paul
        >>> print beatles.getItem('#2')
        George
        >>> print beatles.getItem('#3')
        Ringo

.. _bag_setting_value_position:

Setting value's position
========================

    It is possible to set a new value at a particular position among its brothers, using the optional
    argument ``_position`` of the :meth:`~gnr.core.gnrbag.Bag.setItem` method. The default
    behavior of setItem is to add the new value as the last element of a list, but the ``_position``
    argument provides a compact syntax to insert any value in any place you want. ``_position`` must
    be a string containing one of the following types:
    
    +---------------+----------------------------------------------------------------------+
    |  Attribute    |  Description                                                         |
    +===============+======================================================================+
    | ``'<'``       | Set the value as the first value of the Bag                          |
    +---------------+----------------------------------------------------------------------+
    | ``'>'``       | Set the value as the last value of the Bag                           |
    +---------------+----------------------------------------------------------------------+
    | ``'<label'``  | Set the value in the previous position respect to the labelled one   |
    +---------------+----------------------------------------------------------------------+
    | ``'>label'``  | Set the value in the position next to the labelled one               |
    +---------------+----------------------------------------------------------------------+
    | ``'<#index'`` | Set the value in the previous position respect to the indexed one    |
    +---------------+----------------------------------------------------------------------+
    | ``'>#index'`` | Set the value in the position next to the indexed one                |
    +---------------+----------------------------------------------------------------------+
    | ``'#index'``  | Set the value in a determined position indicated by ``index`` number |
    +---------------+----------------------------------------------------------------------+
    
    Example:
    
        >>> mybag = Bag()
        >>> mybag['a'] = 1
        >>> mybag['b'] = 2
        >>> mybag['c'] = 3
        >>> mybag['d'] = 4
    
    The Bag will look like this:
    
        >>> print mybag
        0 - a: 1
        1 - b: 2
        2 - c: 3
        3 - d: 4
    
    We introduce now some of the ``_position`` properties:
        
        >>> mybag.setItem('e',5, _position= '<')
        >>> mybag.setItem('f',6, _position= '<c')
        >>> mybag.setItem('g',7, _position= '<#3')
        
    Now the Bag looks like this:
        
        >>> print mybag
        0 - (int) e: 5
        1 - (int) a: 1
        2 - (int) b: 2
        3 - (int) g: 7
        4 - (int) f: 6
        5 - (int) c: 3
        6 - (int) d: 4

.. _bag_dictionary_methods:

Dictionary methods implemented by Bag and other related methods
===============================================================

    We report here a list of the Bag methods inherited from a Python Dictionary:
    
    * :meth:`~gnr.core.gnrbag.Bag.keys`
    * :meth:`~gnr.core.gnrbag.Bag.items`
    * :meth:`~gnr.core.gnrbag.Bag.values`
    * :meth:`~gnr.core.gnrbag.Bag.has_key`
    * :meth:`~gnr.core.gnrbag.Bag.update`
    
    * Bag also supports the operator ``in`` exactly like a dictionary:
    
        >>> mybag = Bag()
        >>> mybag.setItem('a',1)
        >>> 'a' in mybag
        True
        
    * Finally, you can transform a Bag into a dict with the :meth:`~gnr.core.gnrbag.Bag.asDict`
      method: check the :ref:`from_bag_to_dict` section for further details.

**Footnotes:**

.. [#] Like a Python ``list``.
