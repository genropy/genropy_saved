	.. _genro-bag-three:

====================
 Advanced functions
====================

	- :ref:`bag-backward-path`
	
	.. _bag-backward-path:

Backward path
=============

	We said that each item is enveloped into a bag node, and that can be contained by several bags in different places. This means that a Bag knows its children but ignores who is its father, in fact it may have many fathers. We could set stricter hypotesis about the structure of a bag, making it more similar to a tree-leaf model: this would happen if a bag had a back reference to the bag that contains it.
	
	.. image:: ../images/backward_path.png

	This feature is implemented by the :meth:`setBackRef()` method. If we call it on a Bag instance, that Bag becomes the root of a tree structure in which each leaf (BagNode) knows its father. This means that we can traverse a Bag backward using the parent properties of Bag's nodes.

		family = Bag()
		family['grandpa'] = Bag() 
		family['grandpa'].setBackRef()
		family['grandpa.father.son.nephew']=Bag()

		nephew = family['grandpa.father.son.nephew']
		son = family['grandpa.father.son']
		father = family['grandpa.father']

		>>> son.parent == father
		True
		>>> nephew.parent.parent == father
		True
		>>> nephew.parent == son
		True
	A bag with back reference can be traversed with special back-paths that use a new syntax. The symbol '../' in a path is equivalent to the property parent.

	When the backreference is set, it is possible to get from the bag its own BagNode:

		>>> nephew['../../'] == father
		True
	Trigger

	Bag provides a trigger system. This means that a Bag may be notified when its data changes. Bag triggers are based on the concept of subscription, that is a link between an event (update, insert, delete) with its eventhandler callback functions. The method subscribe defines new subscriptions for update, insert, delete events.

	Triggers may be defined either on bags or nodes, in fact there are two subscribe methods.

	Bag.subscribe(update=callback1, insert=callback2, delete=callback3, any=callback4)
	BagNode.subscribe(updval=callback1, updattr=callback2)
	Trigger on Bag

	Subscribing an event on a bag means that every time that it happens, it is propagated along the bag hierarchy and is triggered by its eventhandler. A subscription can be seen as a couple event-function, this means that I can define many eventhandlers for the same event.

	Let's consider a bag like the one shown below:

	family=Bag()
	family['Walt']=Bag()
	walt=family['Walt']
	walt['children']=Bag()
	walt['children.Mickey.weight']=32
	walt['children.Mickey.height']=53
	walt['children.Donald.height']=51
	Now we want that the root bag family to handle any data changes that happens within it. In order to do this we define three examples eventhandler functions.

	def onUpdate(node=None, pathlist=None, oldvalue=None, evt=None, **kwargs):
	    if evt=='upd_value':
	        print 'My node at path: %s\n
	        has been updated. Value changed from %s to %s \n' %('.'.join(pathlist), oldvalue, node.getValue())
	    if evt=='upd_attrs':
	        print 'My node at path: %s\n
	        has been updated. attributes changed\n'

	def onDelete(node=None, pathlist=None, ind=None, **kwargs):
	    print 'My node %s at path: %s\n
	    has been deleted from position %i.\n' %(node.getLabel(), '.'.join(pathlist), ind)

	def onInsert(node=None, pathlist=None, **kwargs):
	    print 'A new node has been inserted at path: %s \n' %('.'.join(pathlist))

	An eventhandler function receives the following kwargs.

	parameter	type	Description
	node	BagNode	The node inserted/deleted/updated
	pathlist	list	A list that represents the path from the bag subscribed to the node where the event was catched
	oldvalue	any	For value updates only, it is the previous node's value
	ind	int	The ordinal position of the node inserted/deleted
	evt	string	Event type: insert, delete, upd_value, upd_attrs
	Now, we want the bag family to trigger insert, update and delete events, in order to do this we subscribe them.

	>>> family.subscribe(update=onUpdate, insert=onInsert, delete=onDelete)

	>>> walt['children.Mickey.weight']=36
	>>>
	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 32 to 36

	>>> walt['children.Donald.weight']=31
	>>>
	A new node has been inserted at path: Walt.children.Donald 

	>>> walt.delItem('children.Mickey.height')
	>>>
	My node height at path: walt.children.Mickey 
	has been deleted from position 2.    



	On a bag we can add many subscriptions for the same event; for example we'll add a generic trigger that handles any event:

	def onBagEvent(node=None, evt=None, pathlist=None, **kwargs):
	    print '%s on node %s at path %s'%(evt, node.getLabel(),('.'.join(pathlist) or 'nullpath'))

	>>> family.subscribe(any=onBagEvent) 

	Using the parameter any is equivalent to set the same callback function for insert, update and delete events. The new subscripstion doesn't overwrite so that update events is triggered by both functions.

	>>> walt['children.Mickey.weight']=37
	>>>
	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 32 to 36

	upd on node height at path Walt.children.Mickey.weight



	Since an event is propagated along the bag's hierarchy, it can be triggered by any bag on the path. In this case there is an insert trigger subscribed by the bag children :

	def onNewChild(node=None, ind=None, **kwargs):
	    print 'Greetings for %s, your son number %i \n' %(node.getLabel(), ind+1)


	>>> walt['children'].subscribe(insert=onNewChild)
	>>> walt['children.Goofy']=Bag()
	>>>
	Greetings for Goofy, your son number 3

	A new node has been inserted at path: Walt.children

	ins on node children at path Walt
	All the trigger functions are executed at different levels, as the event is catched.



	It is possible to unsubscribe a bag from a previously subscribed trigger. Let's unsubscribe some the triggers of our example:

	>>>Walt['children'].unsubscribe(insert=onNewChild)
	>>>family.unsubscribe(insert=onInsert)
	Trigger on BagNode

	Sometimes triggering updates of a generic node is not enought, a node may need a specific event handling. Trigger on bags assumes that each node is similar to others, that's why we provide a more accurate way to manage update triggers. A BagNode may define its own triggers, by the method subscribe. Since by node's update, we mean either value change or attributes change, subscribe method allows two kinds of trigger: upd_value and upd_attrs.

	def onValueChange(node, info=None, evt=None):
	    if evt == 'upd_value':
	        print 'My value is changed from %s to %s \n' %(info, node.getValue())
	    if evt == 'upd_attrs':
	        print 'My attributes: %s is/are changed \n' %(', '.join(info))
	A trigger function that handles node's update receives the following parameters:

	parameter	type	description
	node	BagNode	The node that has been updated
	info	list or any	Old value or list of modified attributes
	evt	string	event type: upd_value,upd_attrs
	>>>Walt.getNode('children.Mickey.weight').subscribe(upd_value=onValueChange)
	>>>Walt['children.Mickey.weight']=55
	>>>
	My value is changed from 36 to 55

	My node at path: Walt.children.Mickey.weight 
	has been updated. Value changed from 36 to 55
	As shown in the example and in the below image, there are a BagNode trigger and a bag trigger both launched by the update event. The BagNode trigger is lauched beacuse the value of the subscribed node is updated, and the bag trigger is launched because the bag is subscribed to another update trigger.



	Validators

	The basic ideas of Bag validator is to make a control of the data which can be inserted as value of a node. This mean that you can set a function of validation for a Bag node with two different sintaxes: as attributes or with the use of the Bag method addValidator().

	Validation examples

	Setting with a node attribute:

	# using the prefix validate_ followed by the type of validation.
	myform.setItem('list.user.name','',validate_case='capitalize')


	# now when you overwrite the value at the path 'list.user.name' the Bag does the control

	myform['list.user.name'] = 'John Smith'

	Setting using the setValidator method:

	# using the prefix validate_ followed by the type of validation. The value of the attribute is the parameter of that validtation
	myform.setItem('list.user.name',None,validate_case='capitalize')


	# now set the validator with the Bag method addValidator(self, path, validator, parameterString))

	myform = Bag()

	myform.addValidator('list.user.name','case','capitalize' )

	# now when you overwrite the value at the path 'list.user.name' the Bag does the control

	myform['list.user.name'] = 'John Smith'

	There is also the method removeValidator(self, path, validator) that remove the validator set into the path

	validator function

	Actually you can set this validation:

	validate_case: the parameter string can be 'upper', 'lower', 'capitalize'
	validate_inList: the parameter string is a list of the values accepted eg: 'value1,value2,value3'
	validate_length: the parameter string is the min and the max number of char accepted for the value: eg '2,4'
	validate_hostaddr: no parameters
	Bag from/to source

	As we have seen in the previous chapter, a Bag is a completely dynamic structure. A Bag has a polymorphic interaction with many complex data sources, so it's possible to fill it passing

	A string representing an XML section
	A file path of an XML file
	An URI of a remore XML file
	A file path of a directory on local disk
	A pickle file
	A Bag
	fromlocal= Bag('%s/test_files/standardxml.xml' %current)
	fromurl= Bag('http://www.plone.org')
	fromdirectory= Bag('%s/test_files' %current)

	stringxml='<?xml version="1.02" encoding="UTF-8"?><a><b name="fuffy"><d>dog</d></b><c/></a>'

	fromstringxml=Bag(stringxml)


	A bag can also be serialized into different formats:

	XML
	pickle
	JSON
	etc.


	In the following chapters we'll examine how to load and convert bags in many formats.

	Bag and XML

	toXml

	A bag can be exported to an xml source with the method toXml() This method returns a text, that is a complete standard XML version of the Bag, including the encoding tag <?xml version=\'1.0\' encoding=\'UTF-8\'?>. Since an XML document needs an unique root node, the method creates as outer level the node <GenRoBag>. Each bag becomes an XML block that contains other XML elements.

	Bag's item	 XML element
	label	tag
	value	element's content
	attributes	attributes
	toXml() may receive twe optional parameters:

	filename, that is the path of the output file. If filename is passed, the method returns None, and creates the file at the correct position.
	encoding is used to set the XML encoding: default value is UTF-8.
	XML is a very common instrument to transport data, but transforming any datastructure into XML doument makes you loss the data types. This does't happen with the method toXml(). The method adds for each XML element a special attribute called '_T' that represents a code of the original type of item's value, unless the original type was string.

	mybag= Bag()
	mybag['birthday']=datetime.date(1974,11,23)
	mybag['height']=1.76
	mybag['weight']=65
	xml_source=mybag.toXml()

	>>> print xml_source
	<?xml version='1.0' encoding='UTF-8'?>
	<GenRoBag>
	<birthday _T="D">1974-11-23</birthday>
	<height _T="R">1.76</height>
	<weight _T="L">65</weight>
	</GenRoBag>
	Here is a table that show the keywords used to represents data types.

	Codes	Data Type
	'T'	 txt
	'R'	 float
	'L'	int
	'B	bool
	'D'	 datetime
	'DT'	datetime
	'H'	 datetime.time
	Also attributes' types aren't lost during the transformation, in fact in the value of each attribute is added a substring composed by '::type', unless it's original type was string.

	mybag.setAttr('height',lastMeasure=datetime.date(2006,10,3))
	xml_source = mybag.toXml()

	>>> print xml_source
	<?xml version='1.0' encoding='UTF-8'?>
	<GenRoBag>
	<birthday _T="D">1974-11-23</birthday>
	<height _T="R" lastMeasure="2006-10-03::D">1.76</height>
	<weight _T="L">65</weight>
	</GenRoBag>
	from XML

	If the Bag's constuctor receives as parameter source a filepath, an URL or a string that contains XML source, it creates a Bag that represents the XML document. If the XML source provides type indication, such as _T attribute or ::Type suffix, bag's values and attributes will have the correct type.

	xmlbag=Bag(xml_source)

	>>> print xmlbag
	0 - (date) birthday: 1974-11-23  
	1 - (float) height: 1.76  <lastMeasure='2006-10-03::D'>
	2 - (int) weight: 65