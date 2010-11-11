	.. _genro-bagnode-class:

===================
 The BagNode class
===================

.. class:: BagNode

	.. method:: delAttr(self, *attrToDelete)
	
		It receives one or more attributes' labels and removes them from the node's attributes.

	.. method:: getAttr(self, label=None, default=None)
		
		It returns the value of an attribute. You have to specify the attribute's label. If it doesn't exist then it returns a default value.
		
		* `label`: the attribute's label that should be get.
	
	.. method:: getLabel(self)
	
		Return the node's label.
	
	.. method:: getValue(self, mode='')

		Return the value of the BagNode.
		
		* `mode='static`: allow to get the resolver instance instead of the calculated value.
			
		* `mode='weak`: allow to get a weak ref stored in the node instead of the actual object.
		
	.. method:: hasAttr(self, label=None, value=None)
	
		Check if a node has the given pair label-value in its attributes' dictionary.
	
	.. method:: setAttr(self, attr = None, trigger = True, _updattr = True, _removeNullAttributes = True,**kwargs)
        
		It receives one or more key-value couple, passed as a dict or as named parameters, and sets them as attributes of the node.
        
		* `attr`: the attributes' dict that should be set into the node.
	
	.. method:: setLabel(self, label)
	
		Set node's label.
	
	.. method:: setValue(self, value, trigger=True, _attributes = None, _updattr = None, _removeNullAttributes = True)
		
		Set the node's value (unless the node is locked).
		
		* `value`: the value to set the new bag inherits the trigger of the parentbag and calls it sending an update event.
		