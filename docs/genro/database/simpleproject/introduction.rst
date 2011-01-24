.. _genro_database_introduction:

=========================================
Introduction on the creation of a project
=========================================

	* :ref:`genro_project_introduction`
	
	* :ref:`genro_project_creation`

	.. _genro_project_introduction:

Introduction
============

	Genro is a Data Base Management System (DBMS), so it is a software that is able to manage small and great database ensuring to follow great reliability and security standards.

.. _genro_project_creation:

Create a Genro project
======================

	We want now help you on a creation of a simple project for a management of a database.

	To create a project is very simple; just type in your command window the following line (don't do it for now!!) [#]_::

		gnrmkproject projectname
	
	This will create a folder with the project name you have chosen, and 4 empties subfolders called: ``instances``, ``packages``, ``genro_resources``, ``genro_sites``.
	
	In the following image you can see the project folder with its relative subfolders (we choose ``myproject`` as project name):

	.. image:: ../images/myproject.png
	
	.. note:: the Genro team prefer to call their projects using only lowercase letters.
	
	However, if you want to create a project with both site and instance default features (that we will explain later in the following sections), you have to write::

		gnrmkproject projectname -a

	You can see the result in this image:

	.. image:: ../images/myproject2.png
	
	Now type the command line ``gnrmkproject projectname -a`` and check the tree structure you have created (the 4 subfolders and the contents of the ``instances`` and ``sites`` folders). In the next sections we'll begin to explain all the details of the project's subfolders.

	You can create a project setting many options. Type::
	
		gnrmkproject -h
	
	to call an help that explains all the possibilities::
	
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

**Footnotes**:

.. [#] ``gnrmkproject`` abbrevation has the meaning of ``GeNRo MaKe PROJECT``.
