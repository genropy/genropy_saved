.. _action_batch:

==============
action batches
==============

    *Last page update*: |today|
    
    * :ref:`action_batch_intro`
    * :ref:`action_creation`
    * :ref:`action_batch_examples`:
    
        * :ref:`action_batch_examples_batchupdate` (:ref:`examples_batchupdate_dict`,
          :ref:`examples_batchupdate_method`)
          
.. _action_batch_intro:

introduction
============

    There are some preset types of batch; you can also create your customizable batch.
    
    We first see th common features of a batch (parameters and classes to handle them)
    
    After that, we see the preset batches.
    
.. _action_creation:
    
creation of a batch
===================
    
.. _action_batch_examples:

examples
========

.. _action_batch_examples_batchupdate:

batchUpdate
===========

    add???
    
    You can use:
    
    * a dict, when you need to insert a constant value in database :ref:`columns` - check the following
      example: :ref:`examples_batchupdate_dict`
    * a method, when you need more than insert a constant value  - check the following example:
      :ref:`examples_batchupdate_method`
      
.. _examples_batchupdate_dict:

batchUpdate example - dict
--------------------------

    add???
    
.. _examples_batchupdate_method:

batchUpdate example - method
----------------------------

    add???
    
    ::
    
        # Created by Francesco Porcari on 2010-07-02.
        # Copyright (c) 2010 Softwell. All rights reserved.
        
        from gnr.web.batch.btcaction import BaseResourceAction
        import time
        
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
                