.. _slotbutton:

==========
slotButton
==========

    *Last page update*: |today|
    
    .. note:: slotButton features:
    
              * **Type**: :ref:`Genro form widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`slotbutton_def`
    * :ref:`slotbutton_examples`
    
.. _slotbutton_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.slotButton
    
.. _slotbutton_examples:

examples
========

    **Example**:
    
    This is the standard usage of the slotButton: the label works only as the slotbutton's
    tooltip (so the button will not have a real label). Eventually you can add the *action*
    attribute to perform an action through Javascript::
    
        pane.slotButton(label='I\'m a slotButton', iconClass="icnBuilding")
        
    **Example**:
    
    Some ways to create buttons and slotButtons::
    
        fb = pane.formbuilder(cols=3)
        fb.slotButton('I\'m the label, but I work as a tooltip', iconClass="icnBuilding", action='alert("Hello!")',colspan=2)
        fb.div('This is the standard usage of a slotButton: the label works as a tooltip')
        fb.button('button + icon', iconClass="icnBuilding", action='alert("Hello!")')
        fb.slotButton('slotButton + icon', showLabel=True, iconClass="icnBuilding", action='alert("Hello!")')
        fb.div('Here we have a button and a slotButton set equal (with the "iconClass" attribute)')
        fb.button('button', action='alert("Hello!")')
        fb.slotButton('slotButton', action='alert("Hello!")')
        fb.div('Here we have a button and a slotButton set equal (without the "iconclass" attribute)')