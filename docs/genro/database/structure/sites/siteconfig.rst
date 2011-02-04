.. _sites_siteconfig:

===================
``sitesconfig.xml``
===================

	* :ref:`sitesconfig_description`
	* :ref:`sitesconfig_tags`: :ref:`siteconfig_wsgi`, :ref:`siteconfig_jslib`, :ref:`siteconfig_gui`, :ref:`siteconfig_dojo`
	
.. _sitesconfig_description:
	
Description of the file
=======================

	The ``sitesconfig`` is an XML file that allow to:
	
	* handle the timeout and the refresh of the connection
	* define your project port
	* import dojo and genro engines

	With the :ref:`sites_autofill` the ``siteconfig`` will look like this one::
	
		<?xml version='1.0' encoding='UTF-8'?>
		<GenRoBag>
		    <wsgi _T="NN"></wsgi>
		    <connection_timeout _T="NN"></connection_timeout>
		    <connection_refresh _T="NN"></connection_refresh>
		    <dojo _T="NN" version="11"></dojo>
		</GenRoBag>

.. _sitesconfig_tags:

Tags
====

	Let's see its content:

	* The file begins and ends with a ``<GenRoBag>`` tag: that's because during the execution of the project, this file is being converted in a :ref:`genro_bag_intro`.
	* ``<connection_timeout>``: ???.
	* ``<connection_refresh>``: ???.
	* ``<wsgi>``: allow to define some connections properties used by the :ref:`genro_wsgi`. For more information, check the :ref:`siteconfig_wsgi` paragraph.
	* ``<jslib>``: allow to specify the dojo version used. For more information, check the :ref:`siteconfig_jslib` paragraph.
	* ``<gui>``: allow to specify the CSS theme. For more information, check the :ref:`siteconfig_gui` paragraph.
	* ``<dojo``: allow to specify the Dojo version. For more information, check the :ref:`siteconfig_dojo` paragraph.
	* ``<resources>``: ???
	
.. _siteconfig_wsgi:

``<wsgi>``
==========

	It allows to define some connections properties used by the :ref:`genro_wsgi`:
	
	* ``port``: specify the port number
	* ``reload`` - boolean: if true, ... ???
	* ``debug`` - boolean: if true, ... ???
	
	This is an example of the ``<wsgi>`` tag::
	
		<wsgi port="8083" reload="true" debug="false"/>
	
.. _siteconfig_jslib:
	
``<jslib>``
===========

	It allows to specify the dojo version used.
	
	This is an example of the ``<jslib>`` tag::
	
		<jslib dojo_version="11" gnr_version='11' />

.. _siteconfig_gui:

``<gui>``
=========

	It allows to specify the CSS theme. You can choose between many theme:
	
	* `aqua`
	* `blue`
	* `elephant`
	* `pro`

	This is an example of the ``<gui>`` tag::
	
		<gui css_theme='aqua'/>

.. _siteconfig_dojo:

``<dojo>``
==========

	It allow to specify the Dojo version.
	
	Here we list its attributes:
	
	* ``version``: the version of Dojo, without the dot (example: dojo version ``1.1`` will be written as ``11``)

	This is an example of the ``<dojo>`` tag::
	
		<dojo _T="NN" version="11"></dojo>