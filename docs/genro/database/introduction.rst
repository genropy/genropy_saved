	.. _genro-database-introduction:

====================================================
 Make a database management project: an introduction
====================================================

	- :ref:`genro-project-introduction`
	
	- :ref:`genro-project-creation`

	- :ref:`genro-project-structure`: :ref:`genro-instances`, :ref:`genro-packages`, :ref:`genro-resources` and :ref:`genro-sites`

	.. _genro-project-introduction:

Introduction
============

	???

	.. _genro-project-creation:

Create a Genro project
======================

	To create a (Genro) project, you need to create a "package".

	To create a ``package``, just type in your command window the command::

		gnrmkproject ProjectName
	
	This will create a folder with the project name you have chosen, and 4 subfolders called ``Instances``, ``Packages``, ``Resources``, ``Sites``, as you can see in this image (in this case the name of the project is "MyProject"):

	.. image:: myproject.png

	You can call an help that explains all the possibilities on creating a project, typing::
	
		gnrmkproject -h
	
	.. image:: myproject-h.png
	
	So, if you want to create a project with both site and instance default features (that we will explain later in this page), you have to write::

		gnrmkproject ProjectName -a

	You can see the result in this image:

	.. image:: myproject2.png

	In the next section we'll see all the details of a project's subfolders.

	.. _genro-project-structure:

Structure of a project
======================

	??? CONTINUARE DA QUI!

	.. _genro-instances:

Instances
=========

	.. _genro-packages:

Packages
========

	???
	Model --> containing database :ref:`database-table`

	.. _genro-resources:

Resources
=========

	???

	.. _genro-sites:

Sites
=====

	???
