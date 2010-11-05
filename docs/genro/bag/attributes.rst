	.. _bag-attributes:

============
 attributes
============

	You can attach metadatas to any node of a Bag. These metadatas are called attributes. Each attribute has a name and a value. Attributes are stored in a dictionary.

	Setting attributes with setItem

	You can set attributes while you set an item, passing them as **kwargs of the method setItem.

	b=Bag()
	b.setItem('documents.letters.letter_to_mark', 'file0', createdOn='10-7-2003', createdBy= 'Jack')
	b.setItem('documents.letters.letter_to_john', 'file1', createdOn='11-5-2003', createdBy='Mark', lastModify= '11-9-2003')
	b.setItem('documents.letters.letter_to_sheila', 'file2')
	Setting attributes with setAttr

	You can set attributes and change their value with the method setAttr(path, attributes). Attributes are passed as **kwargs.

	b.setAttr('documents.letters.letter_to_sheila', createdOn='12-4-2003', createdBy='Walter', lastModify= '12-9-2003')
	b.setAttr('documents.letters.letter_to_sheila', fileOwneer='Steve')

	>>> print b
	0 - (Bag) documents: 
	    0 - (Bag) letters: 
	        0 - (int) letter_to_mark: Bag({'file':'file0'})  <createdOn='10-7-2003' createdBy= 'Jack'>
	        1 - (int) letter_to_john: Bag({'file':'file1'})  <lastModify='11-9-2003' createdOn='11-5-2003' createdBy='Mark'>
	        2 - (int) letter_to_sheila: Bag({'file':'file2'})'  <lastModify='12-9-2003' createdOn='12-4-2003' createdBy='Walter' _attributes='{'fileOwneer': 'Steve'}'>

	Getting attributes

	To get a single item's attributes, there is the method getAttr(path, attr).

	>>> print b.getAttr('documents.letters.letter_to_sheila', 'fileOwneer')
	'Steve'
	There is also a compact square-brackets notation for getAttr(path, attr). It uses special char '?' followed by 'a:' and the attribute's name Let's examine the previous example using the compact syntax:

	>>> print b['documents.letters.letter_to_sheila?a:fileOwner']
	'Steve'
	Deleting attributes

	You may delete an attribute by setting 'None' as it's value

	Digest method

	A Bag implements a very useful method called digest that returns a list of tuples, one for each bag's item. These tuples contains the columns requested by the parameter what, which is a comma separated string of special keys.

	#k	 show the label of each item
	#v	 show the value of each item
	#v.path	show inner values of each item
	#a	 show attributes of each item
	#a.attrname	 show the attribute called 'attrname' for each item
	>>> print b['documents.letters'].digest('#k,#a.createdOn,#a.createdBy')
	[('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark'), ('letter_to_sheila', '12-4-2003', 'Walter')]
	In this example we requested the label and the attributes fileOwner, createdOn. There is a square-brackets notation also for the method digest. This syntax uses the special char "?" followed by "d:" and then the parameter what.

	>>> print b['documents.letters.?d:#k,#a.createdOn,#a.createdBy']
	[('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark'), ('letter_to_sheila', '12-4-2003', 'Walter')]

	>>> print b['documents.letters.?d:#v, #a.createdOn']
	[('file0', '10-7-2003'), ('file1', '11-5-2003'), ('file2', '12-4-2003')]
	Attributes in path

	We said that a path, can be formed either by labels or #index. There is a third way to identify a bag item by specifying a condition on any of its attributes where the attribute value is of type string. For example, the item with label letter_to_mark can be identified by the attribute condition "the file created by Jack". Therefore, instead of using a label, or a numeric index of position in a path, we could alternatively insert a condition on an attribute. The syntax for testing a condition on an attribute within a path is:

	#''attribute_name''=''value''
	If the attribute tested is called id, the attribute's name can be omitted. Remember that this syntax works only if the tested attribute has a value of type string.

	bookcase = Bag()
	mybook=Bag()
	mybook.setItem('part1', Bag(),title='The fellowship of the ring', pages=213)
	mybook.setItem('part2', Bag(), title='The two towers', pages=221)
	mybook.setItem('part3', Bag(), title='The return of the king', pages=242)
	bookcase.setItem('genres.fantasy.LRDRNGS', mybook , title='The lord of the rings',id='f123', author='Tolkien')

	>>> print bookcase.getItem('genres.fantasy.#author=Tolkien')

	0 - (Bag) part1: <pages='213' title='The fellowship of the ring'>

	1 - (Bag) part2: <pages='221' title='The two towers'>

	2 - (Bag) part3: <pages='242' title='The return of the king'>

	>>> print bookcase.getAttr('genres.fantasy.#=f123', 'title')
	'The lord of the rings'

	In this example we identify two uses of path that includes conditions on an item's attributes:

	getItem('genres.fantasy.#author=Tolkien')
	getAttr('genres.fantasy.#=f123', 'title')
	
