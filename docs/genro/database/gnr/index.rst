.. _genro_gnr_index:

========
``.gnr``
========

.. _gnr_introduction:

introduction
============

	The ``.gnr`` folder includes the Genro's management files.
	
	.. note:: some files use the XML extension because the XML format is perfect for the conversion to the :ref:`genro_bag_intro` and vice versa (for more information, check the :ref:`bag_from_to_XML` paragraph).

.. _gnr_contents:

``.gnr`` contents
=================

	The hidden ``.gnr`` folder has the following tree structure:

	.. image:: ../../images/gnr.png

	Where:

	* The :ref:`gnr_environment` allow to define the root for your :ref:`genro_structure_mainproject` folders.
	* The :ref:`genro_gnr_instanceconfig_default` of the ``instanceconfig`` folder set the default values for every :ref:`instances_instanceconfig` file of your projects.
	* The :ref:`genro_gnr_siteconfig_default` of the ``siteconfig`` folder set the default values for every :ref:`sites_siteconfig` file of your projects.
	
	.. note:: you can redefine your ``instanceconfig`` and your ``sitesconfig`` XML files in your projects. If you don't modify them, Genro takes as default parameters the ones defined in the two ``default.xml`` file of the ``.gnr`` folder.

Index of .gnr files
===================
	
	Click on the link below for more information on ``.gnr`` files:

.. toctree::

	environment
	instanceconfig/index
	siteconfig/index