.. _genro_structure_instances:

=========
instances
=========

	* :ref:`instances_autofill`
	* :ref:`instances_instanceconfig`

	DEF ???

.. _instances_autofill:

autofill the ``instance`` subfolder
===================================

	If your ``instances`` subfolder is empty, we suggest you to autofill it typing::
	
		gnrmkinstance instancename -i
	
	where ``instancename`` is the name of your instance.
		
	Your ``instances`` subfolder will look like this one:
	
	.. image:: ../../images/structure/structure-instances.png

	We now show you the contents of these folders and files, that are:
	
	* a :ref:`instances_custom` folder
	* a :ref:`instances_data` folder
	* an xml file called :ref:`instances_instanceconfig`

.. _instances_custom:

custom
======

.. _instances_data:

data
====

.. _instances_instanceconfig:

instanceconfig.xml
==================

	??? Add definition

	::

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