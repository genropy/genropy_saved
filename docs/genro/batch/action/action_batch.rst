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
      
      * ``fileName`` is the name of the file that includes your action batch; the
        file must to be placed in a specified location (:ref:`action_location` section)
        
    **Example**:
    
    If you created a batch called "my_batch", then your :ref:`webpage` would begin
    with the following lines::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                pane = root.'contentPane(height='300px', datapath='my_pane')
                pane.button('Start Batch',action='PUBLISH tablehandler_run_script="action","my_batch";')
                
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

    Let's see an example of the batchUpdate passing a dict() for the *updater* attribute
    
    * Line 1 is the :ref:`action_import`
    * Line 3 is the caption of the batch
    * Line 4 includes the authorization tags: if the user logged has got one (or more)
      of the corresponding tags, then he is able to use the batch. More information
      on authorizations in the :ref:`auth` section
    * Line 5 is the batch description
    * Line 7 is the Main class instantation
    * Line 8 is a call to the do() method
    * Line 9 is a call to the batchUpdate; it includes the *updater* parameter to which
      we pass a dict(); we can pass a dict because we need to replace all the value of
      a single column with a default
      
    ::
    
        1   from gnr.web.batch.btcaction import BaseResourceAction
        2    
        3   caption = 'My batch'
        4   tags = 'user,admin'
        5   description = 'My description'
        6
        7   class Main(BaseResourceAction):
        8       def do(self):
        9           self.batchUpdate(updater=dict('issue_price' = 100))
        
.. _batchupdate_method:

batchUpdate example - method
----------------------------

    Let's see an example of the batchUpdate passing a method for the *updater* attribute
    
    * For the description of the first 8 lines, check the previous example (:ref:`batchupdate_dict`)
    * Line 9 is a call to the batchUpdate; we pass to the *updater* the updater() method
    * Line 11 is the definition of the updater() method
    * Line 12 and 13 contain the batch: in particular, they replace the values included in the
      old columns ("old_issue_price" and "old_market_price") in the new columns ("issue_price"
      and "market_price")
      
    ::
    
        1   from gnr.web.batch.btcaction import BaseResourceAction
        2   
        3   caption = 'My batch' # the batch title
        4   tags = '_DEV_'
        5   description = 'Cambia dtype 2'
        6
        7   class Main(BaseResourceAction):
        8       def do(self):
        9           self.batchUpdate(updater=self.updater)
       10           
       11       def updater(self, record):
       12           record['issue_price'] = record['old_issue_price']
       13           record['market_price'] = record['old_market_price']
       