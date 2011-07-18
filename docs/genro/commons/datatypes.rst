.. _genro_datatype:

=====
dtype
=====
    
    *Last page update*: |today|
    
    * :ref:`datatype_format`:
    
        * :ref:`datatype_c`
        * :ref:`datatype_d`
        * :ref:`datatype_dh`
        * :ref:`datatype_h`
        * :ref:`datatype_i`
        * :ref:`datatype_l`
        * :ref:`datatype_r`
        * :ref:`datatype_t`
        * :ref:`datatype_x`
        
    * :ref:`datatype_custom`
    
    We list here all the datatypes (``dtypes``) you can use for your data. You can also create
    your own :ref:`datatype_custom`.
    
.. _datatype_format:

dtypes format
=============
    
.. _datatype_c:

C dtype
-------

    add???
    
..    #   C       char (can be omitted; you have to specify its size)
    
.. _datatype_d:

D dtype
-------

    add???
    
..    #   D       date

.. _datatype_dh:

DH dtype
--------

    add???
    
..    #   DH      datetime
    
.. _datatype_h:

H dtype
-------

    add???
    
..    #   H       time
    
.. _datatype_i:

I dtype
-------

    add???
    
..    #   I       integer
    
.. _datatype_l:

L dtype
-------

    add???
    
..    #   L       long integer
    
.. _datatype_r:

R dtype
-------

    add???
    
..    #   R       float
    
.. _datatype_t:

T dtype
-------

    add???
    
..    #   T       text (can be omitted; you must not specify its size)
    
.. _datatype_x:

X dtype
-------

    add???
    
..    #   X       XML/Bag
    
.. _datatype_dt:

DT dtype
--------

    The ``DT`` type is a Genro type. Its format is::
    
        yyyy-mm-dd T hh:mm:ss.decimals
        
    where ``yyyy-mm-dd`` is the "year-month-day" format date, ``T`` is a separator, ``hh:mm:ss``
    is the "hour-minute-second" format hour (followed by the decimals of seconds)
    
.. _datatype_custom:

custom type
===========

    You can build your own datatype. For more information, check the :ref:`methods_custom_type`
    documentation section of the ``custom_type`` method.
    