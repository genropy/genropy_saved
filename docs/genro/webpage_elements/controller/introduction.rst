	.. _genro-controllers-introduction:

=================================
 Introduction to the controllers
=================================

	The Genro controllers receive inputs and initiate a response by making calls on model objects.

	We emphasize that all the controllers can be attached to every Genro object.

	.. note:: we recommend you to read :ref:`genro-webpage` before reading this paragraph.

	.. _genro-client-side-controllers:

client-side controllers
=======================

	The client-side controllers work on client through Javascript code; they are:

	- :ref:`genro-datacontroller`
	- :ref:`genro-dataformula`
	- :ref:`genro-datascript` (deprecated)

	.. _genro-server-side-controllers:

server-side controllers
=======================

	The server-side controllers work on server, so they use python code; they are:

	- dataRecord ???

	- :ref:`genro-datarpc`

	- dataSelection ???

Common attributes
=================

	Let's see all the controllers' common attributes:

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``_init``          | Boolean; if True, the controller is executed when  |  ``False``               |
	|                    | when the line containing ``_init`` is read         |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onStart``       | Boolean; if True, FIRST all the line codes are     |  ``False``               |
	|                    | read, THEN the controller containing ``_onresult`` |                          |
	|                    | is executed                                        |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_timing``        | number (seconds); the controller will be triggered |  ``None``                |
	|                    | every "x" seconds, where "x" is the number defined |                          |
	|                    | in this attribute                                  |                          |
	+--------------------+----------------------------------------------------+--------------------------+
