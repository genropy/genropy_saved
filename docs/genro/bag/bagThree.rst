.. _genro_bag_three:

==================
Advanced functions
==================

	* :ref:`bag_backward_path`
	* :ref:`bag_trigger`
	* :ref:`bag_trigger_on_a_bag`
	* :ref:`bag_unsubscribe`
	* :ref:`trigger_on_BagNode`:
	
		* :ref:`bag_validators`
		* :ref:`bag_validator_attributes` (with a :ref:`validator_list_parameter`)
		* :ref:`bag_validator_methods`

.. module:: gnr.core.gnrbag

.. _bag_backward_path:

Backward path
=============

	We remember you that:
	
	* each item is enveloped into a BagNode.
	* each item can be included in other Bags.
	
	This means that a Bag knows its children but not its father (infact a Bag may have more than one father). We could set some stricter hypotesis about a Bag's structure, making it more similar to a tree-leaf model: this would happen if a Bag had a back reference to its Bag father.
	
	.. image:: ../images/bag/bag-backward-path.png

	This feature is implemented by the :meth:`Bag.setBackRef()` method. If we call it on a Bag instance, that Bag becomes the root of a tree structure in which each leaf (BagNode) knows its father. This means that we can traverse a Bag backward using the ``parent`` property of Bag's nodes:

		>>> family = Bag()
		>>> family['grandpa'] = Bag() 
		>>> family['grandpa'].setBackRef()
		>>> family['grandpa.father.son.nephew']=Bag()
		>>> nephew = family['grandpa.father.son.nephew']
		>>> son = family['grandpa.father.son']
		>>> father = family['grandpa.father']
		>>> son.parent == father
		True
		>>> nephew.parent.parent == father
		True
		>>> nephew.parent == son
		True
	
	A Bag with back reference can be traversed with special back-paths that use a new syntax. The ``../`` symbol in a path is equivalent to the ``parent`` property: when the backreference is set, it is possible to get from the Bag its own BagNode:

		>>> nephew['../../'] == father
		True
		
.. _bag_trigger:
	
Trigger
=======

	Bag provides a trigger system.
	
	This means that a Bag may be notified when its data changes. Bag triggers are based on the concept of *subscription*, that is a link between an event (update, insert, delete) with its eventhandler callback functions. The subscribe method defines new subscriptions for update, insert and delete events.

	Triggers may be defined either on Bags or BagNodes; to do so, you have to use the :meth:`Bag.subscribe` method and the :meth:`BagNode.subscribe`::

		Bag.subscribe(update=callback1, insert=callback2, delete=callback3, any=callback4)
		BagNode.subscribe(updval=callback1, updattr=callback2)
	
	Where:
	
	* "update", "insert", "delete" and "any" are the parameters for the Bag's subscribe method that allow to trigger their relative callback.
	* "updval" and "updattr" are the parameters for the BagNode's subscribe method that allow to trigger their relative callback.

.. _bag_trigger_on_a_bag:

Trigger on a Bag: the subscribe method
======================================

	Subscribing an event on a Bag means that every time that the event is triggered, it is propagated along the Bag hierarchy and is triggered by its eventhandler. A subscription can be seen as an event-function couple, so you can define many eventhandlers for the same event.

	Let's consider a Bag like the one shown below:
	
	>>> family = Bag()
	>>> family['Walt'] = Bag()
	>>> walt = family['Walt']
	>>> walt['children'] = Bag()
	>>> walt['children.Mickey.weight'] = 32
	>>> walt['children.Mickey.height'] = 53
	>>> walt['children.Donald.height'] = 51
	
	Now we want that the root Bag called "family" is able to handle any data changes that happens within the Bag itself. So we define as an example three eventhandler functions::

		def onUpdate(node=None, pathlist=None, oldvalue=None, evt=None, **kwargs):
			if evt=='upd_value':
				print """My node at path: %s\n has been updated. Value
				changed from %s to %s \n""" %('.'.join(pathlist), oldvalue, node.getValue())
			if evt=='upd_attrs':
				print 'My node at path: %s\n has been updated. attributes changed\n'

		def onDelete(node=None, pathlist=None, ind=None, **kwargs):
			print 'My node %s at path: %s\n has been deleted from position %i.\n' %(node.getLabel(), '.'.join(pathlist), ind)

		def onInsert(node=None, pathlist=None, **kwargs):
			print 'A new node has been inserted at path: %s \n' %('.'.join(pathlist))

	An eventhandler function receives the following parameters
	
	+--------------------+------------------+-----------------------------------------------------------------+
	|    Parameter       |   Type           |   Description                                                   |
	+====================+==================+=================================================================+
	|   `node`           | ``BagNode``      |  The node inserted/deleted/updated                              |
	+--------------------+------------------+-----------------------------------------------------------------+
	|   `pathlist`       | ``list``         |  Include the Bag subscribed's path linked to the node           |
	|                    |                  |  where the event was catched                                    |
	+--------------------+------------------+-----------------------------------------------------------------+
	|   `oldvalue`       | ``any``          |  For value updates only, it is the previous node's value        |
	+--------------------+------------------+-----------------------------------------------------------------+
	|   `ind`            | ``int``          |  The ordinal position of the node inserted/deleted              |
	+--------------------+------------------+-----------------------------------------------------------------+
	|   `evt`            | ``string``       |  Event type: insert, delete, upd_value, upd_attrs               |
	+--------------------+------------------+-----------------------------------------------------------------+
		
	To allow the "family" Bag to trigger on an insert, on an update and on a delete events, we have to add the :meth:`Bag.subscribe` method to the "family" Bag:
	
	>>> family.subscribe(update=onUpdate, insert=onInsert, delete=onDelete)
	>>> walt['children.Mickey.weight']=36
	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 32 to 36

	>>> walt['children.Donald.weight']=31
	A new node has been inserted at path: Walt.children.Donald 

	>>> walt.delItem('children.Mickey.height')
	My node height at path: walt.children.Mickey 
	has been deleted from position 2.

	.. image:: ../images/bag/bag-trigger.png

	We can add on a Bag many subscriptions for the same event; for example we'll add a generic trigger that handles any event::

		def onBagEvent(node=None, evt=None, pathlist=None, **kwargs):
			print '%s on node %s at path %s'%(evt, node.getLabel(),('.'.join(pathlist) or 'nullpath'))

	>>> family.subscribe(any=onBagEvent) 

	Using the "any" parameter is equivalent to set the same callback function for insert, update and delete events. The new subscripstion doesn't overwrite the existing one, so update events are triggered by both functions.

	>>> walt['children.Mickey.weight']=37
	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 32 to 37
	update on node height at path Walt.children.Mickey.weight

	.. image:: ../images/bag/bag-trigger2.png

	Since an event is propagated along the Bag's hierarchy, it can be triggered by any Bag on the path. In this case there's an insert trigger subscribed by the Bag children ::

		def onNewChild(node=None, ind=None, **kwargs):
			print 'Greetings for %s, your son number %i \n' %(node.getLabel(), ind+1)

	>>> walt['children'].subscribe(insert=onNewChild)
	>>> walt['children.Goofy']=Bag()
	Greetings for Goofy, your son number 3
	A new node has been inserted at path: Walt.children
	ins on node children at path Walt
	
	All the trigger functions are executed at different levels, as the event is catched.

	.. image:: ../images/bag/bag-trigger3.png

.. _bag_unsubscribe:

Unsubscribe a Bag
=================

	It is possible to unsubscribe a bag from a previously subscribed trigger with the :meth:`Bag.unsubscribe` method.
	
	Let's unsubscribe some of the triggers of our example:

	>>> Walt['children'].unsubscribe(insert=onNewChild)
	>>> family.unsubscribe(insert=onInsert)
	
	we have unsubscribed all the events for the insertion.

.. _trigger_on_BagNode:

Trigger on a BagNode
====================

	Sometimes triggering updates of a generic node is not enought: infact a node may need a specific event handling. Trigger on bags assumes that each node is similar to others, that's why we provide a more accurate way to manage update triggers. A BagNode may define its own triggers, by the method subscribe. Since by node's update, we mean either value change or attributes change, subscribe method allows two kinds of trigger: upd_value and upd_attrs::

		def onValueChange(node, info=None, evt=None):
			if evt == 'upd_value':
				print 'My value is changed from %s to %s \n' %(info, node.getValue())
			if evt == 'upd_attrs':
				print 'My attributes: %s is/are changed \n' %(', '.join(info))
			
	A trigger function that handles node's update receives the following parameters:
	
	+--------------------+---------------------+-----------------------------------------------------------------+
	|    Parameter       |   Type              |   Description                                                   |
	+====================+=====================+=================================================================+
	|   `node`           | ``BagNode``         |  The node that has been updated                                 |
	+--------------------+---------------------+-----------------------------------------------------------------+
	|   `info`           | ``list`` or ``any`` |  Old value or list of modified attributes                       |
	+--------------------+---------------------+-----------------------------------------------------------------+
	|   `oldvalue`       | ``any``             |  For value updates only, it is the previous node's value        |
	+--------------------+---------------------+-----------------------------------------------------------------+
	|   `ind`            | ``int``             |  The ordinal position of the node inserted/deleted              |
	+--------------------+---------------------+-----------------------------------------------------------------+
	|   `evt`            | ``string``          |  Event type: upd_value, upd_attrs                               |
	+--------------------+---------------------+-----------------------------------------------------------------+
	
	>>> Walt.getNode('children.Mickey.weight').subscribe(upd_value=onValueChange)
	>>> Walt['children.Mickey.weight']=55
	My value is changed from 36 to 55
	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 36 to 55
	
	There are a BagNode trigger and a Bag trigger [#]_ both launched by the update event. The BagNode trigger is launched because the value of the subscribed node is updated, while the Bag trigger is launched because the Bag is subscribed to another update trigger.

	.. image:: ../images/bag/bag-trigger4.png

.. _bag_validators:

Validators
==========

	The basic idea for a Bag validator is to make a control of the data inserted as a node's value. The validation function for a Bag node can be defined with two different syntaxes:
	
	- through some node attributes.
	
	- using some validator methods.

.. _bag_validator_attributes:

Setting a validator through a node attribute
============================================

	To set a validator through a node attribute you have to use the string ``validate_`` followed by a validation type:
	
	>>> myform.setItem('list.user.name','',validate_case='capitalize')

	When you overwrite the value at the path 'list.user.name' the validator will trigger:

	>>> myform['list.user.name'] = 'john smith'
	>>> print myform['list.user.name']
	John smith

	As you can see, the validator have capitalized the first word, that is "john".

.. _validator_list_parameter:

Values' list for the ``validate_`` parameter
============================================

	Actually you can set these values:

	- validate_case: the parameter string can be 'upper', 'lower', 'capitalize'.
	
	- validate_inList: the parameter string is a list of the values accepted eg: 'value1,value2,value3'.
	
	- validate_length: the parameter string is the min and the max number of char accepted for the value: eg '2,4'.
	
	- validate_hostaddr: no parameters.

.. _bag_validator_methods:

Setting a validator using Bag's methods
=======================================

	To set a validator through the :meth:`Bag.addValidator` method you have to give a path, a validator and a parameterString, where:
	
	* `path`: node's path.
	* `validator`: validation's type.
	* `parameterString`: a string which contains the validation parameters.
	
	>>> myform = Bag()
	>>> myform.addValidator('list.user.name','case','capitalize')
	>>> myform['list.user.name'] = 'ABCD efgh Ij kLM'
	>>> print myform
	0 - (Bag) list: 
	    0 - (Bag) user: 
	        0 - (str) name: Abcd efgh ij klm

	The :meth:`Bag.removeValidator` method allow to remove a validator (parameters: `path` and `validator`).

**Footnotes:**

.. [#] The Bag trigger is made by the ``onUpdate`` function that has been previously defined in the :ref:`bag_trigger_on_a_bag` paragraph.