.. _dbselect:

========
dbSelect
========
    
    *Last page update*: |today|
    
    .. note:: dbSelect features:
              
              * **Type**: :ref:`Genro form widget <genro_form_widgets>`
              * **Common attributes**: you can check:
              
                * the :ref:`widget common attributes section <attributes_index>`
                * the :ref:`dbSelect and dbCombobox common attributes section <db_attributes>`
              
    * :ref:`dbselect_def`
    * :ref:`dbselect_examples`:
    
        * :ref:`dbselect_examples_simple`
        * :ref:`dbselect_examples_condition`

.. _dbselect_def:

Definition and Description
==========================

    .. automethod:: gnr.web.gnrwebpage_proxy.apphandler.GnrWebAppHandler.dbSelect
    
.. _dbselect_examples:

Examples
========

.. _dbselect_examples_simple:

simple example
--------------

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1',cols=2)
                fb.dbSelect(dbtable='showcase.person',rowcaption='$name',
                            value='^.person_id',lbl='Star')
                            
.. _dbselect_examples_condition:

condition example
-----------------

    For an example please check the :ref:`sql_condition` example