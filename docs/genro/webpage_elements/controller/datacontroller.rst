.. _datacontroller:

==============
dataController
==============
    
    *Last page update*: |today|
    
    **type**: :ref:`client-side controller <controllers_client>`
    
    The ``dataController`` belongs to :ref:`controllers_client` family.

    * :ref:`datacontroller_def`
    * :ref:`datacontroller_examples`

.. _datacontroller_def:

Definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dataController
    
    **commons attributes**:
    
        For commons attributes (*_init*, *_onStart*, *_timing*) see controllers' :ref:`controllers_attributes`
    
.. _datacontroller_examples:

Examples
========

    We show you two different syntaxes for the ``dataController``::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = pane.borderContainer(height='200px')
                fb = bc.formbuilder(cols=2,datapath='test1')
                
                # First syntax
                fb.dataController("SET .aaa='positive number'" ,_if='shooter>=0',
                                    _else="SET .aaa='negative number'",shooter='^.x')
                fb.numberTextbox(value='^.x',lbl='x')
                fb.textbox(value='^.aaa',margin='10px',lbl='aaa')
                
                # Second syntax
                fb.dataController("""if(shooter>=0){SET .bbb='positive number';}
                                       else{SET .bbb='negative number';}""",
                                       shooter='^.y')
                fb.numberTextbox(value='^.y',lbl='y')
                fb.textbox(value='^.bbb',margin='10px',lbl='bbb')