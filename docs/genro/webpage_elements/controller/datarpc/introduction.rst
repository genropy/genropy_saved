.. _datarpc_introduction:

=======================
Introduction to the Rpc
=======================
    
    *Last page update*: |today|
    
    The ``Rpc`` belongs to :ref:`controllers_server` family.
    
    * :ref:`rpc_def`
    * :ref:`rpc_attributes`
    
.. _rpc_def:

Definition
==========

    A Genro rpc is an inter-process communication that allows a client-server interaction.
    
    The ``rpc`` family is composed by:
    
    * :ref:`datarecord`
    * :ref:`datarpc`
    * :ref:`dataselection`.
    
.. _rpc_attributes:

``rpc`` commons attributes
==========================

    Here we list all the common parameters of the Rpc:
    
    * *_onCalling*: allows to execute a javascript code BEFORE the controller action.
      Default value is ``None``
    * *_onResult*: allows to execute a javascript code AFTER that the controller have
      finished its action. Default value is ``None``
    * *sync*: boolean. If True, Genro stops every further action until the Rpc containing
      ``sync=True`` finishes. Default value is ``False``