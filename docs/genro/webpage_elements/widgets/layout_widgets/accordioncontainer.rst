.. _accordioncontainer:

==================
AccordionContainer
==================
    
    *Last page update*: |today|
    
    .. note:: AccordionContainer features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`accordion_def`
    * :ref:`accordion_examples`:
    
        * :ref:`accordion_examples_simple`
    
.. _accordion_def:

definitions
===========

    * **accordionContainer definition**:
    
      .. method:: pane.accordionContainer([**kwargs])
      
      Like :ref:`stackcontainer` and :ref:`tabcontainer`, an accordionContainer holds a set
      of accordionPanes whose titles are all visible, but only one pane's content is visible at a
      time. Clicking on a pane title slides the currently-displayed one away, similar to a garage door
      
    * **accordionPane definition**:
      
      .. method:: pane.accordionPane([**kwargs])
      
                  **Parameters**: **title**: MANDATORY. Set the accordionPane's title
                
.. _accordion_examples:

examples
========

.. _accordion_examples_simple:

simple example
--------------

    * `accordionContainer [basic] <http://localhost:8080/webpage_elements/widgets/layout/accordioncontainer/1>`_
      
      .. note:: example elements' list:

                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Accordion container"""
        
        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_1_basic(self, pane):
                """Basic accordion container"""
                ac = pane.accordionContainer(height='300px', selected='^selected')
                ap1 = ac.accordionPane(title='Pane one')
                ap1.div("""Click on the "Pane three"!""",
                        font_size='.9em', text_align='justify', margin='10px')
                ap2 = ac.accordionPane(title='Pane two')
                ap3 = ac.accordionPane(title='Pane three')
                ap3.div("""The content of a pane will be shown when user chooses the corresponding pane.""",
                        font_size='.9em', text_align='justify', margin='10px')