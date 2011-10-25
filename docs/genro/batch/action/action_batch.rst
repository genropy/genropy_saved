.. _action_batch:

==============
action batches
==============

    *Last page update*: |today|
    
    * :ref:`action_batch_intro`
    * :ref:`action_location`
    
    * :ref:`action_creation`
    
        * :ref:`action_import`
        * :ref:`action_main`
        
    * :ref:`action_start`
    * :ref:`batchupdate`:
    
        * :ref:`batchupdate_dict`
        * :ref:`batchupdate_method`
        
.. _action_batch_intro:

introduction
============

    There are some preset types of batch; you can also create your customizable batch.
    
    We first see the common features of a batch (parameters and classes to handle them,
    location of the file...); after that, we see the preset batches
    
.. _action_location:

file location
=============
    
    The location of the action batch file must follow this path::
    
        projectName/packages/packageName/resources/tables/tableName/action/fileName
        
    where:
    
    * ``projectName`` is the name of the :ref:`project`
    * ``packages`` is the :ref:`packages` folder
    * ``packageName`` is the name of the package
    * ``resources`` is the :ref:`public_resources` folder
    * ``tables`` is the :ref:`resources_tables` folder
    * ``tableName`` is the name of the :ref:`table` to which the action batch is linked
    * ``fileName`` is the name you choose for the file containing the action batches
      (there is any convention about it)
    
    This is a graphical map of the location of the file into a :ref:`project`:
    
    .. image:: ../../_images/projects/packages/tables_action.png
    
.. _action_creation:
    
Creation of the file
====================
    
.. _action_import:

import
------

    In order to create an action batch you have to import in your file
    the :class:`BaseResourceAction <gnr.web.batch.btcaction.BaseResourceAction>`
    class::
    
        from gnr.web.batch.btcaction import BaseResourceAction
        
    Then you have to create the Main class:
    
.. _action_main:

Main class
----------

    The Main class inherits from the :class:`BaseResourceAction
    <gnr.web.batch.btcaction.BaseResourceAction>` class, so write::
    
        class Main(BaseResourceAction):
        
    .. note:: The ``BaseResourceAction`` class is actually empty, and inherits from the
              :class:`BaseResourceBatch <gnr.web.batch.btcbase.BaseResourceBatch>` class
              
    For a complete description of all the available methods, check the
    :ref:`gnr.web.batch.btcbase <library_btcbase>` page
    
.. _action_start:

start an action batch
=====================

    .. note:: if you use the :ref:`th` component you have also a "batch start" management
              system (it is the "Batch" button of the :ref:`th_query_actions`).
              So, you don't need to create any button that allows to start a batch.
              Continue the reading of this section if you are not using the TableHandler
              
    To start a batch from a :ref:`webpage`, you may create a :ref:`button` using the
    :ref:`action_attr` attribute that performs a :ref:`publish`.
    
    Create your button remembering that:
    
    * the first attribute is the button label
    * the *action* attribute must call a PUBLISH that follows this syntax::
    
        action = 'PUBLISH tablehandler_run_script="action", "fileName"'
        
      where:
      
      * ``fileName`` is the name of the file that includes your action batch; this
        file must be placed in the following place... add???
        
    **Example**:
    
        add???
    
.. _batchupdate:

batchUpdate
===========

    .. automethod:: gnr.web.batch.btcbase.BaseResourceBatch.batchUpdate
    
    You can use:
    
    * a dict, when you need to insert a constant value in database :ref:`columns` - check the following
      example: :ref:`batchupdate_dict`
    * a method, when you need more than insert a constant value  - check the following example:
      :ref:`batchupdate_method`
      
.. _batchupdate_dict:

batchUpdate example - dict
--------------------------

    add???
    
.. _batchupdate_method:

batchUpdate example - method
----------------------------

    add???
    
    ::
    
        # Created by Francesco Porcari on 2010-07-02.
        # Copyright (c) 2010 Softwell. All rights reserved.
        
        from gnr.web.batch.btcaction import BaseResourceAction
        
        caption = 'Cambia dtype 1' # the batch title
        tags = '_DEV_'
        description = 'Cambia dtype 2'
        
        class Main(BaseResourceAction):
            batch_prefix = 'DT'
            batch_title = 'Dtype'
            batch_cancellable = False
            batch_delay = 0.5
            
            def do(self):
                self.batchUpdate(updater=self.updater)
            
            def updater(self, record):
                record['issue_price'] = record['old_issue_price']
                record['market_price'] = record['old_market_price']
                