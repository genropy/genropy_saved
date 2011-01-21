.. _genro_bag_four:

.. module:: gnr.core.gnrbag.Bag

=========================
Resolver and dynamic bags
=========================

	* :ref:`bag_four_introduction`
	* :ref:`bag_resolver`
	* :ref:`bag_resolver_example1`
	* :ref:`bag_resolver_example2`
	* :ref:`bag_resolver_example3`
	* :ref:`bag_shortcuts`
	* :ref:`bag_formula`
	* :ref:`bag_symbol_formula`

.. _bag_four_introduction:

Introduction
============

	A Bag item can be something more than a static value.
	
	**dynamic item:** an item that is able to call a function that get a value or a cached copy of it making a call.
	
	A Bag can be a dynamic item, and we call it a **dynamic Bag**.
	
	Some possible usages for a dynamic Bag are:
	
	* get values from a database server.
	* get values from webservices.
	* calculate values in real-time.
	* etc.
	
	.. image:: ../images/bag/bag-resolver.png

.. _bag_resolver:

resolver
========

	The basic idea of a dynamic Bag is to hide all the function calls treating their results as they were Bag static items (so, a likely-static value can be the result of a realtime elaboration or a remote call). The BagResolver class (:class:`gnr.core.gnrbag.BagResolver`) is an interface that allow to define objects that implement this process.

	A resolver overrides the primitive ``__call__``, which is the one that intercepts any round-brackets call and implements the load() method. When a resolver is called my_resolver(), it calls its load() method. A resolver may have a cache, if the cacheTime is specified in the args, else it's considered 0. The cache stores the retrieved value and keeps it for a lapse of time called cacheTime. Each resolver implements the load() method that reads the result from cache, if cacheTime isn't elapsed, or takes it from its remote source. The my_resolver call can receive some kwargs. A resolver is set in a node by the :meth:`setResolver` method.

.. _bag_resolver_example1:

Resolver Example 1: the TimeResolver
====================================

	There are several ways to create a Bag with an item that returns the current time. Let's define the TimeResolver class that inherits from BagResolver::

		from datetime import datetime
		from gnr.core.gnrbag import Bag, BagResolver
		
		class TimeResolver(BagResolver):
			def __call__(self):
				return datetime.now()
    
	If you define a BagResolver subclass it requires the reimplementation of the ``__call__()`` function.
	
	We can now set a TimeResolver instance:
	
	>>> mybag = Bag()
	>>> mybag['now'] = TimeResolver()
	>>> print mybag['now']
	2010-11-18 11:47:13.237443
	
	If we want to automate the call we have to introduce a cacheTime value:
	
	The mybag['now'] value will be updated every 100 ms:
	
	>>> ct=100
	>>> mybag['now']=TimeResolver(cacheTime=ct)
	>>> print mybag['now']
	2010-11-18 11:49:34.257631
	
.. _bag_resolver_example2:
	
Resolver Example 2: UserInfoResolver
====================================

	The following example defines a resolver who prepares a Bag containing some information about the computer (e.g. hostname, IP, PID, user)::
	
		from gnr.core.gnrbag import Bag, BagResolver
		import socket, os
		
		class UserInfoResolver(BagResolver):
			def load(self):
				result = Bag()
				try:
					result['hostname']=socket.gethostname()
					result['ip']=socket.gethostbyname(result['hostname'])
				except:
					result['hostname']='localhost'
					result['ip']='unknown'
				result['pid']=os.getpid()
				result['user']=os.getenv('USER')
				result['ID']=result['ip']+'-'+str(result['pid'])+'-'+result['user']
				return result
		
	Here is how the resolver works:

	>>> mybag = Bag()
	>>> mybag['info'] = UserInfoResolver()
	>>> info = mybag['info']
	>>> template = "This is the process %s.\nYou are user %s, from the host %s at the address %s"
	>>> print template %(mybag['info.pid'], mybag['info.user'], mybag['info.hostname'], mybag['info.ip'])
	This is the process 7296. 
	You are user foo_user, from the host ikid.local at the address 192.168.1.53

.. _bag_resolver_example3:

Resolver Example 3: RssFeedResolver
===================================

	The resolver receives an URL of a RSS feed of the web, and since a Bag can be created starting from an XML it's very easy to set some news in a Bag::

		class RssFeedResolver(BagResolver):
			def init(self, feed):
				self.feed=feed
    	    
			def load(self):
				feed= Bag(self.feed)['rss.channel']
				result= Bag()
				result['title']= feed.pop('title')
				result['description']= feed.pop('description')
				result['link']= feed.pop('link')
				result['language']= feed.pop('language')
				result['copyright']= feed.pop('copyright')
				dig= feed.digest('#v.title, #v.description, #v.pubDate, #v.link')
				news=Bag()
				for title, description, pubDate, link in dig:
					news.setItem(title.replace('.', '\.').replace(' ','_'), # label 
					             description,                               # values
					             link=link, date=pubDate, title=title)      # attributes
				result['news']=news
				return result

	Here is how the resolver works:

	>>> mybag['feeds.washingtonpost']= RssFeedResolver('http://www.washingtonpost.com/wp-dyn/rss/world/index.xml')
	#NISO ??? There's an unknown error:
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "/Users/niso/sviluppo/genro/gnrpy/gnr/core/gnrbag.py", line 2357, in __init__
	    parname = self.classArgs[j]
	IndexError: list index out of range

	The resulting Bag is structured as shown below:
	
	+--------------------+------------------------------------------------------------------------------------------------------+
	| **item**           |  **value**                                                                                           |
	+====================+======================================================================================================+
	|  `title`           |  washingtonpost.com - World News and Analysis From The Washington Post                               |
	+--------------------+------------------------------------------------------------------------------------------------------+
	|  `description`     |  World news headlines from the Washington Post,including international news and opinion from Africa, |
	|                    |  North/South America,Asia,Europe and Middle East. Features include world weather, news in Spanish,   |
	|                    |  interactive maps, daily Yomiuri and Iraq coverage.                                                  |
	+--------------------+------------------------------------------------------------------------------------------------------+
	|  `link`            |  http://www.washingtonpost.com/wp-dyn/content/world/index.html?nav=rss_world                         |
	+--------------------+------------------------------------------------------------------------------------------------------+
	|  `language`        |  EN-US                                                                                               |
	+--------------------+------------------------------------------------------------------------------------------------------+
	|  `copyright`       |  None                                                                                                |
	+--------------------+------------------------------------------------------------------------------------------------------+
	|  `news`            |  Bag of News                                                                                         |
	+--------------------+------------------------------------------------------------------------------------------------------+

	Each new item is a BagNode structured as follows:

	+--------------------------------------+-----------------------------------------------------------------+---------------------+
	|    label                             |   value                                                         |     attributes      |
	+======================================+=================================================================+=====================+
	| In_Russia,_A_Secretive_Force_Widens_ | MOSCOW - On Nov. 15, the Russian Interior Ministry and Gazprom, |  link, date, title  |
	|                                      | the state-controlled energy giant, announced...                 |                     |
	+--------------------------------------+-----------------------------------------------------------------+---------------------+

.. _bag_shortcuts:

Shortcuts: the BagCbResolver
============================

	If a dynamic value is simply a function call, you can avoid a new resolver definition by using an instance of the :class:`gnr.core.gnrbag.BagCbResolver` class, that is a generic BagResolver for callback functions:

		>>> from gnr.core.gnrbag import Bag, BagCbResolver
		>>> from datetime import datetime
		>>> mybag = Bag()
		>>> mybag['now'] = BagCbResolver(datetime.now)
		>>> print mybag['now']
		2010-11-18 14:23:40.070095
	
	This shortcut can work for every function::

		def sayHello():
			return 'Hello World!'
		
	So we can apply the ``sayHello()`` method to a Bag:
		
		>>> mybag['hello'] = BagCbResolver(sayHello)
		>>> print mybag['hello']
		Hello World!
	
	As alternative syntax you can use the :meth:`setCallBackItem` method:

		>>> mybag.setCallBackItem('hello', sayHello)

.. _bag_formula:

Bag Formula
===========

	We now introduce the :class:`gnr.core.gnrbag.BagFormula` class: it is a resolver method who allows to define some particular expressions among the Bag's items, as if they were cells of a spreadsheet. The ``formula()`` method takes a formula as first parameter.
	
	**Formula definition:** a formula is a string who represents an expression in which all the variables are marked with the char ``$``. The ``formula()`` method may also take some kwargs that specify the path of each variable:

	>>> mybag=Bag({'rect': Bag(), 'polygon': Bag()})
	>>> mybag['rect.params.base'] = 20
	>>> mybag['rect.params.height'] = 10
	>>> mybag['rect.area'] = mybag.formula('$w*$h', w ='params.base', h='params.height')
	>>> print mybag['rect.area']
	200
	
.. _bag_symbol_formula:
	
Bag Formula: ``the defineSymbol()`` and the ``defineFormula()`` methods
=======================================================================
	
	Bag has a register for every defined formula and symbols. So if you plan to use them in several situations, it is better using the following two methods:
	
	* :meth:`defineSymbol`: define a variable and link it to a BagFormula Resolver at the specified path.
	
	* :meth:`defineFormula`: define a formula that uses defined symbols.
	
	>>> mybag.defineFormula(calculate_perimeter='2*($base + $height)' )
	>>> mybag.defineSymbol(base ='params.base',  height='params.height')
	>>> mybag['rect.perimeter']= mybag.formula('calculate_perimeter')
	>>> print mybag['rect.perimeter']
	60

	In the following examples we use a previously defined formula in which its variables are directly bound to a Bag's element and kwargs are bound to the ``formula()`` method.

	>>> mybag.defineFormula(calculate_hypotenuse='(($side1**2)+ ($side2**2))**0.5')
	>>> mybag.triangle = Bag()
	>>> mybag['triangle.sides.short'] = 2
	>>> mybag['triangle.sides.long'] = 4
	>>> mybag['triangle.sides.hypotenuse'] = mybag.formula('calculate_hypotenuse', side1='short', side2='long')
	>>> print mybag['triangle.sides.hypotenuse']
	4.472135955
	
	When a Bag item is bound to the symbol of a formula we use a relative or an absolute path:
	
	**Relative path example:**
	
	As perimeter is within the bag calculated, the relative paths to reach side_number and side_length must include a backward step until polygon level.
	
	>>> mybag.setBackRef()
	>>> mybag['polygon.side_number']=5
	>>> mybag['polygon.params.side_length']=10
	>>> mybag['polygon.calculated.perimeter']= mybag.formula('$num*$length',
	>>>                                                       num='../side_number',
	>>>                                                       length='../params.side_length')
	>>> print mybag['polygon.calculated.perimeter']
	50
	
	**Absolute path example:**
	
	Sometimes is simplier to use absolute path, to bound a variable to its value:

	>>> mybag['polygon.side_number']=5
	>>> mybag['polygon.params.side_length']=10
	>>> mybag['polygon.calculated.perimeter']= mybag.formula('$num*$length',
	>>>                                                       num='/polygon/side_number',
	>>>                                                       length='/polygon.params.side_length')
	>>> print mybag['polygon.calculated.perimeter']
	50

	<#NISO ??? Explain better!!! Now it's necessary to specify with more accuracy how does BagFormula work. The Bag who calls the ``defineFormula()``, ``defineSymbols()`` and ``formula()`` methods becomes a sort of namespace for our spreadsheet like system. It is the origin of the absolute paths and has two important properties that are the dictionary of the formulas and the one of the symbols. />

	.. image:: ../images/bag/bag-resolver2.png
	