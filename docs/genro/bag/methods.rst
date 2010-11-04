	.. _bag-methods:

Bag methods
===========

.. ??? Take doc from gnrbag.py !

.. class:: Bag

	.. note:: The square brackets around some parameters in the following method signature denote that the parameter is optional, not that you should type square brackets at that position. You will see this notation frequently in the Genro Library Reference.

	.. method:: addItem(label,value)

		Used to add different values with the same label. For more information, check the :ref:`bag-duplicated` paragraph.
	
	.. method:: asDict()
	
		Allow to transform a ``Bag`` in a ``dict``.
		
		.. note:: If you attempt to transform a hierarchical bag to a dictionary, the resulting dictionary will contain nested bags as values. In other words only the first level of the Bag is transformed to a dictionary, the transformation is not recursive.

	.. method:: asString()
	
		Allow to transform a ``Bag`` in a ``string``.
		
		The ``Bag`` ``__repr__(self)`` is the asString() method.
	
	.. method:: getItem(path)

		Return the value if it is in the ``Bag``, else it returns ``None``, so that this method never raises a ``KeyError``.

	.. method:: has_key('key')

		Test for the presence of key in the ``Bag``.

	.. method:: items()

		Return a copy of the Bag as a list of tuples (``key, value`` pairs)
		
		>>> b = Bag({'a':1,'b':2,'c':3})
		>>> b.items()
		[('a', 1), ('c', 3), ('b', 2)]

	.. method:: keys()

		Return a copy of the Bag as a list of keys
		
		>>> b = Bag({'a':1,'a':2,'a':3})
		>>> b.keys()
		['a', 'c', 'b']

	.. method:: pop(path)
	
		Remove the first value included in the path, and return it.
		
		>>> b = Bag()
		>>> b.setItem('a',1)
		>>> b.addItem('a',2)
		>>> b.addItem('a',3)
		>>> b.pop('a')
		1
		>>> print b
		0 - (int) a: 2
		1 - (int) a: 3

	.. method:: setItem(path,value[,_position='expression'])

		??? It is possible to set a new value at a particular position among its brothers, using the optional argument ``_position`` of the :meth:`Bag.setItem` method. The default behaviour of setItem is to add the new item as the last element of a list, but the _position argument provides a compact syntax to insert any item at it's desired place. _position must be a string of the following types:
		
		+----------------------------+----------------------------------------------------------------------+
		| *expression* for _position |  Description                                                         |
		+============================+======================================================================+
		| ``<``                      | Set the value as the first value of the Bag                          |
		+----------------------------+----------------------------------------------------------------------+
		| ``>``                      | Set the value as the last value of the Bag                           |
		+----------------------------+----------------------------------------------------------------------+
		| ``<label``                 | Set the value in the previous position respect to the labelled one   |
		+----------------------------+----------------------------------------------------------------------+
		| ``>label``                 | Set the value in the position next to the labelled one               |
		+----------------------------+----------------------------------------------------------------------+
		| ``<#index``                | Set the value in the previous position respect to the indexed one    |
		+----------------------------+----------------------------------------------------------------------+
		| ``>#index``                | Set the value in the position next to the indexed one                |
		+----------------------------+----------------------------------------------------------------------+
		| ``#index``                 | Set the value in a determined position indicated by ``index`` number |
		+----------------------------+----------------------------------------------------------------------+
		
		Check an example in the :ref:`bag_setting_value_position` section.
		
	.. method:: update(other)

		Update the ``Bag`` with the ``key/value`` pairs from *other*, overwriting existing keys. Return ``None``.

	.. method:: values()

		Return a copy of the Bag values as a list.

