.. _genro_clipboard:

=================================
Miscellaneous notes about GenroPy
=================================

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

GenroPy's application class builds *mixin* classes at runtime. The methods and resources (CSS, JS, and Python components) are aggregated at runtime according to specific rules that allow you to customize the behavior for a single install and maintain these customizations, with minimal impact, even for future updates.

When code changes are made the WSGI application restarts.

It can perform the mixin of the interface (webpages, components, CSS, JS, etc.) and for the database structure (models).

**TODO:** See the wiki site http://projects.softwell.it/ the page *Customization* for an explanation of the rules of mixin and customization of applications.

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

Interesting video on the design of web frameworks
=================================================

Djangocon 2008, `Building a better framework`_

.. _Building a better framework: http://www.youtube.com/watch?v=fipFKyW2FA4&feature=related

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

Using the method *field*, You can define fields simply by specifying the name. The widget will be built under the correct type of database field. The method *field* accepts the parameter  ``autospan=N``, corresponding to ``colspan = N`` or ``width = '100%'``.

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
