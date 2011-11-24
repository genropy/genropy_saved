.. _checkbox:

========
CheckBox
========
    
    *Last page update*: |today|
    
    .. note:: CheckBox features:
    
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`checkbox_def`
    * :ref:`checkbox_examples`:
    
        * :ref:`checkbox_examples_simple`
        
.. _checkbox_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkbox
    
.. _checkbox_examples:

examples
========

.. _checkbox_examples_simple:

simple example
--------------

    * `checkbox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/checkbox/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Checkbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self, pane):
                """Checkbox"""
                labels = 'First,Second,Third'
                labels = labels.split(',')
                pane = pane.formbuilder()
                for label in labels:
                    pane.checkbox(value='^.%s_checkbox' % label, label=label)