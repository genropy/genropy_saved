*********************************
Miscellaneous notes about GenroPy
*********************************

Construction of Bags
====================

There are several ways to build bags in genropy:

* from an XML file;
* using the instructions from the python module ``gnr.core.gnrbag``, in this case the code is similar to the construction of a dictionary
* using module ``gnr.core.gnrstructures``  In this case, the code consists of a set of python method calls. This subsequently supports the definition of the database model, in addition to the construction of webpages.


Mapping models the database structure
=====================================

In GenroPy, the transition from model classes to the database is in this way:

1. The code in files in ``<name of package> / models / <table_name>. py`` builds a bag in python which builds the structure of the table.
2. The constructed bag is translated into python objects.
3. Genro script ``gnrdbsetup <project>`` compares these objects with the database structure and performs any updates required.

Site, Instance, Packages and Components
=======================================

GenroPy applications are divided into several layers, allowing customisation (ensuring an easy upgrade even with customisation) and reuse of code and resources among various projects.

A Project of Genropy consists of:


A site:
	deals with everything related to the configuration for a particular installation includes Web components and configurations that are necessary for the execution over the **Web** typically contains the configuration and WSGI script ``root.py`` ( it is used as the executable if you want to use a debugger, like WingIDE).

An instance:
	contains customisations for the particular customer. Usually contains parameters for database access. Has a ``data`` subfolder that you can use to store data in filesystems. When working with the Python interpreter or command line tools, usually working at the instance::

		#!python
		from gnr.app.gnrapp import GnrApp
		instance = GnrApp('name_of_project')

	Gio mentioned the concept of sub instance, used to change the application configuration at runtime (eg, for access to historical data already eliminated from the main current database instance).

A package:
	are the various modules that make up the application code to Genro, including the main package, which is the application developed. Genro provides additional modules that implement common functions for all applications (user management, table of Italian municipalities, etc.).. E 'in the application package (or packages of options), which concentrates most of the Python code (a part of the core framework that is in the package python ``gnr`` and its children).

	The package ``glbl`` already contains a table of locations and Italian municipalities. (**TODO**: ask Giovanni for the table data, as it does not seem to be present in SVN).

	**Note**: the packages of Genro are not Python packages (not a set of linked modules, containing a file `` __init__.py ``), and genre packages can not be imported with the statement ``import <module>`` or ``import from <package> <module or ` class>``.

Components and Resource:
	These are common and reusable to a project. They Include both the Javascript and CSS to Python (eg ``includedView``, standard tables). These components are resources should be located in the ``_resources`` folder of the package and sub directories may be used within the ``_resources folder``.  They are used in webpages through ``py_requires``, ``js_requires`` and ``css_requires``. The ``code`` in module gnr.web.gnrwsgisite, manages the mixin resources.


Mixin classes at runtime
************************

GenroPy's application class builds *mixin* classes at runtime. The methods and resources (CSS, JS, and Python components) are aggregated at runtime according to specific rules that allow you to customize the behaviour for a single install and maintain these customizations, with minimal impact, even for future updates.

When code changes are made the WSGI application restarts.

It can perform the mixin of the interface (webpages, components, CSS, JS, etc.) and for the database structure (models).

**TODO:** See the wiki site http://projects.softwell.it/ the page *Customization* for an explanation of the rules of mixin and customization of applications.

GenroPy web operations
======================

In the construction of the pages, GenroPy first loads the browser (client) with its JavaScript engine (the Genro engine). The the JS engine immediately requests the server to build the recipe for the DOM.  This recipe is returned to the client in a bag.   This is the page description and content of the original datastore form of bags. At this point, the JS can make calls to the python code to further build the page.

In practice, GenroPy behaves in this way:

1. The client makes the HTTP request page ``foo``::

	client ----------- HTTP ----------> server (wsgisite)

2. GenroPy sends a standard blank page, which contains practically only the engine ``gnrjs``::

	client <----- javascript engine --- server (wsgisite)

3. The JavaScript engine calls the server page content, a server side Python function called the ``main`` of ``WebPage`` ::

    js engine ------- ready -----------> server (page ``main.py``)

4. The server sends a description of the page content in high level in terms of widgets, and content of the datastore in the form of bags::

    page js <------ bags ------------- page python

5. From then on, the communication proceeds primarily doing updates to the datastore (or user interface) using the functions rpc::

    page js <- dataRpc() or remote() -> page python

WSGI
====

WSGI is a standard for interfacing with Python web frameworks webservers. It also allows you to compose various web components together through a system of middlewares (similar concept, but not compatible with similar components in Django). A WSGI_ site contains links to many useful resources (frameworks, middlewares, servers).

.. _WSGI: http://wsgi.org/wsgi

WSGI application defines a function that takes a Web request and returns the answer. WSGI middleware is simply an application that calls another, as in the pattern Decorator_.
WSGI standard defines a standard format for the request (which can be decorated with additional information when processing the various middlewares) and response (which can also be asynchronous).

.. _Decorator: http://en.wikipedia.org/wiki/Decorator_pattern

GenroPy Beaker_ using middleware for session management and weberror management Traceback (including the useful ability to open a python interpreter at the point where the error occurs). GenroPy uses Paste_ WebOb_ during development and with standalone servers (I think the function is provided by weberror Paste).

.. _Beaker: http://beaker.groovie.org/
.. _Paste: http://pythonpaste.org/
.. _WebOb: http://pythonpaste.org/webob/reference.html

For an example of middleware, see ``gnrpy/gnr/web/gzipmiddleware.py `` (the script does not work currently Genro, but for other reasons, Michele Bertoldi indicates that it is working)). The file ``root.py`` within the site directory of the genro project (WSGI application) is where is is defined.

Apache WSGI
***********

To use WSGI with apache, you must install the module and configure ``mod_wsgi``::

	<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www
	WSGIDaemonProcess gnr user=genro group=genro python-eggs=/tmp threads=25
	SetEnv PROCESS_GROUP gnr
	WSGIProcessGroup %{ENV:PROCESS_GROUP}
	# modify the following line to point your site
	WSGIScriptAlias / /home/genro/progetti/mmusic/sites/provarci/root.py
	#WSGIRestrictProcess gnr
	<Directory /home/genro/progetti/mmusic/sites/provarci>
	Options Indexes FollowSymLinks
	AllowOverride All
	Order allow,deny
	Allow from all
	</Directory>
	</VirtualHost>

Additional data types, not in the TextMate bundle
=================================================

Tipo ``DH``:
	TimeStamp

GnrApp
======

The code to create an instance is as follows::

	#!python
	from gnr.app.gnrapp import GnrApp
	instance = GnrApp('my_project')

1. ``GnrApp.__init__`` loads the configuration of the instance from ``instanceconfig.xml``.
2. ``GnrApp.init`` running:
	* the hook ``onIniting``
	* creates necessary objects from packages
	* the hook ``onInited``

GnrPackage
==========

The file ``main.py`` of a package, you define ``class``  ``package`` and ``table``. The methods of these classes are available at the respective web pages as ``self.package.name_of_method`` and ``as self.db.table('table name').name_of_method``.

Page
====

Page objects can access the various application components using Genro instance variables:

* ``self.package``
* ``self.db``
* ``self.application`` (es. ``self.application.config``)
* ``self.site`` (es. ``self.site.config``)

Table Objects
=============

The table objects are accessible from pages ``self.db.table('package.table')``. The method ``query `` returns an object of type table. This object representing a table from the db may be configured according to the specified parameters.  The query on the db is not performed, until a further method is called. The methods that can be used include ``selection`` and variants of the ``fetch`` method to return data as list, dictionary, iterator or bag.

Example::

	#!python

	db = ...
	tbl = db.table('common')
	qry = tbl.query(...)
	sel = qry.selection()

	# edit records in memory, even adding new fields (eg for calculated fields to send to client)
	sel.apply(lambda r: dict(area=r.base*r.height))

	sel.output(format)

The selections support various formats:

bag:
	genro Bag (refer to  ``gnr.core.gnrbag``)

json:
	JSON serialization format

*more*:
	for other formats, see the methods with the prefix ``out_``  object selection

The selections have methods to make totals or statistical analysis (averages, sums, etc..) aggregated into various fields. See the methods ``analyze`` or ``totalize``.

**NOTE**: selections are implemented in terms of bags (not database) and can also be used with data sources from different db.

See also ``gnr.gnrsql.gnrsqldata`` for information on selection/query/record.

Useful Tools
============

BonjourFoxy:
	Firefox plugins to see the websites registered in the local network with Bonjour (useful in development)

Navicat:
	database editor with good support for Postgres


pycallgraph
===========

Use the profiler python calls and shows how to graph using graphviz. To install it, use ``easy_install`` or ``pip``::

	sudo easy_install  -U -Z pycallgraph

Bags
====

The bag of GenroPy is very powerful and pervasive in the design of the framework. (This is a great thing, but a possible downside in terms of security).

You can create a bag with data from:

* Dictionary
* A list of key / value
* Another bag
* The name of an xml file
* The name of a directory, in this case you can take the tree and also read the contents of XML files (as if they were part of the same tree)

The power of bags lies in the concept of a resolver. They are a callable with a cache time, so they are lazy. They promise to return a bag. The resolver can cache the returned bag or provide new data for each call.

Interesting video on the design of web frameworks
=================================================

Djangocon 2008, `Building a better framework`_

.. _Building a better framework: http://www.youtube.com/watch?v=fipFKyW2FA4&feature=related

DOJO
====

The documentation is available as an AIR application DOJO (search DOJO * Toolbox *), but not kept up to date. Currently Genro using version 1.1 of the Dojo (and now we are at 1.4).

The datastore and the Javascript code of Genro
==============================================

Through various commands python, you can attach the javascript code to the events of the components interface or events generated by the datastore

The datastore is a Genro bag.

Syntax for datapath
*******************

The path followed by the syntax in the datastore:

* ``path.absolute.in.datastore``
* ``.path.relative.in.datastore``
* ``#ID.path.relative.to.the.ID``

The path indicates the access path to data to virtually every element of the datastore (it is implemented by reading the Bag interface, and thus includes many things: for example, you can also specify the CSS classes of an HTML element linking them to an element of the datastore), using the prefixes:

* "^" (circumflex accent): ``^access.to.resolver``, setting an observer at this node. The component will be informed of changes to the datastore
* equal: ``=accessed.from.resolver``, reads the contents of the datastore.

Access to the datastore from javascript
***************************************

The possible operations on the datastore include:

**SET**:
	sets a value and triggers any associated events (ie any observers or resolver connected by "^")
**PUT**:
	sets a value, but does not trigger the events associated
**GET**:
	reads the contents of a value in the datastore
**FIRE**:
	sets a value in the datastore, and then triggers the events associated, and then resets the value to zero (without triggering events). It is used when you need to trigger events via a temporary parameter to the Observers.

These operations can be specified in the javascript events associated with an interface, the framework deals gnrjs to the expansion of these macros. It 'can be accessed from its datastore javascript code (ie from code written in .JS file and then read without macro-expansion) using simple javascript functions.

Useful components (defined as resources)
========================================

includedViewBox:
	list of records useful for implementing views master / detail

recordDialog:
	popup window to edit a single record. Usually used for editing records includedViewBox.

Studying these two components for more information on how to define complex components using resources.

Idea for a useful tool for development in Genro
===============================================

Extracted relations (reading the Observer) between the interface and the datastore and display them in graphical form with graphviz.

**NOTE:** has been implemented in ``gnrdbgraph``.

Opensource policies of Softwell
===============================

* The shell (packages in `` gnr .*``) will always remain open source.
* In the future, Softwell could decide to continue the development of resources (``_resources`` ) as closed source software.

Security in PDF files
=====================

To read local data or parameters of the URL may need a certificate to avoid the security alert (but maybe used by browsers and upload the PDF from the server, this is not needed).

Testgarden
==========

The project testgarden contains demos for all widgets included in the genre. Can be used for testing and verifying without breaking anything.

**NOTE**: However, I do not think that is actively maintained, and I believe it is already half-broken at present.

DOJO
====

Genro utilises Dojo_ using version 1.1, see also documentation `Dojo Campus`_.

.. _Dojo: http://www.dojotoolkit.org/
.. _Dojo Campus: http://dojocampus.org/

In Dojo, widgets can be of two types: Container, ContentPanes.

* The container can contain other Containers or ContentPanes.
* The ContentPanes can contain widgets or HTML elements.

In practice, following the pattern *Composite*.

In previous versions of Dojo, ``borderContainer`` was necessary to specify the center as last item inserted. It is better to do it now, though not necessary, because this speeds up page loading (you can calculate the occupation of the central without first loaded and calculated that the elements at the edges).

Resource ``public``
===================

The resource ``public`` implements the basic elements of the interface Genro.

It also provides CSS classes:

pbl_RoundedGroup:
	used to divide the page into two logically separated areas.

pbl_RoundedGroupLabel:
	to give a title to a group (a pbl_RoundedGroup).

These elements are often used within borderContainers.

Events and activities
=====================

Each interface element (widget or HTML tags) can attach javascript events using the syntax ``connect_<event_name>``.
Example::

	def divTest(self, parentContainer):
		cp = parentContainer.contentPane(...)
		cp.div(connect_onDoubleClick='JS code')

As a convention, the syntax ``connect_<event_name>`` is used for events or JavaScript dojo, while the syntax ``<event>_action`` is used for events and actions genropy.

includedView
============

The includedView is well documented. Some parameters such as ``formPars`` and ``pickerPars`` are deprecated but (now there is another way to do the same thing.)

The possible specifiers are ``addAction=True`` or ``delAction=True`` to unleash the standard events (modification of records in a recordDialog). In this case, the records are updated in the datastore (ie are treated as logically part of the record in the master table, and the changes will be applied to save the master record).

Using the method ``iv.gridEditor()`` can define the widgets used for editing lines. (The widgets are reused gridEditor, moving them into the DOM of the page, as you move between the lines.)

Componenti per operare sul datastore
====================================

``data()``:
	stores a value in the datastore

``dataFormula()``:
	Calculate a cell of the datastore from other values (like a spreadsheet)

``dataController()``:
	Running JS code, linking it to an event in the datastore (via a resolver).

Parameters of dataController or dataFormula become delcarations of local variables used in the formula or the same JS.

Remote Operation
****************

``dataRecord()``:
	**TODO**: to be explored - I question the need to store a database record in the datastore

``dataRemote()``:
	Set a resolver in the datastore. Access to this item in the datastore will be called Python code (defined in a function with the prefix ``rpc_`` ) will return a bag.

``dataRpc()``:
	as above, dataRpc is the function of low-level underlying the previous functionalityi. Can be used to make calls to python code (via triggering resolver as parameters).
	It is possible to specify js code to call before the call(with the parameter ``onCalling='codice JS'``) or with the results received from the server (``onresult='codice JS'``).

The parameters of these functions that do not begin with an underscore "_" are passed to the server and are available to Python code called.

The entry point into the web page called by these functions have the prefix ``rpc_``.

**NOTE:** You can use ``page.externalUrl(...)`` to get the URL of an RPC call (useful for passing URLs loading / saving XML to PDF document in the project *myproject*).

Functions can return:

* a bag
* a tuple (bag, dictionary) -- dictionary contains the attributes / metadata bag, visible in the explorer of the datastore by clicking while holding down SHIFT

There is also an API to make changes to the datastore in RPCs.

FormBuilder
===========

Component to simplify the creation of forms.

Using the method ``field``, You can define fields simply by specifying the name. The widget will be built under the correct type of database field. The method ``field`` accepts the parameter  ``autospan=N``, corresponding to ``colspan = N`` or ``width = '100%'``.

Triggers
========

Triggers defined on page
************************

It is possible to define methods at the python-level of a web page that are called when the records in a given table are loaded or saved. The names of methods should follow this syntax::
	on<Operation>
	on<Operation>_<name_of_package>_<name_of_table>

possible *Operation* is ``Loading``, ``Saving`` or ``Saved``.

This is implemented at rpc/web layer.

Triggers on table
*****************

At the table level, events are similarly available ``Inserting``/``Inserted``, ``Updating``/``Updated`` e ``Deleting``/``Deleted``.

**NOTE**: you can specify whether the database should delete multiple records using a single SQL statement or individual statements for each record. There are different triggers for the two cases.
