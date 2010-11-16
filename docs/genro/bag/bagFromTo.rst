	.. _bag-from-to:

Bag from/to source
==================

	- :ref:`bag_from_to_XML`:
	
		- :ref:`bag-to-xml`
		
		- :ref:`XML`
	
	- :ref:`from_bag_to_dict`

	As we have seen in the previous chapter, a Bag is a completely dynamic structure. A Bag has a polymorphic interaction with many complex data sources, so it's possible to fill it passing:

	- A string representing an XML_ section.
	
	- A file path of an XML file.
	
	- An URI of a remote XML file.
	
	- A file path of a directory on local disk.
	
	- A pickle file.
	
	- Another Bag.
	
	- A dict_
	
	>>> fromlocal = Bag('%s/test_files/standardxml.xml' %current)
	>>> fromurl = Bag('http://www.plone.org')
	>>> fromdirectory = Bag('%s/test_files' %current)
	>>> stringxml = '<?xml version="1.02" encoding="UTF-8"?><a><b name="fuffy"><d>dog</d></b><c/></a>'
	>>> fromstringxml = Bag(stringxml)

	.. image:: ../images/bag/bag-trigger5.png

	A bag can also be serialized into different formats:

	- XML
	- pickle
	- JSON
	- etc.

	.. image:: ../images/bag/bag-serialized.png

.. _bag_from_to_XML:

Bag from/to XML
===============

	.. _bag-to-xml:

toXml
=====

	A Bag can be exported to an XML source with the `gnr.core.gnrbag.Bag.toXml` method. This method returns a text, that is a complete standard XML version of the Bag, including the encoding tag <?xml version=\'1.0\' encoding=\'UTF-8\'?>. Since an XML document needs an unique root node, the method creates as outer level a node called <GenRoBag>. Each Bag becomes an XML block that contains other XML elements.

	+--------------------+---------------------+
	|    Bag's item      |   XML element       |
	+====================+=====================+
	|   `label`          | `tag`               |
	+--------------------+---------------------+
	|   `value`          | `element's content` |
	+--------------------+---------------------+
	|   `attributes`     | `attributes`        |
	+--------------------+---------------------+

	the `gnr.core.gnrbag.Bag.toXml` method may receive two optional parameters:

	- `filename`: the path of the output file. If filename is passed, the method returns None, and creates the file at the correct position.
encoding is used to set the XML encoding (default value is UTF-8).
	
	- `???otherParam!`:
	
	XML is a very common instrument to transport data, but transforming any datastructure into XML doument makes you loss the data types. This does't happen with the method toXml(). The method adds for each XML element a special attribute called '_T' that represents a code of the original type of item's value, unless the original type was string.

	>>> mybag= Bag()
	>>> mybag['birthday']=datetime.date(1974,11,23)
	>>> mybag['height']=1.76
	>>> mybag['weight']=65
	>>> xml_source=mybag.toXml()
	>>> print xml_source
	<?xml version='1.0' encoding='UTF-8'?>
		<GenRoBag>
			<height _T="R">1.76</height>
			<weight _T="L">65</weight>
		</GenRoBag>

	Here is a table that show the keywords used to represents data types:

	+--------------------+---------------------+
	|    Codes           |   Data type         |
	+====================+=====================+
	|   `T`              | `txt`               |
	+--------------------+---------------------+
	|   `R`              | `float`             |
	+--------------------+---------------------+
	|   `L`              | `int`               |
	+--------------------+---------------------+
	|   `B`              | `bool`              |
	+--------------------+---------------------+
	|   `D`              | `datetime`          |
	+--------------------+---------------------+
	|   `DT`             | `datetime` ???      |
	+--------------------+---------------------+
	|   `H`              | `datetime.time`     |
	+--------------------+---------------------+

	Also attributes' types aren't lost during the transformation, in fact in the value of each attribute is added a substring composed by '::type', unless it's original type was string.

	>>> mybag.setAttr('height',lastMeasure=datetime.date(2006,10,3))
	>>> xml_source = mybag.toXml()
	>>> print xml_source
	<?xml version='1.0' encoding='UTF-8'?>
		<GenRoBag>
			<birthday _T="D">1974-11-23</birthday>
			<height _T="R" lastMeasure="2006-10-03::D">1.76</height>
			<weight _T="L">65</weight>
		</GenRoBag>

.. _XML:

from XML
========

	If the Bag's constuctor receives as parameter source a filepath, an URL or a string that contains XML source, it creates a Bag that represents the XML document. If the XML source provides type indication, such as _T attribute or ::Type suffix, bag's values and attributes will have the correct type.

	>>> xmlbag=Bag(xml_source)
	>>> print xmlbag
	0 - (date) birthday: 1974-11-23
	1 - (float) height: 1.76  <lastMeasure='2006-10-03::D'>
	2 - (int) weight: 65

.. _dict:

.. _from_bag_to_dict:

Trasform a Bag into a dict
==========================

	A bag can be transformed into a dict with the :meth:`gnr.core.gnrbag.Bag.asDict` method:

		>>> mybag=Bag({'a':1,'b':2,'c':3,'d':4})
		>>> print mybag
		0 - (int) a: 1
		1 - (int) c: 3
		2 - (int) b: 2
		3 - (int) d: 4
		>>> d = mybag.asDict()
		>>> print d
		{'a': 1, 'c': 3, 'b': 2, 'd': 4}