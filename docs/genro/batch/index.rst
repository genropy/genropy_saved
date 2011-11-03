.. _batch:

=====
batch
=====
    
    *Last page update*: |today|
    
    * :ref:`batch_intro`
    * :ref:`batch_section_index`
    
.. _batch_intro:

introduction
============

    In this chapter we learn about how to create a batch in Genro.
    
    In Genropy there are three different batch types to perform different actions:
    
    #. the :ref:`action batches <action>`: perform a common batch operation
    #. the :ref:`email batches <mail>`: send emails
    #. the :ref:`print batches <print>`: create prints
    
    The base class of every batch is the :class:`BaseResourceBatch
    <gnr.web.batch.btcbase.BaseResourceBatch>` class (check the link for the complete
    methods reference)
    
    Check also the :ref:`btcbase_webpage_variables`: they are some variables through which you
    can set some basic actions for your batch (like: the batch name, the dimensions of dialogs)
    that belong to every batch (:ref:`action batches <action>`, :ref:`mail batches <mail>`
    and :ref:`print batches <print>`)
    
.. _batch_section_index:

section index
=============
    
.. toctree::
    :maxdepth: 1
    
    action/index
    mail/index
    print/index
    