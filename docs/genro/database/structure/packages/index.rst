.. _genro_packages_index:

========
packages
========

	* :ref:`packages_map`
	* :ref:`packages_autofill`
	
	.. module:: gnr.app.gnrdeploy
	
	The ``packages`` folder is... DEFINITION ???
	
.. _packages_map:
	
``packages`` folder content list
================================
	
	Inside every package folder you will find a ``lib`` folder, a ``model`` folder, a ``webpages`` folder, a ``main.py`` file and a ``menu.xml`` file.
	
	Click on the following links for more information on them:

.. toctree::
	:maxdepth: 1
	
	package_name
	lib
	main
	menu
	model
	webpages

.. _packages_autofill:
	
autocreation of the ``packages`` folder
=======================================

	You can create a ``packages`` folder typing::
	
		gnrmkpackage packagename
	
	where ``packagename`` is the name of your package (we suggest you to call your package with the name you gave to your :ref:`genro_structure_mainproject`).
	
	Your ``packages`` folder will look like this one:
	
	.. image:: ../../../images/structure/structure-packages.png
	
	where ``myproject`` is the name of your package.
	
	.. note:: The autocreation of this folder is handled by the :class:`InstanceMaker` class.
	