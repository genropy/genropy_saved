.. _bag:

===
Bag
===

    *Last page update*: |today|
    
    * :ref:`bag_intro`
    * :ref:`bag_section_index`
    
.. _bag_intro:

introduction
============

    A :class:`Bag <gnr.core.gnrbag.Bag>` is a Genro class used to create a multi-purpose
    datastructure, and it is ideal for storing and retrieving any kind of complex hierarchical
    data in tidily and deeply way.
    
    Nested elements can be accessed with a path of keys joined with dots:
    
    >>> mybag['foo.bar'] = 'spam'
    >>> x = mybag['foo.bar']
    
    A Bag takes some Dictionary features:
    
    * Both Bag and Dictionary are made by a set of ``key:value`` pairs.
    * Values are accessed using a key (called *path*).
    * Both Bag and Dictionary can shrink or grow as needed.
    * Both Bag and Dictionary can be nested.
    * A Bag inherit some Dictionary methods [#]_ and some syntax forms (that we will document
      in the following Bag documentation pages).
    
    Most important, a Bag carries some features that Dictionary hasn't got:
    
    +-----------------------------------------------------------------+----------------------------------------------------------+
    | Dictionary                                                      | Bag                                                      |
    +=================================================================+==========================================================+
    | A Dictionary is a mutable unordered set of ``key:value`` pairs. | A Bag is a unmutable ordered set of ``key:value`` pairs. |
    +-----------------------------------------------------------------+----------------------------------------------------------+
    | A Dictionary is NOT hierarchic.                                 | A Bag IS hierarchic.                                     |
    +-----------------------------------------------------------------+----------------------------------------------------------+
    | A Dictionary is NOT ordered.                                    | A Bag IS ordered.                                        |
    +-----------------------------------------------------------------+----------------------------------------------------------+
    | Keys must be unique.                                            | You can have different values with the same key.         |
    +-----------------------------------------------------------------+----------------------------------------------------------+
    
.. _bag_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    :numbered:
    
    definitions
    basic_functions
    basic_functions_two
    Attributes <attributes>
    Nodes <nodes>
    advanced_functions
    from_to
    resolver_dynamics
    library
    
**Footnotes:**

.. [#] Check the :ref:`bag_dictionary_methods` section for further details.
.. [#] You might be wondering why we call "label" the ``key`` argument of a Bag: its origin is historical: the Bag has been created before Genro Team began to use Python language.
