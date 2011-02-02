.. _instances_instanceconfig:

======================
``instanceconfig.xml``
======================

	The ``instanceconfig`` is an XML file that allow to:
	
	* ???
	* ???
	* ???
	
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

	Let's see its content:

	* The file begins and ends with the ``<GenRoBag>`` tag: that's because during the execution of the project, this file is being converted in a :ref:`genro_bag_intro`.
	* The ``<packages>`` tag allow to include any other package from other projects; Genro will search it through its mixin tecnique. For more information, check the :ref:`instances_packages` paragraph.
	* The ``<db>`` tag includes the name of your database. For more information, check the :ref:`instances_db` paragraph.
	* The ``<authentication>`` tag allow to handle all the access authorization to your project. You have to introduce a support tag called ``<py_auth>`` too. Check the :ref:`instances_auth_py` paragraph for more information.
	* The ``_T="NN"`` is a special attribute that allow to keep track of datatypes (for more information, check the :ref:`bag_from_to_XML` section).

.. _instances_packages:

``<packages>``
==============

	In the ``<packages>`` tag you have at least put your main package, that is the one where you put your ``model`` and ``webpages`` folders, like::
	
		<packages>
		    <mypackage />
		</packages>
	
	where ``mypackage`` is the name of your main package.
	
	You can include more than one package, and you can include any packages you have in the Genro folders, like::
	
		<packages>
		    <mypackage />
		    <adm />
		    <glbl />
		</packages>
	
	This allow you to use every :ref:`packages_model` of the packages you've imported.
	
	In particular:
	
		* the ``adm`` package includes some useful tools for the customers management
		* the ``glbl`` package includes some useful tools for the management of countries, provinces, regions and towns
	
	You can find these two packages (and more others!) in the ``$GNRHOME/packages`` folder.
	
.. _instances_db:

``<db>``
========

	bla bla
	
.. _instances_auth_py:

``<auth> and <py>``
===================

	bla bla
