.. _togglebutton:

============
ToggleButton
============
    
    *Last page update*: |today|
    
    .. note:: ToggleButton features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`togglebutton_def`
    * :ref:`togglebutton_examples`
    
.. _togglebutton_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.togglebutton
    
.. _togglebutton_examples:

examples
========

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=root.togglebutton(value='^.toggle1',iconClass="dijitRadioIcon",label='Button')