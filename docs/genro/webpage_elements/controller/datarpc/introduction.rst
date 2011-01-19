.. _genro_datarpc_introduction:

=======================
Introduction to the Rpc
=======================

	The ``dataRpc`` belongs to :ref:`controllers_server` family.

	- :ref:`rpc_def`

	- :ref:`rpc_attributes`

.. _rpc_def:

Definition
==========

	The ``rpc`` family is composed by :ref:`genro_datarecord`, :ref:`genro_datarpc`, :ref:`genro_dataselection`.
	
	A Genro rpc is an inter-process communication that allows a client-server interaction.

.. _rpc_attributes:

``rpc`` common attributes
=========================

	Here we list all the common parameters of the Rpc:

	* ``_onCalling``: allows to execute a Javascript code BEFORE the controller action. Default value is ``None``
	* ``_onResult``: allows to execute a Javascript code AFTER that the controller have finished its action. Default value is ``None``
	* ``sync``: boolean; if True, Genro stops every further action until the Rpc containing ``sync=True`` finishes. Default value is ``False``
