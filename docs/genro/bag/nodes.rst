	.. _bag-nodes:

=======
 nodes
=======

	We discovered in the previous paragraph that we can associate a set of attributes to each item. We will now discuss a more advanced concept about Bag, introducing the BagNode.
	
	Until now we have considered the hierachical Bag as a chain of nested bags. That is not properly true, because *each bag's element is a BagNode*.

	A 'BagNode' is an object composed of three parts:

	label
	attributes
	value (or item)
	In order to avoid confusion between the terms item and node, what we used to call an 'item' we will now call a value.

	If you need to work with nodes, you may get them with the methods:

	- getNode(path): returns a node
	
	- getNodes(): returns a list of nodes
	
	- getNodeByAttr(attribute, attr_value): returns the node that has the passed couple attribute-value
	
	>>> mybag = Bag({'paper':1,'scissors':2})
	>>> papernode = mybag.getNode('paper')
	>>> mybag.setItem('rock',3,color='grey')
	>>> rocknode=mybag.getNodeByAttr('color','grey')
	>>> nodes=mybag.getNodes()
	
	The method getNodes() implements the bag's property nodes.

	>>>mybag.getNodes() == mybag.nodes
	True

	If you have a node instance you may use one of the following methods:

	hasAttr(attribute)	returns true if the node has a value for the passed attribute
	setAttr(attribute=value)	set to the node one or more attributes passed as kwargs
	getAttr(attribute)	returns the attribute's value
	replaceAttr(attribute=value)	replaces the value of one or more attributes passed as kwargs
	delAttr(attribute)	deletes the attribute with the passed name
	getLabel()	returns the node's label
	setLabel(label)	sets the node's label
	getValue()	returns the node's value
	setValue()	sets the node's value
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