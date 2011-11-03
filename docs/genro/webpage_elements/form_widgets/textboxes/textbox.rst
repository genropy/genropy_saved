.. _textbox:

=======
TextBox
=======
    
    *Last page update*: |today|
    
    .. note:: TextBox features:
              
              * **Type**: :ref:`Dojo-improved form widget <dojo_improved_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`textbox_def`
    * :ref:`textbox_description`
    * :ref:`textbox_attributes`
    * :ref:`textbox_examples`: :ref:`textbox_examples_simple`

.. _textbox_def:

definition
==========

    .. method:: textbox([**kwargs])
    
.. _textbox_description:

description
===========

    Textbox is used to insert a text
    
.. _textbox_attributes:

attributes
==========
    
    **textbox attributes**:
    
    * *constraints*: TBC add???
    * *invalidMessage*: tooltip text that appears when the content of the textbox is invalid
    * *promptMessage*: tooltip text that appears when the textbox is empty and on focus
    * *required*: define if the field is a required field or not. Default value is ``False``
    * *regExp*: regular expression pattern to be used for validation. If this is used, don't use regExpGen
    * *regExpGen*: TBC. If this is used, do not use regExp ???. Default value is ``None``
    * *tooltipPosition*: define where Tooltip will appear. Default value is ``right``
    
.. _textbox_examples:

Examples
========

.. _textbox_examples_simple:

simple example
--------------

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.div("Some simple textboxes.",font_size='.9em',text_align='justify')
                fb = root.formbuilder(datapath='test1',cols=2)
                fb.textbox(value='^.name',lbl='Name')
                fb.textbox(value='^.surname',lbl='Surname')
                fb.textbox(value='^.address',lbl='Address')
                fb.textbox(value='^.email',lbl='e-mail')
