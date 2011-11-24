.. _datarpc_index:

============
the dataRpcs
============
    
    *Last page update*: |today|
    
    * :ref:`rpc_def`
    * :ref:`rpc_attributes`
    * :ref:`rpc_section_index`
    
.. _rpc_def:

definition
==========

    A Genro rpc is an inter-process communication that allows a client-server interaction.
    
    The ``dataRpc`` family is composed by:
    
    * :ref:`datarecord`
    * :ref:`datarpc`
    * :ref:`dataselection`
    
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
      
.. _rpc_section_index:

section index
=============
      
.. toctree::
    :maxdepth: 1
    :numbered:
    
    attributes
    datarpc
    datarecord
    dataselection