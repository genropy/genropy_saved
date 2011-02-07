.. _genro_instances_index:

=========
instances
=========

	* :ref:`instances_map`
	* :ref:`instances_autofill`
	
	The ``instances`` folder is... DEFINITION ???
	
.. _instances_map:

``instances`` folder content list
=================================
	
	Inside every instance folder you will find a ``custom`` folder, a ``data`` folder and the ``instanceconfig`` file.
	
	Click on the following links for more information on them:
	
.. toctree::
	:maxdepth: 1
	
	instance_name
	custom
	data
	instanceconfig

.. _instances_autofill:

autocreation of the ``instances`` folder
========================================

	You can create an ``instances`` folder typing::
	
		gnrmkinstance instancename -i
	
	where ``instancename`` is the name of your instance (we suggest you to call your instance with the name you gave to your :ref:`genro_structure_mainproject`).
	
	Your ``instances`` folder will look like this one:
	
	.. image:: ../../../images/structure/structure-instances.png
	
	where ``myproject`` is the name of your instance.