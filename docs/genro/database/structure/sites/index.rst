.. _genro_sites_index:

=====
sites
=====

	* :ref:`sites_map`
	* :ref:`sites_autofill`
	
	.. module:: gnr.app.gnrdeploy
	
	The ``sites`` folder is... DEFINITION ???
	
.. _sites_map:

``sites`` folder content list
=============================

	Inside every sites folder you will find a ``pages`` folder, a ``root`` file and a ``siteconfig`` file.
	
	Click on the following links for more information on them:
	
.. toctree::
	:maxdepth: 1
	
	sites_name
	pages
	root
	siteconfig
	
.. _sites_autofill:

autocreation of the ``sites`` folder
====================================

	You can create a ``sites`` folder typing::
	
		gnrmksite sitesname
	
	where ``sitesname`` is the name of your ``sites`` folder (that we suggest you to call as your :ref:`genro_structure_mainproject` folder).
		
	Your ``sites`` folder will look like this one:
	
	.. image:: ../../../images/structure/structure-sites.png
	
	.. note:: The autocreation of this folder is handled by the :class:`SiteMaker` class.
