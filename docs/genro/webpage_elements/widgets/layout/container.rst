	.. _genro-layout-introduction:

================================
 Introduction to the containers
================================

	In Genro you can use layout containers to put panes (or other containers) in specific regions of your page. There are five regions: top, left, right, bottom and a mandatory center.

	As we previously said [#]_, Genro inherit its forms (containers and panes) directly from Dojo.

	The containers are:
	
	- the :ref:`genro-bordercontainer`;
	
	- the :ref:`genro-contentpane`;
	
	- the :ref:`genro-accordioncontainer`;
	
	- the :ref:`genro-stackcontainer`;
	
	- the :ref:`genro-tabcontainer`.
	
	.. _genro-layout-common-attributes:

Common attributes
=================

	There are some common attributes that you can use with ALL the containers and panes:

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``datapath``       | Set path for data. For more details,               |  ``None``                |
	|                    | check the :ref:`genro_datapath` page               |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the container.          |  ``False``               |
	|                    | For more details, check the :ref:`genro-disabled`  |                          |
	|                    | page                                               |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``height``         | Set the height of the container. You have to       |  ``100%``                |
	|                    | specify this attribute (example: height='100px')   |                          |
	|                    | whenever the container is the father container.    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the container. For more details, check the    |  ``False``               |
	|                    | :ref:`genro-hidden` page                           |                          |
	+--------------------+----------------------------------------------------+--------------------------+

**Footnotes**

.. [#] We have introduced the containers in the :ref:`genro-webpage-elements-introduction` page.