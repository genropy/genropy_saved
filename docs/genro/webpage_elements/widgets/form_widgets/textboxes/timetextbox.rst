.. _timetextbox:

===========
TimeTextBox
===========
    
    *Last page update*: |today|
    
    .. note:: TimeTextBox features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`timetextbox_def`
    * :ref:`timetextbox_examples`:
    
        * :ref:`timetextbox_examples_simple`
        
.. _timetextbox_def:

definition
==========

    .. method:: timeTextbox([**kwargs])
                
                A timeTextbox it's a time input control that allow either typing time
                or choosing it from a picker widget
                
                * The format of the timeTextbox is ``hh:mm``
                
.. _timetextbox_examples:

Examples
========

.. _timetextbox_examples_simple:

simple example
--------------

    * `timeTextbox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/timeTextbox/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """timeTextbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_timeTextbox(self, pane):
                """timeTextbox"""
                fb = pane.formbuilder()
                fb.timeTextBox(value='^.timeTextbox', lbl='Appointment')
                