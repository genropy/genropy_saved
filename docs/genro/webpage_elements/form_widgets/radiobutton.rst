.. _radiobutton:

===========
RadioButton
===========
    
    *Last page update*: |today|
    
    .. note:: RadioButton
              
              * **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`rb_def`
    * :ref:`rb_examples`: :ref:`rb_examples_group`
    
.. _rb_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.radiobutton
    
.. _rb_examples:

examples
========

.. _rb_examples_group:

group example
-------------

    Let's see a simple example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=root.contentPane(title='Buttons',datapath='test1').formbuilder(cols=3,border_spacing='10px')
                
                fb.radiobutton(value='^.radio.jazz',group='music',label='Jazz')
                fb.radiobutton(value='^.radio.rock',group='music',label='Rock')
                fb.radiobutton(value='^.radio.blues',group='music',label='Blues')
                
                fb.div('Sex')
                fb.radiobutton(value='^.sex.male',group='my_group',label='M')
                fb.radiobutton(value='^.sex.female',group='my_group',label='F')
