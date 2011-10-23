.. _action_batch:

==============
action batches
==============

    :ref:`action_batch_intro`
    
.. _action_batch_intro:

introduction
============

    add???
    
.. _action_batch_examples:

examples
========

.. _action_batch_examples_batchupdate:

batchUpdate
===========

    add???
    
    You can use:
    
    * a dict, when ... add??? - :ref:`examples_batchupdate_dict`
    * a method, when ... add??? - :ref:`examples_batchupdate_method`
    
.. _examples_batchupdate_dict:

batchUpdate - dict
------------------

    add???

.. _examples_batchupdate_method:

batchUpdate - method
--------------------

    ::
    
        # Created by Francesco Porcari on 2010-07-02.
        # Copyright (c) 2010 Softwell. All rights reserved.
        
        from gnr.web.batch.btcaction import BaseResourceAction
        import time
        
        caption = 'Cambia dtype 1' # ciò che viene visualizato nel th come titolo del batch
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
                record['prezzo_emissione'] = record['prezzo_emissione_old']
                record['prezzo_rimborso'] = record['prezzo_rimborso_old']