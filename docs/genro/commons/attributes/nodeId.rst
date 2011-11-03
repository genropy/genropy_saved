.. _nodeid:

======
nodeId
======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *nodeId* attribute is supported by every element
    
    * :ref:`nodeid_def`
    * :ref:`nodeid_examples`
    
.. _nodeid_def:

description
===========

    The *nodeId* is an attribute used to specify the ID of a :ref:`bagnode`.
    
    .. warning:: remember that:
                 
                 * Every object in Genro is a :ref:`bag`
                 * Every Bag is a collection of :ref:`BagNodes <bagnode>`
                 * Every BagNode is unique because of its *nodeId*
                 
    Some object supports an attribute that creates automatically the *nodeId* for the object
    itself (and when it has got children, for its children). In particular:
    
    * the :ref:`includedgrid` has got the *frameCode* attribute
    * the :ref:`paletteGrid` has got the *paletteCode* attribute
    * the :ref:`framepane` has got the :ref:`frame_framecode` attribute
    * the :ref:`slotBar <toolbar>` and the :ref:`slotToolbar <toolbar>` have got the
      :ref:`toolbar_slotbarcode`
      
.. _nodeid_examples:

examples
========

    add???