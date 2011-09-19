.. _framepane:

=========
framePane
=========
    
    *Last page update*: |today|
    
    **Type**: :ref:`layout widget <layout>`
    
    * :ref:`frame_def`: :ref:`frame_sides`
    * :ref:`frame_attributes`
    * :ref:`frame_examples`: :ref:`frame_examples_simple` :ref:`toolbar_example`
    
.. _frame_def:

Definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.framepane
    
.. _frame_sides:
    
sides
-----
    
    Every *side* can be highly customized with regard to the look and with regard to its tools.
    
    For example, in the *top side* you can keep a :ref:`toolbar` with a selector for
    :ref:`table`\'s records (like a :ref:`iv_searchbox`) and in the *bottom side* you can keep
    a place for messages that will inform the user of the correct (or uncorrect) execution of
    its action.
    
    To customize these regions, you have to follow this syntax::
    
        add???
    
.. _frame_attributes:

Attributes
==========
    
    **framePane's attributes**:
    
    * *frameCode*: MANDATORY - autocreate a :ref:`nodeid` for the framePane AND autocreate
      hierarchic nodeIds for every framePane child
      
      Example::
      
        frameCode='frame1'
      
    * *design (Dojo attribute)*: framePane operates in a choice of two layout modes: the design
      attribute may be set to ``headline`` or ``sidebar``. With the ``headline`` layout, the top
      and bottom sections extend the entire width of the box and the remaining regions are placed
      in the middle. With the ``sidebar`` layout, the side panels take priority, extending the full
      height of the box. Default value is ``headline``.
    * *center*: allow to give CSS attributes to your *center* region.
    
      Example::
      
        center_border='5px solid #bbb'
        center_background='#A7A7A7'
    
    **Common attributes**:
    
        For common attributes, check the :ref:`layout_common_attributes` section.
        
.. _frame_examples:

Examples
========

.. _frame_examples_simple:

simple example
--------------

    Here we show you a simple code::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                frame = root.framePane(frameCode='frame1', height='200px', margin='10px',
                                       border='1px solid #bbb', shadow='3px 3px 5px gray',
                                       center_background='gray', rounded=20, design='sidebar')
    
    where:
    
    * the *rounded* attribute is the CSS :ref:`css_border_radius` attribute
    * the *shadow* attribute is the CSS :ref:`css_box_shadow` attribute
    
.. _toolbar_example:

slotToolbar, slotBar example
----------------------------
    
    For some examples with the slotToolbar and the slotBar, please check the
    :ref:`toolbar` documentation page
    