.. _datetextbox:

===========
DateTextbox
===========
    
    *Last page update*: |today|
    
    .. note:: DateTextbox features:
    
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`datetextbox_def`
    * :ref:`datetextbox_examples`:
    
        * :ref:`datetextbox_examples_simple`
        
.. _datetextbox_def:

definition
==========

    .. method:: dateTextbox([**kwargs])
    
                A dateTextbox is a easy-to-use date entry controls that allow either
                typing or choosing a date from any calendar widget
                
                The data format type depends on the locale parameters of your browser. For example,
                with the ``en`` locale it is set to ``mm/dd/yyyy``
                  
                * **Parameters**: **popup**: allow to show a calendar dialog. Default value is ``True``
                
                  .. image:: ../../../../_images/widgets/datetextbox.png
                  
.. _datetextbox_examples:

Examples
========

.. _datetextbox_examples_simple:

simple example
--------------

    * `datetextbox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/dateTextbox/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dateTextbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self, pane):
                """simple dateTextbox"""
                fb = pane.formbuilder()
                fb.dateTextbox(value='^.date', lbl='Date')
                