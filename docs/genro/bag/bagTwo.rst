	.. _genro-bag-two:

============================
 Basic functions (part two)
============================

	- :ref:`bag-hierarchical`
	
	- :ref:`bag-path`
	
	- :ref:`bag_setting_hierchical`
	
	- :ref:`bag-printing-advanced`
	
	- :ref:`bag_getting_values_advanced`
	
	- :ref:`bag_digest`

	.. _bag-hierarchical:

Bag as a hierarchical container
===============================

	We can define every Bag as a hierarchical Bag. In the introduction to a Bag [#]_ we saw how a Bag works *in breadth*. Now we'll see how they can be used to store data *in depth*.

	Bags aren't just another traversable tree structure. Infact a Bag supports a direct access to any value contained in any of its nested bags, using a complex path. So every Bag contains all the information to get every other value in every other related "Hierarchical Bag".

	.. _bag-path:

Bag's path
==========

	We define "path" as a concatenation of nested bag labels ending with the innermost value's label. The separator character of a path is the "." char [#]_. Let's check out this example:

		>>> new_card= Bag()
	
	We instantiate a Bag called "new_card" setting three values labelled "name", "surname" and "phone":
		
		>>> new_card['name']='John' # Here we use the square-brackets notation for a value insertion
		>>> new_card.setItem('surname','Doe') # Here we use the setItem notation for a value insertion
		
	"phone" contains a Bag filled with three new values, labelled "office", "home" and "mobile":
		
		>>> new_card['phone']= Bag()
		>>> new_card['phone'].setItem('office',555450210)
		>>> new_card.setItem('phone.home',555345670)
		>>> new_card.setItem('phone.mobile', 555230450)
	
	A hierarchical bag ("new_card") can be nested within a larger one ("address_book"). In the following line we set the "new_card" Bag into the  "friends" Bag that is included into the "address_book" Bag.
	
	Now you might be thinking that the "friends" Bag was not instantiated and that it wasn't set into the "address_book". But, when :meth:`Bag.setItem` method receives a path, creates every Bag included in the path, even if you haven't create them:

		>>> address_book=Bag()
	
	With the following line we insert all the previous stuff in the "friends.johnny" path:
	
		>>> address_book.setItem('friends.johnny',new_card)
	
	If we want to take Johnny's mobile we have to call the :meth:`Bag.getItem` method on the ``friends.johnny.phone.mobile`` path:
	
		>>> john_mobile= address_book.getItem('friends.johnny.phone.mobile')
		>>> print john_mobile
		555230450

	This feature is very useful to quickly create many nested bags with just a single command:
    
		>>> mybag=Bag()
		>>> mybag.setItem('a.b.c.d.e.f.g', 7)
		>>> print mybag['a.b.c.d.e.f.g']
		7
		>>> print mybag
		0 - (Bag) a:
		    0 - (Bag) b:
		        0 - (Bag) c:
		            0 - (Bag) d:
		                0 - (Bag) e:
		                    0 - (Bag) f:
		                        0 - (int) g: 7

.. _bag_setting_hierchical:

Setting item on a hierarchical Bag
==================================

	In the previous examples we saw two equivalent ways to create a nested value; we report them here with the same label and value, so in these following lines we report two different ways to create the same nested Bag path::
	
		new_card['phone'].setItem('office',555450210)
		new_card.setItem('phone.office',555450210)

	So you can create a nested path with the square-brackets syntax or with the :meth:`Bag.setItem` method, just remember that every folder of Bag path is introduced by a dot (``.``).

	.. _bag-printing-advanced:

Printing Bag (advanced)
=======================

	``print`` function displays nested bags with indented blocks:

		>>> print address_book
		0 - (Bag) friends:
		    0 - (Bag) johnny:
		        0 - (str) name: John
		        1 - (str) surname: Doe
		        2 - (Bag) phone:
		            0 - (int) office: 555450210
		            1 - (int) home: 555345670
		            2 - (int) mobile: 555230450

.. _bag_getting_values_advanced:

Getting Values (advanced)
=========================

	We can access to a value using a label made by ``#`` followed by a numeric ``index``. A Bag can be traversed using a path that includes either common labels or a numeric label.

		>>> print address_book['friends.johnny.#2.office']
		555450210
		
	Or, with the :meth:`Bag.getItem` method:
		
		>>> officenumber = address_book.getItem('friends.johnny.#2.office')
		>>> print officenumber
		555450210
	
	We show now other properties:
	
	- If a path ends with ``.?``, the :meth:`Bag.getItem` method return the item's keys.
	
	- If the last path-level contains ``#``, what follows the '#' is considered the key of an item's attribute and the function will return that attribute's value.
	
	- If a path starts with ``?`` then the path is interpreted as a call to the :meth:`Bag.digest` method.
	
	- A path can also ba a list of keys.

.. _bag_digest:

The digest method
=================

	Let's introduce a very useful method: the :meth:`Bag.digest` method. It returns a list of ``n`` tuples including keys and/or values and/or attributes of all the Bag's elements.

	``n`` is the number of expressions called in the method.

	+------------------------+----------------------------------------------------------------------+
	|  *Expressions*         |  Description                                                         |
	+========================+======================================================================+
	| ``'#k'``               | Show the label of each item                                          |
	+------------------------+----------------------------------------------------------------------+
	| ``'#v'``               | Show the value of each item                                          |
	+------------------------+----------------------------------------------------------------------+
	| ``'#v.path'``          | Show inner values of each item                                       |
	+------------------------+----------------------------------------------------------------------+
	| ``'#a'``               | Show attributes of each item                                         |
	+------------------------+----------------------------------------------------------------------+
	| ``'#a.attributeName'`` | Show the attribute called 'attrname' for each item                   |
	+------------------------+----------------------------------------------------------------------+

	>>> print b['documents.letters'].digest('#k,#a.createdOn,#a.createdBy')
	[('letter_to_sheila', '12-4-2003', 'Walter'), ('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark')]

	In this example we made a query of:

	- the Bag's labels, with ``#k``

	- the Bag's attribute createdOn, with ``#a.createdOn``

	- the Bag's attribute createdBy, with ``#a.createdBy``

	**Square-brackets notations:** you have to use the special char ``?`` followed by ``d:`` followed by one or more expressions:

	>>> print b['documents.letters.?d:#k,#a.createdOn,#a.createdBy']
	[('letter_to_sheila', '12-4-2003', 'Walter'), ('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark')]
	>>> print b['documents.letters.?d:#v,#a.createdOn']
	[('file0', '10-7-2003'), ('file1', '11-5-2003'), ('file2', '12-4-2003')]

**Footnotes**

.. [#] Check the :ref:`genro-bag-one` page.

.. [#] If you need to use the dot (``.``) in the name of the instance (label), but you didn't want them to be interpreted as part of a complex path, you have to add a backslash (``\``) before the dot.
