.. _bag_attributes:

============
 attributes
============

	* :ref:`bag_attributes_setItem`
	* :ref:`bag_attributes_setAttr`
	* :ref:`bag_getting_attributes`
	* :ref:`bag_conditions`

	.. module:: gnr.core.gnrbag.Bag

	You can attach metadatas to any node of a Bag. Let's introduce the attributes: each attribute has a name and a value and they are stored in a dictionary.

.. _bag_attributes_setItem:

Setting attributes with setItem method
======================================

	You can set attributes while you set an item, passing them as ``**kwargs`` of the :meth:`setItem` method.

	>>> b=Bag()
	>>> b.setItem('documents.letters.letter_to_mark','file0',createdOn='10-7-2003',createdBy= 'Jack')
	>>> b.setItem('documents.letters.letter_to_john','file1',createdOn='11-5-2003',createdBy='Mark',lastModify='11-9-2003')
	>>> b.setItem('documents.letters.letter_to_sheila','file2')
	>>> print b
	0 - (Bag) documents: 
	    0 - (Bag) letters: 
	        0 - (str) letter_to_mark: file0  <createdOn='10-7-2003' createdBy='Jack'>
	        1 - (str) letter_to_john: file1  <lastModify='11-9-2003' createdOn='11-5-2003' createdBy='Mark'>
	        2 - (str) letter_to_sheila: file2

.. _bag_attributes_setAttr:

Setting attributes with setAttr method
======================================

	With :meth:`setAttr` method you can set, modify or delete attributes. The attributes are passed as ``**kwargs``; let's add some attributes to the letter to Sheila (the Bag item labelled "2"):

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

.. _bag_getting_attributes:

Getting attributes
==================

	To get a single Bag's attribute you can use the :meth:`getAttr` method:

	>>> print b.getAttr('documents.letters.letter_to_sheila', 'fileOwner')
	Steve
	
	**Square-brackets notations:** you have to use the special char ``?`` followed by the attribute's name:

	>>> print b['documents.letters.letter_to_sheila?fileOwner']
	Steve

.. _bag_conditions:

Attributes in a path: insert a condition
========================================

	If the attribute value is a string type, there is another way [#]_ to identify a step of a bag path: by specifying a condition on any of its attributes.
	
	The syntax for testing a condition on an attribute within a path is: ``#attributeName=value``. Let's check an example:

	>>> bookcase = Bag()
	>>> mybook=Bag()
	>>> mybook.setItem('part1',Bag(),title='The fellowship of the ring',pages=213)
	>>> mybook.setItem('part2',Bag(),title='The two towers',pages=221)
	>>> mybook.setItem('part3',Bag(),title='The return of the king',pages=242)
	>>> bookcase.setItem('genres.fantasy.LOTR',mybook,title='the Lord Of The Rings',id='f123',author='Tolkien')
	
	If we print now our bookcase, we'll get this:
	
	>>> print bookcase
	0 - (Bag) genres: 
	    0 - (Bag) fantasy: 
	        0 - (Bag) LOTR: <author='Tolkien' id='f123' title='the Lord Of The Rings'>
	            0 - (Bag) part1: <pages='213' title='The fellowship of the ring'>
	            1 - (Bag) part2: <pages='221' title='The two towers'>
	            2 - (Bag) part3: <pages='242' title='The return of the king'>
	
	Now, if we want to get the information of the LOTR Bag, we can use one of the these following lines::
	
		>>> print bookcase.getItem('genres.fantasy.#author=Tolkien')
		>>> print bookcase.getItem('genres.fantasy.LOTR')
		>>> print bookcase.getItem('genres.fantasy.#=f123')

	The result will be always the same::

		0 - (Bag) part1: <pages='213' title='The fellowship of the ring'>
		1 - (Bag) part2: <pages='221' title='The two towers'>
		2 - (Bag) part3: <pages='242' title='The return of the king'>
	
	You can omit the attribute's name if the attribute is called ``id``, but remember that this syntax works only if the attribute has a value of type string:
	
	>>> print bookcase.getAttr('genres.fantasy.#=f123', 'title')
	the Lord Of The Rings

**Footnotes:**

.. [#] The other two ways are: labels (check the :ref:`genro_bag_one` introduction paragraph) and numeric index ``#index`` (check the :ref:`bag_getting_values_advanced` paragraph). 
