.. _genro_structure_instances:

=========
instances
=========

	* :ref:`instances_autofill`
	* :ref:`instances_instanceconfig`

	The ``instances`` folder is... DEFINITION ???

.. _instances_autofill:

autocreation of the ``instance`` folder
=======================================

	You can create an ``instance`` folder typing::
	
		gnrmkinstance instancename -i
	
	where ``instancename`` is the name of your instance.
		
	Your ``instances`` folder will look like this one:
	
	.. image:: ../../images/structure/structure-instances.png

	We now show you the contents of these folders and files, that are:
	
	* the :ref:`instances_custom` folder
	* the :ref:`instances_data` folder
	* the :ref:`instances_instanceconfig`

.. _instances_custom:

custom
======

	???

.. _instances_data:

data
====

	???

.. _instances_instanceconfig:

instanceconfig.xml
==================

	The ``instanceconfig`` is a XML file that ... ???
	
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

	The ``_T="NN"`` is a special attribute that allow to keep track of datatypes (for more information, check the :ref:`bag_from_to_XML` section).
	
	The file begins and ends with the ``<GenRoBag>`` tag: that's because during the execution of the project, this file is being converted in a :ref:`genro_bag_intro`.
	
	CONTINUE FROM HERE!!! ???
	
..	CANCELLARE!!!
..  <?xml version='1.0' encoding='UTF-8'?>
..  <GenRoBag>
..  	<packages>
..  		<adm />
..  		<sw_base />
..  		<agenda />
..  	</packages>
..  	<db dbname="agenda" /db>
..  	<authentication pkg="adm">
..  		<py_auth defaultTags="user" pkg="adm" method="authenticate"></py_auth>
..  		<xml_auth defaultTags="users,xml">
..  			<fastolfi pwd="sh0t0st0" tags="_DEV_,admin,user,staff"/>
..  		</xml_auth>
..  	</authentication>
..  </GenRoBag>