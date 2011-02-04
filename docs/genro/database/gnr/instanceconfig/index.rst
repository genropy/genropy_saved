.. _genro_gnr_instanceconfig:

==================
``instanceconfig``
==================

	The ``instanceconfig`` folder includes a single file: ``default.xml``
	
.. _genro_gnr_instanceconfig_default:
	
``default.xml``
===============

	The ``default.xml`` of the ``.gnr/instanceconfig`` folder set the default values of your :ref:`instances_instanceconfig` files.
	
	You can obviously redefine the values of the ``instanceconfig`` file for every project you make, setting the features directly in the :ref:`instances_instanceconfig` of the specific project.
	
	Let's see its structure::
	
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
	
	We remind the detailed explanations of the various tags on the :ref:`instances_instanceconfig` documentation page.