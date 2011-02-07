.. _instances_instanceconfig:

======================
``instanceconfig.xml``
======================

	.. note:: We recommend you to read the :ref:`gnr_introduction` to the ``genro_gnr_index`` folder before reading this section.
	
	* :ref:`instanceconfig_description`
	* :ref:`instanceconfig_tags`: :ref:`instanceconfig_packages`, :ref:`instanceconfig_db`, :ref:`instanceconfig_authentication`, :ref:`instanceconfig_xml_auth`, :ref:`instanceconfig_py_auth`
	
.. _instanceconfig_description:
	
Description of the file
=======================

	The ``instanceconfig`` is an XML file that allow to handle different aspects of your projects. Among other things it allows you to:
	
	* define the packages you want to use in your :ref:`genro_structure_mainproject`
	* define the name of your database
	* handle the permits of your :ref:`genro_structure_mainproject`
	
	With the :ref:`instances_autofill` the ``instanceconfig`` will look like this one::
	
		<?xml version='1.0' encoding='UTF-8'?>
		<GenRoBag>
		    <packages _T="NN">
		    </packages>
		    <db _T="NN">
		    </db>
		    <authentication pkg="adm">
		        <py_auth _T="NN" defaultTags="user" pkg="adm" method="authenticate"></py_auth>
		    </authentication>
		</GenRoBag>

.. _instanceconfig_tags:

Tags
====

	Let's see its content:

	* The file begins and ends with a ``<GenRoBag>`` tag: that's because during the execution of the project, this file is being converted in a :ref:`genro_bag_intro`.
	* The ``<packages>`` tag allow to include any other package from other projects; Genro will search it through its mixin tecnique. For more information, check the :ref:`instanceconfig_packages` paragraph.
	* The ``<db>`` tag includes the name of your database. For more information, check the :ref:`instances_db` paragraph.
	* The ``<authentication>`` tag allow to handle all the access authorization to your project. Check the :ref:`instances_authentication` paragraph for more information.
	* The ``_T="NN"`` is a special attribute that allow to keep track of datatypes (for more information, check the :ref:`bag_from_to_XML` section).

.. _instanceconfig_packages:

``<packages>``
==============
	
	The ``<packages>`` tag allow to include any other package from other projects: this allow you to use every file (like the :ref:`packages_model` and the :ref:`packages_webpages`) of the packages you've imported. If you want to import one package, you have to:
	
	* include its path into the ``<packages>`` of your :ref:`gnr_environment` file::
	
		<packages>
			<my paths='~/yourRootPathForGenro/yourFolderPathOfYourProject' />
		</packages>
	
	* include the package name into the ``<packages>`` tag of the ``instanceconfig.xml`` file::
	
		<packages>
		    <mypackage />
		</packages>
		
	where ``mypackage`` is the name of your main package.
	
	Remember that in the ``<packages>`` tag you have at least put your main package, that is the one where you put your :ref:`packages_model` and :ref:`packages_webpages` folders.
	
.. _instanceconfig_db:

``<db>``
========

	In the ``<db>`` tag you have to specify at least the database name::
	
		<db dbname='myDatabaseName' />
	
	There are many options you can add:
	
	* ``dbname``: specify the name of the database
	* ``implementation``: you can choose the SQL database engine. By default Genro will be use postgreSQL_ (implementation="postgres")
	* ``host``: specify the host. Default value is ???
	* ``password``: the password of the SQL database engine.
	* ``user``: the user of the SQL database engine.
	
	.. note:: We suggest you to keep the usage of postgreSQL_, but, if you prefer, you can use MySQL_ or SQLite_.
	
	.. _postgreSQL: http://www.postgresql.org/
	.. _MySQL: http://www.mysql.it/
	.. _SQLite: http://www.sqlite.org/
	
	This is an example of ``<db>``::
	
		<db implementation="postgres" host="localhost" password="superSecurePwd" user="postgres" dbname="mypersonaldatabase" />
	
.. _instanceconfig_authentication:

``<authentication>``
====================

	The ``<authentication>`` tag allow to manage the authentications to your project's webpages.
	
	You have to specify the ``adm`` package inside the ``<authentication>`` tag::
	
		<authentication pkg="adm"></authentication>
	
	The ``<adm>`` package allow to manage the authenitcations. For more information, check the :ref:`genro_library_adm` paragraph.
	
	Inside the ``<authentication>`` tag we have to define two different tags: the ``<py_auth>`` and the ``<xml_auth>``.

.. _instanceconfig_xml_auth:

``<xml_auth>``
==============

	The ``<xml_auth>`` tag is a support tag that comes in handy to the :ref:`instanceconfig_py_auth` tag; it allows to you (i.e. the programmer) to enter the first time into the webpage called :ref:`genro_packages_adm_webpages_manage_users` (of the :ref:`genro_library_adm` package), so that you can give to your customers (and to you!) a user and a password to access to your project.
	
	The ``<xml_auth>`` attributes are:
	
	* The first attribute is the name of your temporary user (in the example below, ``nameUser``)
	* `pwd`: the password of your temporary user
	* `tags`: the level of authorization of your user:
	
		* `_DEV_`: developer
		* `admin`: administrator
		* `user`: user
		* `staff`: staff
	
	Let's see an example::
	
		<xml_auth defaultTags="users,xml">
			<myName pwd="superSecurePwd" tags="_DEV_,admin,user,staff"/>
		</xml_auth>
	
	where ``myName`` is the name, ``superSecurePwd`` is the password.

.. _instanceconfig_py_auth:

``<py_auth>``
=============

	Once you have your temporary user [#]_, you can create the users for your customers.
	
	For doing this, you have to go the following webpage::
	
		http://127.0.0.1:yourPort/adm/manage_users
		
	where in place of ``yourPort`` you have to put your port (e.g. 8090) that you have set in your :ref:`sites_siteconfig`::
	
		http://127.0.0.1:8090/adm/manage_users
	
	Once you're there you will find a :ref:`genro_standardtable`; open :ref:`genro_st_padlock` (you can do it because you entered with xml authorization) and set all the users you need (your one, the customers one...).
	
	So, your ``<authentication>`` tag will look like this one::
	
		<authentication pkg="adm">
			<py_auth defaultTags="user" pkg="adm" method="authenticate"></py_auth>
			<xml_auth defaultTags="users,xml">
				<myName pwd="superSecurePwd" tags="_DEV_,admin,user,staff"/>
			</xml_auth>
		</authentication>
	

**Footnotes**:

.. [#] If you don't have a temporary user, please create it following the instructions of the :ref:`instanceconfig_xml_auth` paragraph
