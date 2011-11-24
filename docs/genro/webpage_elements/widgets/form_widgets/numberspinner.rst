.. _numberspinner:

=============
NumberSpinner
=============
    
    *Last page update*: |today|
    
    .. note:: NumberSpinner features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`numberspinner_def`
    * :ref:`numberspinner_description`
    * :ref:`numberspinner_attributes`
    * :ref:`numberspinner_examples`
    
.. _numberspinner_def:

definition
==========

    .. method:: pane.numberspinner([**kwargs])
    
.. _numberspinner_description:

description
===========
    
    numberSpinner is similar to :ref:`numbertextbox`, but makes integer entry easier
    when small adjustments are required.
    
    There are two features:
    
        * The down and up arrow buttons "spin" the number up and down.
        * Furthermore, when you hold down the buttons, the spinning accelerates to
          make coarser adjustments easier.
        
.. _numberspinner_attributes:

attributes
==========

    **numberspinner attributes**:
    
    * *min*: set the minimum value of the numberSpinner
    * *max*: set the maximum value of the numberSpinner
    
.. _numberspinner_examples:

examples
========

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root	.formbuilder(datapath='test1',cols=2)
                fb.numberSpinner(value='^.number',min=0,lbl='number')
                fb.div("""Try to hold down a button: the spinning accelerates to make coarser
                          adjustments easier""", font_size='.9em',text_align='justify',margin='5px')