.. _checkboxtext:

============
checkBoxText
============

    *Last page update*: |today|
    
    .. note:: checkBoxText features:
              
              * **Type**: :ref:`Genro form widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`checkboxtext_def`
    * :ref:`checkboxtext_examples`:
    
        * :ref:`checkboxtext_examples_simple`
        
.. _checkboxtext_def:

definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkboxtext
    
.. _checkboxtext_examples:

Examples
========

.. _checkboxtext_examples_simple:

simple example
--------------

    * `checkboxtext [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/checkboxtext/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`, :ref:`simpletextarea`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """checkBoxText"""

        class GnrCustomWebPage(object):
            py_requires="gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self,pane):
                """checkboxtext"""
                pane.checkBoxText('name,surname,address',value='^.foo',separator=' - ')
                pane.simpleTextarea(value='^.foo')