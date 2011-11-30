.. _simpletextarea:

==============
SimpleTextarea
==============
    
    *Last page update*: |today|
    
    .. note:: SimpleTextArea features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`simpletextarea_def`
    * :ref:`simpletextarea_examples`:
    
        * :ref:`simpletextarea_examples_simple`

.. _simpletextarea_def:

Definition
==========

    .. method:: pane.simpleTextarea([**kwargs])
                
                With simpletextarea you can add an area for text
                
                * **Parameters**: *default*: Add a text to the area
                
.. _simpletextarea_examples:

Examples
========

.. _simpletextarea_examples_simple:

simple example
--------------

    * `simpleTextArea [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/simpleTextarea/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """simpleTextarea"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_simpleTextarea(self, pane):
                """simpleTextarea"""
                pane.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
                                    color='#605661', font_size='1.2em',
                                    default='A simple area to contain text')