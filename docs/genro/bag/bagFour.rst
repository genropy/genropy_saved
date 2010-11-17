	.. _genro-bag-four:

=========================
Resolver and dynamic bags
=========================

	- :ref:`bag-four-introduction`
	
	- :ref:`bag_resolver`
	
	- :ref:`bag_resolver_example1`
	
	- :ref:`bag_resolver_example2`
	
	- :ref:`bag_resolver_example3`
	
	- :ref:`bag_shortcuts`
	
	- :ref:`bag_formula`

	.. _bag-four-introduction:

Introduction
============

	A Bag item can be something more than a static value.
	
	**dynamic item:** a dynamic item is a Bag item that is able to call a function that retrieves dynamically a value or a cached copy of it.
	
	Some possible usages for a dynamic item are:

	- get values from a database server.

	- get values from webservices.

	- calculate values in real-time.

	- etc.
	
	.. image:: ../images/bag/bag-resolver.png

.. _bag_resolver:

Resolver
========

	The basic idea of a dynamic Bag is to hide all the function calls treating their results as they were Bag static items (so, a likely-static value can be the result of a realtime elaboration or a remote call.). BagResolver is an interface for defining objects that implement this 'reification'.

	A resolver overrides the primitive __call__, wich is the one that intercepts any round-brackets call, and must implements the method load(). When a resolver is called my_resolver(), it calls its method load(). A resolver may have a cache, if the cacheTime is specified in the args, else it's considered 0. The cache stores the retrieved value and keeps it for a lapse of time called cacheTime. Each resolver implements the method load() that reads the result from cache, if cacheTime isn't elapsed, or takes it from its remote source. The call my_resolver can receive some kwargs. A resolver is set in a node by the BagNode's method setResolver(my_resolver).

.. _bag_resolver_example1:

Resolver Example 1: the TimeResolver
====================================

	For example, there are several ways to create a Bag with an item labeled now that always returns current time. First of all we can define a class TimeResolver that inherits from BagResolver::

	from datetime import datetime

	class TimeResolver(BagResolver):
		def __call__(self):
			return datetime.now()
    
	Defining a BagResolver's sublass requires the reimplementation of the __call__() function.

	Now we can set an instance of TimeResolver as now:

	>>> mybag=Bag()
	>>> mybag['now']=TimeResolver()

	>>> print mybag['now']
	resolving now: <__main__.TimeResolver object at 0x6a870>
	2006-10-04 10:27:16.231559

	As we can see, there's no need to import the module datetime because it was already imported in the class definition.

	If we want the now item to be updated every 100 ms, we can use the TimeResolver? class with a cacheTime value.

	The mybag['now'] value will be updated every 100 ms:

	>>> ct=100
	>>> mybag['now']=TimeResolver(cacheTime=ct)

	>>> print mybag['now']
	resolving now: <__main__.TimeResolver object at 0x6a370>
	2006-10-04 10:27:18.221551
	
.. _bag_resolver_example2:
	
Resolver Example 2: UserInfoResolver
====================================

	The following example defines a resolver that prepares a Bag containing some information about the computer (e.g. hostname, IP, PID, user)::
	
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

	>>> mybag= Bag()
	>>> mybag['info']= InfoResolver()
	>>> info=mybag['info']
	>>> template="This is the process %s. \n You are user %s, from the host %s at the address %s"
	>>> print template %(mybag['info.pid'],mybag['info.user'],mybag['info.hostname'], mybag['info.ip'])
	This is the process 7296. 
	You are user foo_user, from the host ikid.local at the address 192.168.1.53

.. _bag_resolver_example3:

Resolver Example 3: RssFeedResolver
===================================

	In the following example the resolver receives the URL of a RSS feed of the web, and since a Bag can be created starting from an XML it's very easy to have all the news in our bag:

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

	Each news item is a bag node structured as follows:

	+--------------------------------------+-----------------------------------------------------------------+---------------------+
	|    label                             |   value                                                         |     attributes      |
	+======================================+=================================================================+=====================+
	| In_Russia,_A_Secretive_Force_Widens_ | MOSCOW - On Nov. 15, the Russian Interior Ministry and Gazprom, |  link, date, title  |
	|                                      | the state-controlled energy giant, announced...                 |                     |
	+--------------------------------------+-----------------------------------------------------------------+---------------------+

.. _bag_shortcuts:

Shortcuts
=========

	If the dynamic value is simply a function call, you can avoid a new resolver definition by using an instance of BagCbResolver, that is a generic BagResolver for callback functions:

	>>> from gnr.bag.gnrbag import Bag, BagCbResolver
	>>> mybag['now']=BagCbResolver(datetime.now)
	>>> print mybag['now']
	resolving now: <gnr.bag.gnrbag.BagCbResolver object at 0x56cd0>
	2006-12-12 12:41:33.603008
	
	This can work for every function::

	def sayHello():
		return 'Hello World!'

	>>> mybag['hello']=BagCbResolver(sayHello)
	>>> print mybag['hello']
	resolving hello: <gnr.bag.gnrbag.BagCbResolver object at 0x56f90>
	Hello World!
	
	Alternative syntax:

	>>> mybag.setCallBackItem('hello', sayHello)

.. _bag_formula:

Bag Formula
===========

	GnrBag provides as built-in a particular resolver, called BagFormula, that allows the definition of particular expressions among the bag's items, as they were cells of a spreadsheet. The method formula() takes a formula as first parameter. A formula is a string that represents an expression in which all the variables are marked with the char '$. The method fomula() may also take some kwargs that specify the path of each variable.

	>>> mybag=Bag({'rect': Bag(), 'polygon': Bag()})
	>>> mybag.setBackRef()
	>>> mybag['rect.params.base']=20
	>>> mybag['rect.params.height']=10
	>>> mybag['rect.area']= mybag.formula('$w*$h', w ='params.base', h='params.height')
	>>> print mybag['rect.area']
	200
	
	You can define some formulas and symbols if you plan to use them in several situations, in fact Bag has a register of all defined formula and symbols. With the method defineSymbol() it's possible define a variable and link it to a value at the specified path. With the method defineFormula() you can define a formula that uses defined symbols.

	>>> mybag.defineFormula(calculate_perimeter='2*($base + $height)' )
	>>> mybag.defineSymbol(base ='params.base',  height='params.height')
	>>> mybag['rect.perimeter']= mybag.formula('calculate_perimeter')
	>>>print mybag['rect.perimeter']
	60

	In the following examples is used a previously defined formula with the method defineFormula(), but its variables are directly bound to Bag's element and kwargs of the method formula().

	>>> mybag.defineFormula(calculate_hypotenuse= '(($side1**2)+ ($side2**2))**0.5')
	>>> mybag.triangle=Bag()
	>>> mybag['triangle.sides.short']=2
	>>> mybag['triangle.sides.long']=4
	>>> mybag['triangle.sides.hypotenuse']=mybag.formula('calculate_hypotenuse', side1='short', side2='long')
	>>> print mybag['triangle.sides.hypotenuse']
	resolving hypotenuse: <gnr.bag.gnrbag.BagFormula object at 0x101d910>
	4.472135955
	
	When a bag item is bound to the symbol of a formula we use a path. We can use two kinds of path, relative path is the default. By relative we mean that starts from from the point of view of the bag that contains the formula.

	mybag['polygon.side_number']=5
	mybag['polygon.params.side_length']=10
	mybag['polygon.calculated.perimeter']= mybag.formula('$num*$length',
	                                                      num='../side_number',
	                                                      length='../params.side_length')
	>>>print mybag['polygon.calculated.perimeter']
	50

	As perimeter is within the bag calculated, the relative paths to reach side_number and side_length must include a backward step until polygon level. Sometimes is simplier to use absolute path, to bound a variable to its value. As absolute path we mean that it starts from the point of view of the bag that calls the method formula(). An absolute path starts with the char '/'. Let's see the previous example with absolute paths.

	mybag['polygon.side_number']=5
	mybag['polygon.params.side_length']=10
	mybag['polygon.calculated.perimeter']= mybag.formula('$num*$length',
	                                                      num='/polygon/side_number',
	                                                      length='/polygon.params.side_length')
	>>>print mybag['polygon.calculated.perimeter']
	50

	Now it's necessary to specify with more accuracy how does BagFormula work. The bag that calls the methods defineFormula, defineSymbols and formula becomes a sort of namespace for our spreadsheet like system. It is the origin of the absolute paths and has two important properties that are the dictionary of the formulas and the one of the symbols.

	.. image:: ../images/bag/bag-resolver2.png
	