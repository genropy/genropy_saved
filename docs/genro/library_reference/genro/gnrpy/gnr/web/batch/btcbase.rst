.. _library_btcbase:

===========================================
:mod:`gnr.web.batch.btcbase` - base batches
===========================================
    
    *Last page update*: |today|
    
    **Classes:**
    
    * :ref:`btcbase_base`
    * :ref:`btcbase_webpage_variables`
    
    **Complete reference:**
    
    * :ref:`btcbase_classes`
    
.. _btcbase_base:

:class:`BaseResourceBatch`
==========================

    .. module:: gnr.web.batch.btcbase.BaseResourceBatch
    
    ========================== =========================== =============================
    :meth:`batchUpdate`        :meth:`get_records`          :meth:`pre_process`         
    :meth:`defineSelection`    :meth:`get_selection`        :meth:`result_handler`      
    :meth:`do`                 :meth:`get_selection_pkeys`  :meth:`run`                 
    :meth:`get_record`         :meth:`get_step_caption`     :meth:`storeResult`         
    :meth:`get_record_caption` :meth:`parameters_pane`                                  
    ========================== =========================== =============================
    
.. _btcbase_webpage_variables:

BaseResourceBatch - webpage variables
=====================================
    
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

    If ``True``, allow to stop the batch during its execution
    
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
    
    A string with a prefix for the batch name.
      
      **Example**::
      
        batch_prefix = 'st_prest'
        
.. _batch_steps:

batch_steps
-----------

    TODO
    
.. _batch_thermo_lines:

batch_thermo_lines
------------------

    TODO
    
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

    TODO
    
.. _btcbase_classes:

:mod:`gnr.web.batch.btcbase` - The complete reference list
==========================================================

.. automodule:: gnr.web.batch.btcbase
    :members:
