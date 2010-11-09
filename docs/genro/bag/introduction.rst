	.. _genro-bag-intro:

=======================
 Introduction to a Bag
=======================

	- :ref:`bag-what`
	
	- :ref:`bag-intro-hierarchical`
	
	.. _bag-what:

What is a Bag?
==============

	A :class:`Bag` is a Genro class, a multi-purpose datastructure, and it is ideal for storing and retrieving any kind of complex data in tidily and deeply way.
	
	A Bag looks like a Dictionary, infact:
	
	- Both Bag and Dictionary are made by a set of ``key:value`` pairs.

	- Values are accessed using a key.

	- Both Bag and Dictionary can shrink or grow as needed.

	- Both Bag and Dictionary can be nested.
	
	- A Bag inherit some Dictionary methods [#]_ and some syntax forms (that we will document you in the following Bag documentation pages).
	
	A Bag carries some features that Dictionary hasn't got:
	
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| Dictionary                                                        | Bag                                                                  |
	+===================================================================+======================================================================+
	| A Dictionary is a mutable unordered set of ``key:value`` pairs.   | A Bag is a stable ordered set of ``key:value`` pairs.                |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| A Dictionary is NOT hierarchic.                                   | A Bag IS hierarchic.                                                 |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| A Dictionary is NOT ordered.                                      | A Bag IS ordered.                                                    |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	| Keys must be unique.                                              | You can have different values with the same key.                     |
	+-------------------------------------------------------------------+----------------------------------------------------------------------+
	
	So, the three main Bag features are:
	
	- A Bag is hierarchic
	
	- A Bag is ordered
	
	- You can have different values with the same key.
	
	In the next paragraphs we analyze in depth these features.

	.. _bag-intro-hierarchical:

Definitions
===========

	**Bag definition:** A Bag is a collection of :ref:`bag-nodes`. You can use a Bag as a `flat Bag`_ or as a `hierarchical Bag`_
	
	**BagNode definition:** a :class:`BagNode` (or "node") is a Genro class composed by three metadata:
	
	- a single label.
	
	- a single value.
	
	- one or more :ref:`bag-attributes`.

	Where:
	
	- The "label"" is the key of the BagNode.
	
	- The "value" contains the value of the Bagnode.
	
	- The "attributes" allow to insert other metadata (for more information, check the :ref:`bag-attributes` page).
	
		.. note:: The couple ``label:value`` carries many analogies with the ``key:value`` couple Dictionary [#]_, so you can think to the Bag label as a transposition of the Dictionary key (for example, with the :meth:`Bag.keys` method you will get all the Bag labels) but for its nature a key is unique, while Bag label can be unique or not.
	
	Let's see a scheme of a BagNode:

	.. image:: BagNode.png

	.. _flat Bag:

	**flat Bag definition:** a flat Bag is a Bag in which all its BagNodes don't have a Bag as value.
	
	Example: ???
	
	.. _hierarchical Bag:
	
	**hierarchical Bag definition:** ???
	
	Finally, a BagNode value can be a Bag: these features make the Bag a recursive and a hierarchical container.


**Footnotes:**

.. [#] Check the :ref:`bag_dictionary_methods` paragraph for further details.

.. [#] You might be wondering why we call "label" the ``key`` argument of a Bag: its origin is storical: the Bag has been created before Genro Team began to use Python language.
