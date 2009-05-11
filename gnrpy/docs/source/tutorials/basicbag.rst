######################
  About Bag
######################

Hello Bag
=========

Bag is a multi-purpose datastructure, that is ideal for storing and retrieving
any kind of complex data '' tidily and deeply '': Any value inserted into a
bag has its own position at the appropriate hierarchical level.

There are two logical modes for thinking about how data is stored in a bag.

* As a ''flat'' container
* As a ''hierachical'' container

These can be termed, ''in breadth'' for flat and ''in depth'' for hierarchical.

Bag, used as a simple flat container has some similarities with both
Dictionary and List, but also several important differences. However, bags are
far more powerful and complicated, first of all because of their hierarchical
nature.

A bag may be defined as an ordered container of couples composed by a
''label'' and a ''value''. A bag's value can be a bag itself and so on. This
fact makes Bag a recursive and hierarchical container. Each bag may access
directly to its inner elements using a path composed by a concatenation of
traversed bags' labels.

Instantiate a Bag
*****************

To instantiate a bag you simply call its constructor Bag.
The constructor may receive several kinds of initialization params.
If nothing is passed it creates an empty bag.

::

>>> from gnr.core.gnrbag import Bag
>>> mybag = Bag()



It also may receive a list  of tuples or a dict.

::

>>> mybag = Bag([('a',1),('b',2)])
>>> mybag = Bag({'a': 1, 'b':2})

A Bag may also be created starting from XML files, URL or file-system path,
but this will be explained in the session Importing and exporting bags.

::

>>> mybag = Bag('/data/myfile.xml')
>>> mybag = Bag('http://www.foo.com')




Setting and getting items
*************************
You can read/write a bag's item using the methods *getItem(path)*,
*setItem(path,value)*. When considering flat bags, the path is called a
*label* and represent the item's identifier among the bag's children.


::

>>> mybag = Bag()
>>> mybag.setItem('a',1)
>>> first = mybag.getItem('a')


A more compact way to access a bag's items is the square-brackets notation,
which is a typical feature of dictionaries.

::

>>> mybag['b']=2
>>> second = mybag['b']


Flat bags VS lists and dictionaries
===================================


It is evident that there are several analogies between a bag's ''label'' and
dictionary ''key'', but there are also some fundamental differences.

 * A bag's label must be a string: numbers or complex types are not valid labels.
 * Unlike dictionaries, whose keys must be unique, bags can have different items tagged with the same label. 
 * If you try to get an item that is not present within the bag, you get '' None '' not an exception.

 
Duplicated labels
*****************

It is possible to insert different values with the same label, but in order to
do this you have to use the method *addItem(label,value)* because
*setItem(label,value)* would set a new value on the existing item.

::

>>> beatles= Bag()
>>> beatles.setItem('member', 'John')
>>> beatles.addItem('member', 'Paul')
>>> beatles.addItem('member', 'George')
>>> beatles.addItem('member', 'Ringo')


Accessing to items by index
***************************

A bag is an ordered container, in fact a Bag remembers the order of insertion
of its children. This makes a Bag similar to a list, allowing it to get its
items with a numeric index that represents an element's position. If you want
to access data by its position, you have to use a particular label composed by
''#'' followed by the item's ''index''.

::

>>> first = mybag.getItem('#1')
>>> second = mybag['#2']


This feature is very useful when a bag has several items with the same label,
because the method ''getItem(label)'' returns only the first item tagged with
the argument ''label''. This means that the only way to access items with a
duplicated label is by index.

::

>>> lennon = beatles.getItem('member')
>>> lennon = beatles.getItem('#0')
>>> mccartney = beatles.getItem('#1')
>>> harrison = beatles['#2']


If you need to know the ordinal position of an item you can use the method
''index(label)''. But remember that unlike a list's ''index'' method, returns
the element position using its label and not its value. A bag's label can be
duplicated and in this case the method ''index(label)'' returns the position
of the first occurrence of the label.

::

>>> n = beatles.index('member')
>>> lennon = beatles['#%i' %n']


Setting item's position
***********************

It is possible to set a new item at a particular position among its brothers,
using the optional argument ''_position'' of the method
*setItem(label,value)* The default behaviour of setItem is to add the new
item as the last element of a list, but the *_position* argument provides a
compact syntax to insert any item at it's desired place. *_position* must be
a string of the following types:

||'<' || set as first item ||
|| '<label' || set before the element with label||
|| '<#index '|| set before the element with index||
||'>' || set as last item ||
|| '>label' || set after the element with label||
|| '>#index '|| set after the element with index||
|| '#index'|| set at position||


{{{
mybag=Bag({'a':1,'b':2,'c':3,'d':4})
mybag.setItem('e',5, _position= '<')
mybag.setItem('f',6, _position= '<c')
mybag.setItem('g',7, _position= '<#3')
}}}



=== Dictionary methods implemented by Bag ===

 * bag.keys()
 * bag.items()
 * bag.values()
 * bag.has_key()
 * bag.update()

=== List methods implemented by Bag ===

 * index()
 * pop()

=== The operator 'in' ===
Bag also supports the operator ''in'' exactly like a dictionary.

{{{
>>>'a' in mybag
True
}}}

=== How to transform a flat bag in a dictionary ===

A bag can be transformed into a dict with the method ''asDict()''

{{{
d=b.asDict()
}}}

If you attempt to transform a hierarchical bag to a dictionary, the resulting dictionary will contain nested bags as values. In other words only the first level of the Bag is transformed to a dictionary, the transformation is not recursive.



----

== Printing a bag ==

If you want to display a bag in your python shell you can use the built-in function ''print''.
If you need a bag's representation as a string use the method ''asString''


{{{
>>> print mybag

0 - (int) e: 5  
1 - (int) a: 1  
2 - (int) g: 7  
3 - (int) f: 6  
4 - (int) c: 3  
5 - (int) b: 2  
6 - (int) d: 4

>>> mystring= mybag.asString()
>>> mystring

0 - (int) e: 5  
1 - (int) a: 1  
2 - (int) g: 7  
3 - (int) f: 6  
4 - (int) c: 3  
5 - (int) b: 2  
6 - (int) d: 4

}}}

Bag representation makes a line for each item.  The line is structured:

||item's index||item's type||label||value||

== Bag as a hierarchical container ==

If a bag contains other bags, the outer one is a Hierarchical Bag. 

In the previous paragraphs we saw how a bag works ''in breadth''. Now we'll see how they can be used to store data ''in depth''.

Bags aren't just another traversable tree structure. In fact a Bag supports direct access to any value contained in any of the nested bags, using a complex ''path''.  This means that a bag ''contains'' not only its children but also its descendants.



=== Bag's path ===
We call ''path'' a concatenation of nested bags' labels that ends always with the innermost item's label. The separator character of a path is dot. Remember that if you need to use labels that include dot char, but you didn't want them to be interpreted as part of a complex path, you have to escape the dot char with a backslash.


{{{
1    new_card= Bag()
2    new_card['name']='John'
3    new_card.setItem('surname','Doe')
4    new_card['phone']= Bag()
5    new_card['phone'].setItem('office',555450210)
6    new_card.setItem('phone.home',555345670)
7    new_card.setItem('phone.mobile', 555230450) 
8    address_book=Bag()
9    address_book.setItem('friends.johnny', new_card)
10   john_mobile= address_book.getItem('friends.johnny.phone.mobile')

>>> print john_mobile

555230450

}}}

Let's examine the ''address_book'' example:
We instantiate a bag called ''new_card'' and we set three items: ''name'', ''surname'' and ''phone''.  
From the above example, we can set an item in  bag by using two different syntax: a. the square-brackets notation, or b. the 'setitem' notation. 
The item ''phone'' is a bag and we fill it with three new values: ''mobile'', ''home'', ''office''. There is a formal difference between line 5 and line 6. In line 5, we set ''office'' as child of ''phone'', calling the method setItem from the instance labelled as ''phone''. 
In line 6 we instead set ''home'' directly from the bag ''new_card'' as its nephew, using the ''path'' 'phone.home'.

Even if the instance which sets the item is different, the result is identical. Both items are set at the same level and we can consider them either as children of "phone" or as nested content of ''new_card''.

A hierarchical bag as ''new_card'' can be nested within a larger one. In line 9 we set it into the bag ''friends'' that is inside the bag ''address_book''.
Now you might be thinking that the bag "friends" was not intantiated and that it was not set into ''address_book''.  When the method setItem receives the path 'friends.johnny', the bags in the middle are also created, if they don't exist.

This feature is very useful to quickly create many nested bags with just a single command.

{{{
mybag=Bag()
mybag.setItem('a.b.c.d.e.f.g', 7)
print mybag['a.b.c.d.e.f.g']
>>> 7
}}}

Print function displays nested bags with indented blocks.
{{{
>>>print address_book

0 - (Bag) friends: 
    0 - (Bag) johnny: 
        0 - (str) name: John  
        1 - (str) surname: Doe  
        2 - (Bag) phone: 
            0 - (int) office: 555450210  
            1 - (int) home: 555345670  
            2 - (int) mobile: 555230450  
}}}


In the previous chapter we saw that we can access an item using a numeric label ''#index''. A bag can be traversed using a path that includes either common labels or a numeric label.

{{{
print address_book['friends.johnny.#2.office']
>>> 555450210
}}}



----


== Bag's attributes ==

You can attach metadatas to any item of  Bag. These metadatas are called ''attributes'' . Each attribute has a ''name'' and a ''value''. Attributes are stored in a dictionary.


=== Setting attributes with setItem ===
You can set attributes while you set an item, passing them as ''**kwargs'' of the method ''setItem''.

{{{
b=Bag()
b.setItem('documents.letters.letter_to_mark', 'file0', createdOn='10-7-2003', createdBy= 'Jack')
b.setItem('documents.letters.letter_to_john', 'file1', createdOn='11-5-2003', createdBy='Mark', lastModify= '11-9-2003')
b.setItem('documents.letters.letter_to_sheila', 'file2')
}}}

=== Setting attributes with setAttr ===
You can set attributes and change their value with the method ''setAttr(path, attributes)''. Attributes are passed as **kwargs.

{{{
b.setAttr('documents.letters.letter_to_sheila', createdOn='12-4-2003', createdBy='Walter', lastModify= '12-9-2003')
b.setAttr('documents.letters.letter_to_sheila', fileOwneer='Steve')

>>> print b
0 - (Bag) documents: 
    0 - (Bag) letters: 
        0 - (int) letter_to_mark: Bag({'file':'file0'})  <createdOn='10-7-2003' createdBy= 'Jack'>
        1 - (int) letter_to_john: Bag({'file':'file1'})  <lastModify='11-9-2003' createdOn='11-5-2003' createdBy='Mark'>
        2 - (int) letter_to_sheila: Bag({'file':'file2'})'  <lastModify='12-9-2003' createdOn='12-4-2003' createdBy='Walter' _attributes='{'fileOwneer': 'Steve'}'>

}}}

=== Getting attributes ===

To get a single item's attributes, there is the method ''getAttr(path, attr)''.
{{{
>>> print b.getAttr('documents.letters.letter_to_sheila', 'fileOwneer')
'Steve'
}}}

There is also a compact square-brackets notation for ''getAttr(path, attr)''.  It uses special char '?' followed by 'a:' and the attribute's name
Let's examine the previous example using the compact syntax:

{{{
>>> print b['documents.letters.letter_to_sheila?a:fileOwner']
'Steve'
}}}

=== Deleting attributes ===

You may delete an attribute by setting 'None' as it's ''value''

=== Digest method ===

A Bag implements a very useful method called ''digest'' that returns a list of tuples, one for each bag's item. These tuples contains the ''columns'' requested by the parameter ''what'', which is a comma separated string of special keys.

||#k|| show the label of each item||
||#v|| show the value of each item||
||#v.path||show inner values of each item||
||#a|| show attributes of each item||
||#a.attrname|| show the attribute called 'attrname' for each item||

{{{
>>> print b['documents.letters'].digest('#k,#a.createdOn,#a.createdBy')
[('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark'), ('letter_to_sheila', '12-4-2003', 'Walter')]
}}}

In this example we requested the ''label'' and the attributes ''fileOwner'', ''createdOn''.
There is a square-brackets notation also for the method ''digest''. This syntax uses the special char "?" followed by "d:" and then the parameter ''what''.

{{{
>>> print b['documents.letters.?d:#k,#a.createdOn,#a.createdBy']
[('letter_to_mark', '10-7-2003', 'Jack'), ('letter_to_john', '11-5-2003', 'Mark'), ('letter_to_sheila', '12-4-2003', 'Walter')]

>>> print b['documents.letters.?d:#v, #a.createdOn']
[('file0', '10-7-2003'), ('file1', '11-5-2003'), ('file2', '12-4-2003')]
}}}



=== Attributes in path ===

We said that a path, can be formed either by ''labels'' or ''#index''. There is a third way to identify a bag item by specifying a condition on any of its attributes where the attribute value is of type ''string''.
For example, the item with label ''letter_to_mark'' can be identified by the attribute condition "the file created by Jack". Therefore, instead of using a label, or a numeric index of position in a ''path'', we could alternatively insert a condition on an attribute. The syntax for testing a condition on an attribute within a path is: 

{{{
#''attribute_name''=''value''
}}}

If the attribute tested is called ''id'', the attribute's name can be omitted. Remember that this syntax works only if the tested attribute has a value of type ''string''.

{{{
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

}}}

In this example we identify two uses of path that includes conditions on an item's attributes: 
 * ''getItem('genres.fantasy.#author=Tolkien')''
 * ''getAttr('genres.fantasy.#=f123', 'title')''



----


== Bag merge and update ==

=== merge ===
You can merge two bags into one using the method ''merge()''

''merge()'' has four optional parameters:



||''flag''||''default''||

||upd_values|| True||

||add_values|| True||

||upd_attr|| True||

||add_attr|| True||


{{{

john_doe=Bag()

john_doe['telephones']=Bag()

john_doe['telephones.house']=55523412

other_numbers=Bag({'mobile':444334523, 'office':3320924, 'house':2929387})

other_numbers.setAttr('office',{'from': 9, 'to':17})

john_doe['telephones']=john_doe['telephones'].merge(other_numbers)



>>> print john_doe

0 - (Bag) telephones: 

    0 - (int) house: 2929387  

    1 - (int) mobile: 444334523  

    2 - (int) office: 3320924  <to='17' from='9'>



john_doe['credit_cards']=Bag()

}}}


As you can see, since I did't set any of the flag parameters to False merge added twe new values (mobile, office), updated a value (house) and added two attributes.


=== update ===


The method update is similar to dictionary's update. It receives an update bag that overrides completely the starting bag. The method adds new elements, changes values and attributes at all levels recursively.


----

== Bag Node ==

We discovered in the previous chapter that we can associate a set of ''attributes'' to each item.
We will now discuss a more advanced concept about Bag, where we introduce the !BagNode.
Until now we considered the hierachical Bag as a chain of bags within bags. That is not exactly true, because each bag's element is
a !BagNode.

A '!BagNode' is an object composed of three parts: 

 * ''label''
 * ''attributes'' 
 * ''value'' (or item) 

In order to avoid confusion between the terms ''item'' and ''node'', what we used to call an 'item' we will now call a ''value''.

[[Image(bagnode.jpg)]]    

If you need to work with nodes, you may get them with the methods:
||''getNode(path)''|| returns a node||
||''getNodes()''||returns a list of nodes||
||''getNodeByAttr(attribute, attr_value)''|| returns the node that has the passed couple attribute-value||


{{{
mybag = Bag({'paper':1, 'scissors':2})
papernode = mybag.getNode('paper')
mybag.setItem('rock', 3 , color='grey')
rocknode=mybag.getNodeByAttr('color','grey')
nodes=mybag.getNodes()
}}}

The method getNodes() implements the bag's property ''nodes''.

{{{

>>>mybag.getNodes() == mybag.nodes
True

}}}

If you have a ''node'' instance you may use one of the following methods:

 ||''hasAttr(attribute)''||returns true if the node has a value for the passed attribute||
 ||''setAttr(attribute=value)''||set to the node one or more attributes passed as kwargs||
 ||''getAttr(attribute)''||returns the attribute's value||
 ||''replaceAttr(attribute=value)''||replaces the value of one or more attributes passed as kwargs||
 ||''delAttr(attribute)''||deletes the attribute with the passed name||
 ||''getLabel()''||returns the node's label||
 ||''setLabel(label)''||sets the node's label|| 
 ||''getValue()''||returns the node's value||
 ||''setValue()''||sets the node's value||


{{{

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
}}}


