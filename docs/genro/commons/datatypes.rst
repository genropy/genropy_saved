.. _datatype:

=====
dtype
=====
    
    *Last page update*: |today|
    
    * :ref:`datatype_format`:
    
        * :ref:`datatype_a`
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

.. _datatype_a:

A dtype
-------

    TODO

.. _datatype_c:

C dtype
-------

    Character type.
    
.. _datatype_d:

D dtype
-------

    Date type. Use the ``datetime.date()`` Python module syntax
    
    Example::
    
        datetime.date(2011, 10, 10)
        
.. _datatype_dh:

DH dtype
--------

    DateHour type. Use the ``datetime.datetime.now()`` Python module syntax
    
.. _datatype_h:

H dtype
-------

    Hour type. Use the ``datetime.time()`` Python module syntax
    
    Example::
    
        datetime.time(4, 5)
        
.. _datatype_i:

I dtype
-------

    Integer type.
    
    Example::
    
        1223
        
.. _datatype_l:

L dtype
-------

    Long integer type
    
    Example::
    
        48205294
        
.. _datatype_r:

R dtype
-------

    Float number type.
    
    Example::
    
        34567.67
        
.. _datatype_t:

T dtype
-------

    Text type.
    
.. _datatype_x:

X dtype
-------

    XML or :ref:`bag` type.
    
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

    You can build your own datatype. For more information, check the
    :ref:`methods_custom_type` method
    