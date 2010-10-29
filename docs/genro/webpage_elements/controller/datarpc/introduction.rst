	.. _genro-datarpc-introduction:

=========================
 Introduction to the Rpc
=========================

	:ref:`rpc-description`

	:ref:`rpc-common-attributes`

	.. _rpc-description:

Description
===========

	The ``dataRpc`` are ???

	.. _rpc-common-attributes:

Rpc common attributes
=====================

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``method``         | MANDATORY - name of the dataRpc                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onCalling``     | allows to execute a Javascript code BEFORE the     |  ``None``                |
	|                    | controller action                                  |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onResult``      | allows to execute a Javascript code AFTER when the |  ``None``                |
	|                    | controller finished its action                     |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``sync``           | boolean; ???                                       |  ``False``               |
	+--------------------+----------------------------------------------------+--------------------------+