.. _toolbar:

=======
toolbar
=======

    *Last page update*: |today|
    
    .. note:: toolbar features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`toolbar_def`
    
.. _toolbar_def:

definition
==========

    .. method:: pane.toolbar([**kwargs])
    
    .. _previous_image:
    
    .. image:: ../../_images/widgets/toolbars/toolbar.png
    
    In Dojo, the Dojo toolbar is a container for buttons. Any button-based Dijit component can be
    placed on the toolbar, DropDownButtons.
    
    In Genro, the Dojo toolbar is a container for any :ref:`form widget <form_widgets>` (like
    :ref:`buttons`, :ref:`textboxes_index`...)
    
    The only mandatory parameter is the *height* parameter
    
examples
========

    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                tb = root.toolbar(height='20px')
                fb = tb.formbuilder(cols=8, border_spacing=0)
                for i in ('icnBaseAdd', 'icnBuilding', 'icnBaseCalendar',
                          'icnBuddy', 'queryMenu', 'icnBuddyChat'):
                    fb.slotButton('tooltip', iconClass=i)
                fb.textbox()
                fb.button('save', action='alert("Saving!")')