.. _genro_database_introduction:

===============================
Make a project: an introduction
===============================

	* :ref:`genro_project_introduction`
	
	* :ref:`genro_project_creation`

	* :ref:`genro_project_structure`: :ref:`genro_instances`, :ref:`genro_packages`, :ref:`genro_resources` and :ref:`genro_sites`

	.. _genro_project_introduction:

Introduction
============

	Genro is a Data Base Management System (DBMS), so it is a software that is able to manage small and great database ensuring to follow great reliability and security standards.

.. _genro_project_creation:

Create a Genro project
======================

	To create a project, you need to create a "package".

	To create a ``package``, just type in your command window the command::

		gnrmkproject projectname
	
	This will create a folder with the project name you have chosen, and 4 empties subfolders called ``Instances``, ``Packages``, ``Resources``, ``Sites``, as you can see in this image (in this case the name of the project is "myproject") [#]_:

	.. image:: ../images/myproject.png
	
	However, if you want to create a project with both site and instance default features (that we will explain later in this page), you have to write::

		gnrmkproject ProjectName -a

	You can see the result in this image:

	.. image:: ../images/myproject2.png
	
	In the next sections we'll begin to explain all the details of the project's subfolders.

	However, you can call an help that explains all the possibilities on creating a project, typing::
	
		gnrmkproject -h
		Usage: gnrmkproject [options]

		Options:
		  -h, --help            show this help message and exit
		  -b BASE_PATH, --base-path=BASE_PATH
		                        base path where project will be created
		  -s, --create-site     create site
		  -i, --create-instance
		                        create instance
		  -a, --create-all      create both site and instance
		  -p WSGI_PORT, --wsgi-port=WSGI_PORT
		                        Specify WSGI port
		  -r WSGI_RELOAD, --wsgi-reload=WSGI_RELOAD
		                        Specify WSGI autoreload
		  -d WSGI_DEBUG, --wsgi-debug=WSGI_DEBUG
		                        Specify WSGI debug
	
	As you can see in the previous snapshot, you can use ``-p``, ``-r`` and ``-d`` to specify some :ref:`genro_wsgi` features.

.. _genro_project_structure:

Structure of a project
======================

	???

.. _genro_instances:

Instances
=========

.. _genro_packages:

Packages
========

	???
	Model --> containing database :ref:`genro_database_table`
	Webpages --> containing all the webpages of your project --> :ref:`genro_webpage`

.. _genro_resources:

Resources
=========

	???

.. _genro_sites:

Sites
=====

	???

.. [#] Genro team prefer to call a project using only lowercase letters.
