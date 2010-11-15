	.. _genro-bag-intro:

=====
 Bag
=====

	- :ref:`bag-what`
	
	- :ref:`bag-intro-hierarchical`
	
	.. _bag-what:

Overview
========

	A :class:`Bag` is a Genro class used to create a multi-purpose datastructure, and it is ideal for storing and retrieving any kind of complex hierarchical data in tidily and deeply way.
	
	Nested elements can be accessed with a path of keys joined with dots.
	
	>>> mybag['foo.bar'] = 'spam'
	>>> x = mybag['foo.bar']
	
	We are going to see that:
	
	- A Bag is hierarchic.
	
	- A Bag is ordered.
	
	- You can have different values at the same path.
	
	Also, a Bag takes some Dictionary features:
	
	- Both Bag and Dictionary are made by a set of ``key:value`` pairs.

	- Values are accessed using a key (*path*).

	- Both Bag and Dictionary can shrink or grow as needed.

	- Both Bag and Dictionary can be nested.
	
	- A Bag inherit some Dictionary methods [#]_ and some syntax forms (that we will document in the following Bag documentation pages).
	
	A Bag carries some features that Dictionary hasn't got:
	
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| Dictionary                                                        | Bag                                                                  |
	+===================================================================+======================================================================+
	| A Dictionary is a mutable unordered set of ``key:value`` pairs.   | A Bag is a unmutable ordered set of ``key:value`` pairs.             |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| A Dictionary is NOT hierarchic.                                   | A Bag IS hierarchic.                                                 |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| A Dictionary is NOT ordered.                                      | A Bag IS ordered.                                                    |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| Keys must be unique.                                              | You can have different values with the same key.                     |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	
	.. _bag-intro-hierarchical:

Definitions
===========

	**Bag definition:** A Bag is a collection of :ref:`bag-nodes`. You can use a Bag as a `flat Bag`_ or as a `hierarchical Bag`_.
	
	**BagNode definition:** a :class:`BagNode` (or "node") is a Genro class composed by three metadata:
	
	- a single label.
	
	- a single value (or *item*).
	
	- one or more :ref:`bag-attributes`.

	Where:
	
	- The "value" contains the value of the Bagnode.
	
	- The "attributes" allow to insert other metadata (for more information, check the :ref:`bag-attributes` page).
	
		.. note:: The couple ``label:value`` carries many analogies with the ``key:value`` couple Dictionary [#]_, so you can think to the Bag label as a transposition of the Dictionary key (for example, with the :meth:`gnr.core.gnrbag.Bag.keys` method you will get all the Bag labels) but for its nature a key is unique, while Bag label can be unique or not. <???> approfondire! spiegare che la vera chiave di una Bag è il *path*, ma che c'è un'analogia con i metodi del Python dict() (ad esempio keys()...)</???>
	
	Let's see a scheme of a BagNode:

	.. image:: ../images/BagNode.png
	
	A BagNode value can be a Bag, so a Bag is a *recursive and hierarchical container*.

	We now introduce the two definitions of a Bag:

	.. _flat Bag:

	**flat Bag:** it is a Bag in which all of its BagNodes don't have a Bag as their value.
	
	.. _hierarchical Bag:
	
	**hierarchical Bag:** it is a nested Bag with complex path, including Bags as a value of some BagNodes (check :ref:`bag-path` paragraph for more explanation).
	
		.. note:: there is no syntax difference in the two definitions, as you can see in the :ref:`bag-instance` paragraph.
	
	Each Bag may access directly to its inner elements using a *path*.
	
	**path:** a *path* is a concatenation of traversed Bag labels separated by a dot (``.``) (For more information, check :ref:`bag-path` paragraph).

**Footnotes:**

.. [#] Check the :ref:`bag_dictionary_methods` paragraph for further details.

.. [#] You might be wondering why we call "label" the ``key`` argument of a Bag: its origin is storical: the Bag has been created before Genro Team began to use Python language.
