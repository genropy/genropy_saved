.. _bag_def:

===============
Bag definitions
===============

    1. *definition -* **Bag**: A Bag is a collection of :ref:`BagNodes <bagnode>`.
       You can use a Bag as a `flat Bag`_ or as a `hierarchical Bag`_.
       
    2. *definition -* **BagNode**: a :class:`BagNode <gnr.core.gnrbag.BagNode>` (or "node") is a Genro
       class composed by three metadata:
       
       * a single label.
       * a single value (or *item*).
       * one or more :ref:`bag_attributes`.
       
       Where:
       
       * The "value" contains the value of the Bagnode.
       * The "attributes" allow to insert other metadata (for more information, check the :ref:`bag_attributes` page).
       
           .. note:: The couple ``label:value`` carries many analogies with the ``key:value`` couple
                     Dictionary [#]_, so you can think to the Bag label as a transposition of the Dictionary
                     key (for example, with the :meth:`keys() <gnr.core.gnrbag.Bag.keys>` method you will get
                     all the Bag labels) but for its nature a key is unique, while Bag label can be unique or not
                     
       Let's see a scheme of a BagNode:
       
       .. image:: ../_images/bag/bag-bagnode.png
       
       A BagNode value can be a Bag, so a Bag is a *recursive and hierarchical container*.
       
       We now introduce the two definitions of a Bag:
       
    .. _flat Bag:
    
    3. *definition -* **flat Bag**: it is a Bag in which all of its BagNodes don't have a Bag as their value.
    
    .. _hierarchical Bag:
    
    4. *definition -* **hierarchical Bag**: it is a nested Bag with complex path, including Bags as a value
       of some BagNodes (check :ref:`bag_path` section for more explanation).
       
           .. note:: there is no syntax difference in the two definitions, as you can see in the
                     :ref:`bag_instance` section.
       
       Each Bag may access directly to its inner elements using a *path*.
       
    5. *definition -* **path**: it is a concatenation of traversed Bag labels separated by a dot (``.``)
       (For more information, check :ref:`bag_path` section).