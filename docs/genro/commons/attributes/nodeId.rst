.. _genro_nodeid:

======
nodeId
======

    * :ref:`nodeId_def`
    * :ref:`nodeId_validity`
    * :ref:`nodeId_examples`

.. _nodeId_def:

definition and description
==========================

    The *nodeId* is an attribute used to specify the ID of a :ref:`bagnode`.
    
    * Every object in Genro is a** :ref:`genro_bag`
    * Every Bag is a collection of :ref:`bagnode`\s
    * Every BagNode is unique because of its *nodeId*
    
    Some object supports the *Code* attribute. For example, the :ref:`genro_framepane` has got the
    *frameCode* and :ref:`genro_toolbar` have got the slotbarCode.
    Through the *Code* attribute, the *nodeId* is automatically created in the object to which you
    give the code and in every child of this object.
    
.. _nodeId_validity:

validity
========

    **Validity:** you can give ``nodeId`` attribute to the following objects:
    
    * add???
    
.. _nodeId_examples:

examples
========

    add???