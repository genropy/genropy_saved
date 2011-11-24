.. _togglebutton:

============
ToggleButton
============
    
    *Last page update*: |today|
    
    .. note:: ToggleButton features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`togglebutton_def`
    * :ref:`togglebutton_examples`:
    
        * :ref:`togglebutton_examples_basic`
    
.. _togglebutton_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.togglebutton
    
.. _togglebutton_examples:

examples
========

.. _togglebutton_examples_basic:

simple example
--------------

    * `togglebutton [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/buttons/togglebutton/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                
    * **Code**::

        # -*- coding: UTF-8 -*-
        """Toggle buttons"""
        
        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
        
            def test_1_basic(self, pane):
                """Simple test"""        
                pane.togglebutton(value='^.toggle', iconClass="dijitRadioIcon", label='A togglebutton')