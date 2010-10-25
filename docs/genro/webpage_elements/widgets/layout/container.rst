	.. _genro-layout-introduction:

================================
 Introduction to the containers
================================

	In Genro you can use layout containers to put panes (or other containers) in specific places of your page (we call this places from now on "regions"). There are five regions: top, left, right, bottom and a mandatory center.

	Genro inherit its forms (containers and panes) directly from Dojo_.

	.. _Dojo: http://dojotoolkit.org/

	Let's analize the containers:

	- :ref:`genro-accordioncontainer`

	- :ref:`genro-bordercontainer`

	- :ref:`genro-stackcontainer`

	- :ref:`genro-tabcontainer`

	.. _genro-layout-common-attributes:

Common attributes
=================

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``datapath``       | Set path for data.                                 |  ``None``                |
	|                    | For more details, see :ref:`genro-datapath`        |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the container.          |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`        |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``height``         | Set the height of the container. You have to       |  ``100%``                |
	|                    | specify this attribute (example: height='100px')   |                          |
	|                    | whenever the container is the father container.    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the container.                                |  ``False``               |
	|                    | See :ref:`genro-hidden`                            |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	