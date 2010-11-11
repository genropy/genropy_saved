	.. _genro-bag-class:

===============
 The Bag class
===============

.. class:: Bag

	.. note:: The square brackets around some parameters in the following method signature denote that the parameter is optional, not that you should type square brackets at that position. You will see this notation frequently in the Genro Library Reference.
	
	.. note:: Some methods have the "square-brackets notation": it is a shorter notation for the method.

	.. method:: addItem(label,value)

		Used to add different items with the same label:
		
		>>> beatles = Bag()
		>>> beatles.setItem('member','John')    # alternatively, you could write beatles.addItem('member','John')
		>>> beatles.addItem('member','Paul')
		>>> beatles.addItem('member','George')
		>>> beatles.addItem('member','Ringo')
		>>> print beatles
		0 - (str) member: John
		1 - (str) member: Paul
		2 - (str) member: George
		3 - (str) member: Ringo
		
		You can't use the *square-brackets notations* within this method, because if you try to insert different values with the same label you would lose all the values except for the last one.
		
	.. method:: asDict()
	
		Allow to transform a Bag in a dict.
		
		.. note:: If you attempt to transform a hierarchical bag to a dictionary, the resulting dictionary will contain nested bags as values. In other words only the first level of the Bag is transformed to a dictionary, the transformation is not recursive.

	.. method:: asString()
	
		Allow to transform a Bag in a string.
		
		The Bag use as repr(*object*) method the asString() method.
		
	.. method:: digest(expression[,otherExpressions])
	
		It returns a list of ``n`` tuples including keys and/or values and/or attributes of all the Bag's elements.
		
		``n`` is the number of expressions called in the method.

		+------------------------+----------------------------------------------------------------------+
		|  *Expressions*         |  Description                                                         |
		+========================+======================================================================+
		| ``'#k'``               | Show the label of each item                                          |
		+------------------------+----------------------------------------------------------------------+
		| ``'#v'``               | Show the value of each item                                          |
		+------------------------+----------------------------------------------------------------------+
		| ``'#v.path'``          | Show inner values of each item                                       |
		+------------------------+----------------------------------------------------------------------+
		| ``'#a'``               | Show attributes of each item                                         |
		+------------------------+----------------------------------------------------------------------+
		| ``'#a.attributeName'`` | Show the attribute called 'attrname' for each item                   |
		+------------------------+----------------------------------------------------------------------+

		>>> b=Bag()
		>>> b.setItem('documents.letters.letter_to_mark','file0',createdOn='10-7-2003',createdBy= 'Jack')
		>>> b.setItem('documents.letters.letter_to_john','file1',createdOn='11-5-2003',createdBy='Mark',lastModify='11-9-2003')
		>>> b.setItem('documents.letters.letter_to_sheila','file2')
		>>> b.setAttr('documents.letters.letter_to_sheila',createdOn='12-4-2003',createdBy='Walter',lastModify='12-9-2003',fileOwner='Steve')
		>>> print b['documents.letters'].digest('#k,#a.createdOn,#a.createdBy')
		[('letter_to_sheila', '12-4-2003', 'Walter'), ('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark')]
		
		**Square-brackets notations:**
		
		You have to use the special char ``?`` followed by ``d:`` followed by one or more *expressions*:

		>>> print b['documents.letters.?d:#k,#a.createdOn,#a.createdBy']
		[('letter_to_sheila', '12-4-2003', 'Walter'), ('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark')]
		>>> print b['documents.letters.?d:#v,#a.createdOn']
		[('file0', '10-7-2003'), ('file1', '11-5-2003'), ('file2', '12-4-2003')]

	.. method:: getAttr(path, attribute)
	
		Return a single attribute if it exists, else it returns ``None``, so that this method never raises a ``KeyError``.

		>>> b = Bag()
		>>> b.setItem('documents.letters.letter_to_mark','file0',createdOn='10-7-2003',createdBy= 'Jack')
		>>> print b
		0 - (Bag) documents: 
		    0 - (Bag) letters: 
		        0 - (str) letter_to_mark: file0  <createdOn='10-7-2003' createdBy='Jack'>
		>>> print b.getAttr('documents.letters.letter_to_mark', 'createdBy')
		Jack
		>>> print b.getAttr('documents.letters.letter_to_mark', 'fileOwner')
		None
		
		**Square-brackets notations:**
		
		You have to use the special char ``?`` followed by the attribute's name:

		>>> print b['documents.letters.letter_to_sheila?fileOwner']
		Steve
	
	.. method:: getItem(path, default=None[, mode=None])

		Return the value if it is in the Bag, else it returns ``None``, so that this method never raises a ``KeyError``:
		
		* `default`: it is the default value.
		
		* `mode='static'`: with this attribute the getItem doesn't solve the Bag :ref:`bag_resolver`.
		
		>>> mybag = Bag()
		>>> mybag.setItem('a',1)
		>>> first= mybag.getItem('a')
		>>> second = mybag.getItem('b')
		>>> print(first,second)
		(1, None)
		
		**Square-brackets notations:**
			
		>>> mybag = Bag({'a':1,'b':2})
		>>> second = mybag['b']
		>>> print second
		2

	.. method:: getNode(self, path=None, asTuple=False, autocreate=False, default=None)
	
		Return the BagNode stored at the relative path.
		
		* `path`: path of the given item.
		
		* `asTuple`: ???
		
		* `autocreate`: ???
		
		* `default`: ???
	
	.. method:: getNodeByAttr(self, attr, value [, path=None])
	
		Return: a BagNode with the requested attribute.
		
		Return the first found node which has an attribute named 'attr' equal to 'value'.
		
		* `attr`: path of the given item.
		
		* `value`: path of the given item.
		
		* `path`: optional, an empty list that will be filled with the path of the found node.
		
	.. method:: getNodes(self, condition=None)
	
		Get the actual list of nodes contained in the Bag.
		
	.. method:: has_key(key)
	
		Test for the presence of key in the Bag.
		
		>>> b = Bag({'a':1,'b':2,'c':3})
		>>> b.has_key('a')
		True
		>>> b.has_key('abc')
		False

	.. method:: items()
	
		Return a copy of the Bag as a list of tuples (``key, value`` pairs)
		
		>>> b = Bag({'a':1,'b':2,'c':3})
		>>> b.items()
		[('a', 1), ('c', 3), ('b', 2)]

	.. method:: keys()

		Return a copy of the Bag as a list of keys
		
		>>> b = Bag({'a':1,'a':2,'a':3})
		>>> b.keys()
		['a', 'c', 'b']
	
	.. method:: merge(upd_values=True, add_values=True, upd_attr=True, add_attr=True)
	
		.. deprecated:: 0.7

		.. note:: This method have to be rewritten.

		Allow to merge two bags into one.

		It has four optional parameters:

		* `upd_values`: ???
		
		* `add_values`: ???
		
		* `upd_attr`: ???
		
		* `add_attr`: ???
		
		>>> john_doe=Bag()
		>>> john_doe['telephones']=Bag()
		>>> john_doe['telephones.house']=55523412
		>>> other_numbers=Bag({'mobile':444334523, 'office':3320924, 'house':2929387})
		>>> other_numbers.setAttr('office',{'from': 9, 'to':17})
		>>> john_doe['telephones']=john_doe['telephones'].merge(other_numbers)
		>>> print john_doe
		0 - (Bag) telephones:
		    0 - (int) house: 2929387
		    1 - (int) mobile: 444334523
		    2 - (int) office: 3320924  <to='17' from='9'>
		>>> john_doe['credit_cards']=Bag()

	.. method:: pop(path)
	
		Remove the first value included in the path, and return it.
		
		>>> b = Bag()
		>>> b.setItem('a',1)
		>>> b.addItem('a',2)
		>>> b.addItem('a',3)
		>>> b.pop('a')
		1
		>>> print b
		0 - (int) a: 2
		1 - (int) a: 3

	.. method:: setAttr(path,attribute[,attributes])
	
		Allow to set, modify or delete attributes. The attributes are passed as ``**kwargs``.

			>>> b = Bag()
			>>> b.setAttr('documents.letters.letter_to_sheila', createdOn='12-4-2003', createdBy='Walter', lastModify= '12-9-2003')
			>>> b.setAttr('documents.letters.letter_to_sheila', fileOwner='Steve')
			>>> print b
			0 - (Bag) documents: 
			    0 - (Bag) letters: 
			        0 - (str) letter_to_mark: file0  <createdOn='10-7-2003' createdBy='Jack'>
			        1 - (str) letter_to_john: file1  <lastModify='11-9-2003' createdOn='11-5-2003' createdBy='Mark'>
			        2 - (str) letter_to_sheila: file2  <lastModify='12-9-2003' createdOn='12-4-2003' fileOwner='Steve' createdBy='Walter'>

		You may delete an attribute assigning ``None`` to an existing value:

		>>> b.setAttr('documents.letters.letter_to_sheila', fileOwner=None)
		>>> print b
		0 - (Bag) documents:
		    0 - (Bag) letters:
		        0 - (str) letter_to_sheila: file2  <lastModify='12-9-2003' createdOn='12-4-2003' createdBy='Walter'>

	.. method:: setItem(path,value[,_position=expression])

		Add values (or attributes) to your Bag. The default behaviour of ``setItem`` is to add the new value as the last element of a list. You can change this trend with the _position argument, who provides a compact syntax to insert any item in the desired place.
		
		* `_position`: with this optional argument it is possible to set a new value at a particular position among its brothers. *expression* must be a string of the following types:

			+----------------------------+----------------------------------------------------------------------+
			| *Expressions*              |  Description                                                         |
			+============================+======================================================================+
			| ``'<'``                    | Set the value as the first value of the Bag                          |
			+----------------------------+----------------------------------------------------------------------+
			| ``'>'``                    | Set the value as the last value of the Bag                           |
			+----------------------------+----------------------------------------------------------------------+
			| ``'<label'``               | Set the value in the previous position respect to the labelled one   |
			+----------------------------+----------------------------------------------------------------------+
			| ``'>label'``               | Set the value in the position next to the labelled one               |
			+----------------------------+----------------------------------------------------------------------+
			| ``'<#index'``              | Set the value in the previous position respect to the indexed one    |
			+----------------------------+----------------------------------------------------------------------+
			| ``'>#index'``              | Set the value in the position next to the indexed one                |
			+----------------------------+----------------------------------------------------------------------+
			| ``'#index'``               | Set the value in a determined position indicated by ``index`` number |
			+----------------------------+----------------------------------------------------------------------+
		
		Example::
		
			>>> mybag = Bag()
			>>> mybag.setItem('a',1)
			>>> mybag.setItem('b',2)
			>>> mybag.setItem('c',3)
			>>> mybag.setItem('d',4)
			>>> mybag.setItem('e',5, _position= '<')
			>>> mybag.setItem('f',6, _position= '<c')
			>>> mybag.setItem('g',7, _position= '<#3')
			>>> print mybag
			0 - (int) e: 5
			1 - (int) a: 1
			2 - (int) b: 2
			3 - (int) g: 7
			4 - (int) f: 6
			5 - (int) c: 3
			6 - (int) d: 4
		
		**Square-brackets notations:**
		
		``Bag[path] = value``:
		
		>>> mybag = Bag()
		>>> mybag['a'] = 1
		>>> mybag['b.c.d'] = 2
		>>> print mybag
		0 - (int) a: 1
		1 - (Bag) b:
		    0 - (Bag) c:
		        0 - (int) d: 2
		
		.. note:: if you have to use the ``_position`` attribute you can't use the square-brackets notation.
	
	.. method:: setdefault(self, path, default=None)
	
		If *path* is in the Bag, return its value. If not, insert key in the *path* with a value of default and return default. default defaults to None.
	
	.. method:: toTree(self, group_by, caption=None, attributes="*")
	
		It transforms a flat Bag into a hierarchical Bag and returns it.
		
		* `group_by`: list of keys.
		
		* `caption`: the attribute to use for the leaf key. If not specified, it uses the original key.
		
		* `attributes`: keys to copy as attributes of the leaves. (default: `'*'` = select all the attributes)
		
	.. method:: update(other)

		Update the Bag with the ``key/value`` pairs from *other*, overwriting existing keys. Return ``None``.

	.. method:: values()

		Return a copy of the Bag values as a list.
