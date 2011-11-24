.. _toolbar:

=======
toolbar
=======

    *Last page update*: |today|
    
    .. note:: toolbar features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    .. _previous_image:
    
    *In the image, a toolbar*
    
    .. image:: ../../../_images/widgets/toolbars/toolbar.png
    
    * :ref:`toolbar_def`
    * :ref:`toolbar_examples`:
    
        * :ref:`toolbar_examples_simple`
        
.. _toolbar_def:

definition
==========

    .. method:: pane.toolbar([**kwargs])
    
    In Dojo, the Dojo toolbar is a container for buttons. Any button-based Dijit component can be
    placed on the toolbar, DropDownButtons.
    
    In Genro, the Dojo toolbar is a container for any :ref:`form widget <form_widgets>` (like
    :ref:`buttons`, :ref:`textboxes_index`...)
    
    The only mandatory parameter is the *height* parameter
    
.. _toolbar_examples:

examples
========

.. _toolbar_examples_simple:

simple example
--------------

    * `toolbar [basic] <http://localhost:8080/webpage_elements/widgets/toolbars/toolbar/1>`_

      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`button`, :ref:`contentpane`, :ref:`formbuilder`,
                  :ref:`slotbutton`, :ref:`textbox`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Dojo toolbar"""
        
        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
            
            def test_0_basic(self, pane):
                """Basic example"""
                tb = pane.toolbar(height='20px')
                fb = tb.formbuilder(cols=8, border_spacing=0)
                for i in ['icnBaseAdd', 'icnBuilding', 'icnBaseCalendar',
                          'icnBuddy', 'queryMenu', 'icnBuddyChat']:
                    fb.slotButton('tooltip', iconClass=i, action='alert("Performing an action...")')
                fb.textbox()
                fb.button('save', action='alert("Saving!")')