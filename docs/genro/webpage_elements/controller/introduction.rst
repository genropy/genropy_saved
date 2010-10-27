	.. _genro-controllers-introduction:

=================================
 Introduction to the controllers
=================================

	The Genro controllers allow to execute a script.

	.. note:: we recommend you in reading :ref:`genro-webpage` before.

	*Client-side controllers*:
	
	The client-side controllers work on client through Javascript code; they are:

	- :ref:`genro-datacontroller`
	- :ref:`genro-dataformula`
	- :ref:`genro-datascript` (deprecated)
	
	*Server-side controllers*:
	
	The server-side controllers work on server, so they use python code; they are:

	- dataRecord ???
	
	- :ref:`genro-datarpc`
	
	- dataSelection ???

	We emphasize that all the controllers can be attached to every Genro object.

Common attributes
=================

	Let's see all the controllers' common attributes:

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``_init``          | Boolean; if True, the controller is executed when  |  ``False``               |
	|                    | when the line containing ``_init`` is read         |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onresult``      | Boolean; if True, ... ??? #NISO                    |  ``False``               |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onstart``       | Boolean; if True, FIRST all the line codes are     |  ``False``               |
	|                    | read, THEN the controller containing ``_onresult`` |                          |
	|                    | is executed                                        |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_timing``        | number; this attribute allows to choose the        |  ``???``                 |
	|                    | controller response time (milliseconds)            |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	