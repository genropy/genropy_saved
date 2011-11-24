.. _bagnode:

=======
BagNode
=======

    *Last page update*: |today|
    
    We discovered in the previous section that we can associate a set of :ref:`bag_attributes`
    to each item, and we know that each item is a BagNode.
    
    We remember you that a :class:`BagNode <gnr.core.gnrbag.BagNode>` is a class composed by:
    
    * a single label.
    * A single value (or item).
    * One or more attributes.
    
    If you need to work with nodes, you may get them with the following methods:
    
    * :meth:`~gnr.core.gnrbag.Bag.getNode`: return a node.
    * :meth:`~gnr.core.gnrbag.Bag.getNodes`: return a list of nodes.
    * :meth:`~gnr.core.gnrbag.Bag.getNodeByAttr`: return the node who has the
      passed couple "value-attribute"
    
    >>> mybag = Bag({'paper':1,'scissors':2})
    >>> papernode = mybag.getNode('paper')
    >>> mybag.setItem('rock',3,color='grey')
    >>> rocknode=mybag.getNodeByAttr('color','grey')
    >>> nodes=mybag.getNodes()
    
    The :meth:`getNodes() <gnr.core.gnrbag.Bag.getNodes>` method implements the Bag's property nodes:
    
    >>> mybag.getNodes() == mybag.nodes
    True
    
    If you have a node instance you may use one of the following methods:
    
    * :meth:`~gnr.core.gnrbag.BagNode.hasAttr`: check if a node has the given pair label-value
      in its attributes' dictionary.
    * :meth:`~gnr.core.gnrbag.BagNode.setAttr`: receive one or more key-value couple, passed as
      a dict or as named parameters, and sets them as attributes of the node.
    * :meth:`~gnr.core.gnrbag.BagNode.getAttr`: return the value of an attribute. You have to
      specify the attribute's label. If it doesn't exist then it returns a default value.
    * :meth:`~gnr.core.gnrbag.BagNode.delAttr`: delete the attribute with the passed names.
    * :meth:`~gnr.core.gnrbag.BagNode.getLabel`: return the node's label.
    * :meth:`~gnr.core.gnrbag.BagNode.setLabel`: sets the node's label.
    * :meth:`~gnr.core.gnrbag.BagNode.getValue`: return the node's value.
    * :meth:`~gnr.core.gnrbag.BagNode.setValue`: set the node's value.
    
    >>> print papernode.hasAttr('color')
    False
    >>> papernode.setAttr(color='white')
    >>> print papernode.getAttr('color')
    white
    >>> papernode.replaceAttr(color='yellow')
    >>> papernode.delAttr('color')
    >>> papernode.setLabel('sheet')
    >>> print papernode.getLabel()
    sheet
    >>> papernode.setValue(8)
    >>> papernode.getValue()
    8
    
    For a complete list of the :class:`BagNode <gnr.core.gnrbag.BagNode>` methods, check the :ref:`gnrbags_bagnode` section.