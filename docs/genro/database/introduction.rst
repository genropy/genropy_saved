	.. _genro-database-introduction:

=================================
 Make a project: an introduction
=================================

	- :ref:`genro-project-introduction`
	
	- :ref:`genro-project-creation`

	- :ref:`genro-project-structure`: :ref:`genro-instances`, :ref:`genro-packages`, :ref:`genro-resources` and :ref:`genro-sites`

	.. _genro-project-introduction:

Introduction
============

	Genro is a Data Base Management System (DBMS), so it is a software that is able to manage small and great database ensuring to follow great reliability and security standards.

	.. _genro-project-creation:

Create a Genro project
======================

	To create a project, you need to create a "package".

	To create a ``package``, just type in your command window the command::

		gnrmkproject ProjectName
	
	This will create a folder with the project name you have chosen, and 4 subfolders called ``Instances``, ``Packages``, ``Resources``, ``Sites``, as you can see in this image (in this case the name of the project is "myproject") [#]_:

	.. image:: myproject.png

	You can call an help that explains all the possibilities on creating a project, typing::
	
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
	
	As you can see in the previous snapshot, you can use ``-p``, ``-r`` and ``-d`` to specify some :ref:`genro-wsgi` features.
	
	However, if you want to create a project with both site and instance default features (that we will explain later in this page), you have to write::

		gnrmkproject ProjectName -a

	You can see the result in this image:

	.. image:: myproject2.png

	In the next section we'll see all the details of the project's subfolders.

	.. _genro-project-structure:

Structure of a project
======================

	???

	.. _genro-instances:

Instances
=========

	.. _genro-packages:

Packages
========

	???
	Model --> containing database :ref:`genro-database_table`
	Webpages --> containing all the webpages of your project --> :ref:`genro-webpage`

	.. _genro-resources:

Resources
=========

	???

	.. _genro-sites:

Sites
=====

	???

.. [#] Genro team prefer to call a project using only lowercase letters.
