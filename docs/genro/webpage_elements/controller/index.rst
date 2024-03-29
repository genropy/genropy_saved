.. _controllers:

===========
controllers
===========
    
    *Last page update*: |today|
    
    * :ref:`controllers_intro`
    * :ref:`controllers_client`, :ref:`controllers_server`
    * :ref:`controllers_section_index`
    
.. _controllers_intro:

introduction
============

    The Genro controllers receive inputs and initiate a response by making calls on model objects.
    
    We emphasize that all the controllers can be attached to every Genro object
    
    The controllers can be divided in two groups:
    
    * the :ref:`controllers_client`
    * the :ref:`controllers_server`
    
.. _controllers_client:

client-side controllers
-----------------------

    A client-side controller works on the client through javascript; they are:
    
    * :ref:`datacontroller`: allow to execute javascript code
    * :ref:`dataformula`: allow to insert a value into a specific address of the
      :ref:`datastore` calculated through a formula
    * :ref:`datascript` (*deprecated*)
    
.. _controllers_server:

server-side controllers
-----------------------

    A server-side controller works on the server thorugh Python; they are:
    
    * :ref:`data`: used to define variables from server to client
    * :ref:`datarecord`: TODO
    * :ref:`dataremote`: synchronous rpc
    * :ref:`dataresource`: TODO
    * :ref:`datarpc`: allow the client to make a call to the server to perform an action.
    * :ref:`dataselection`: TODO
    
.. _controllers_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    :numbered:
    
    data
    datacontroller
    dataformula
    dataremote
    dataresource
    dataRpcs: dataRecord, dataRpc, dataSelection <datarpc/index>
    datascript
    