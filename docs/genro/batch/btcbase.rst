.. _btcbase:

==========
base batch
==========

    * :ref:`btcbase_intro`
    * :ref:`btcbase_webpage_variables`
    
.. _btcbase_intro:

introduction
============

    We have previously said that every batch import from a base batch class called
    :ref:`btcbase_base` class.
    
    For the complete library reference, check the :ref:`library_btcbase` section.
    
    In this section we list all the :ref:`btcbase_webpage_variables`, that belong
    to every batch (:ref:`action`, :ref:`mail` and :ref:`print`)
    
.. _btcbase_webpage_variables:

btcbase - webpage variables
===========================
    
    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize the class to which they belong (in this case, the
    BaseResourceBatch class). They are:
    
    * :ref:`batch_cancellable`
    * :ref:`batch_delay`
    * :ref:`batch_note`
    * :ref:`batch_prefix`
    * :ref:`batch_steps`
    * :ref:`batch_thermo_lines`
    * :ref:`batch_title`
    * :ref:`base_dialog_height`
    * :ref:`base_dialog_width`
    * :ref:`virtual_columns`
    
.. _batch_cancellable:

batch_cancellable
-----------------

    add???
    
.. _batch_delay:

batch_delay
-----------
    
    A string with the time milliseconds start delay
    
.. _batch_note:

batch_note
----------

    Allow to add a note to the batch.
    
    In the :ref:`prints <print>` the "batch_title" adds a default note to the
    :ref:`print_setting_dialog_notes` of the :ref:`print_setting_dialog`
    
.. _batch_prefix:

batch_prefix
------------
    
    A string with a prefix for the batch name
      
      **Example**::
      
        batch_prefix = 'st_prest'
        
.. _batch_steps:

batch_steps
-----------

    add???
    
.. _batch_thermo_lines:

batch_thermo_lines
------------------

    add???
    
.. _batch_title:

batch_title
-----------
        
    A string with the batch title.
    
    In the :ref:`prints <print>` the "batch_title" is the title of the :ref:`print_setting_dialog`
    
.. _base_dialog_height:

dialog_height
-------------

    Define the height of the batch dialog
    
.. _base_dialog_width:

dialog_width
------------

    Define the width of the batch dialog
    
.. _virtual_columns:

virtual_columns
---------------

    add???
