.. _numberspinner:

=============
NumberSpinner
=============
    
    *Last page update*: |today|
    
    .. note:: NumberSpinner features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`numberspinner_def`
    * :ref:`numberspinner_examples`
    
.. _numberspinner_def:

definition
==========

    .. method:: pane.numberspinner([**kwargs])
    
                numberSpinner is similar to :ref:`numbertextbox`, but makes integer entry easier
                when small adjustments are required
                
                * **Parameters**:
                
                                  * **min**: set the minimum value of the numberSpinner
                                  * **max**: set the maximum value of the numberSpinner
                                  
    There are two features:
    
        * The down and up arrow buttons "spin" the number up and down.
        * Furthermore, when you hold down the buttons, the spinning accelerates to
          make coarser adjustments easier
          
.. _numberspinner_examples:

examples
========

    * `numberSpinner [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/numberspinner/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`data`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Numberspinner"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_numberSpinner(self, pane):
                """numberSpinner"""
                fb = pane.formbuilder()
                fb.data('.number',1)
                fb.div('Try to hold down a button: the spinning accelerates to make coarser adjustments easier.')
                fb.div('A lower limit of \'-10\' is set')
                fb.numberSpinner(value='^.number', min=-10, lbl='number')