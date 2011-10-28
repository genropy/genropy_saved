.. _togglebutton:

============
ToggleButton
============
    
    *Last page update*: |today|
    
    .. note:: ToggleButton features:
              
              * **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`togglebutton_def`
    * :ref:`togglebutton_description`
    * :ref:`togglebutton_attributes`
    * :ref:`togglebutton_examples`
    
.. _togglebutton_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.togglebutton
        

.. _togglebutton_description:

Description
===========

    A toggle button is a button that represents a setting with a ``True`` or ``False`` state.
    
    Togglebuttons look similar to command buttons and display a graphic or text (or both) to identify themselves.

.. _togglebutton_attributes:

Attributes
==========
    
    **togglebutton attributes**:
    
    * ``iconClass``: CSS attribute to insert a button image. Default value is ``None``.
    
      If you want to use the togglebutton as a boolean widget, you can use ``iconClass="dijitRadioIcon"``, like in the following line code [#]_::
    
        fb.togglebutton(value='^.toggle1', iconClass="dijitRadioIcon", label='a togglebutton')
        
.. _togglebutton_examples:

Examples
========

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.div('We show you here a simple togglebuttons set:')
                fb=root.formbuilder(border_spacing='10px',datapath='test1')
                fb.togglebutton(value='^.toggle1',iconClass="dijitRadioIcon",label='label')
                fb.togglebutton(value='^.toggle2',iconClass="dijitRadioIcon",label='another label')

**Footnotes**:

.. [#] This allow the user to check the actual state of the button (``True`` or ``False``).