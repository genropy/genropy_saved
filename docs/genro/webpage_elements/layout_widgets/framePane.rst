.. _framepane:

=========
framePane
=========
    
    *Last page update*: |today|
    
    .. note:: **Type**: :ref:`Genro layout widget <genro_layout>`
    
    * :ref:`frame_def`
    * :ref:`frame_attributes`:
    
        * :ref:`frame_design`
        * :ref:`frame_framecode`
        * :ref:`frame_sides`
        * :ref:`frame_common_attrs`
        
    * :ref:`frame_examples`: :ref:`frame_examples_simple` :ref:`toolbar_example`
    
.. _frame_def:

definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.framepane
    
.. _frame_attributes:

attributes
==========

    We list here all the attributes of the framePane:
    
    * :ref:`frame_design`
    * :ref:`frame_framecode`
    * :ref:`frame_sides`
    * :ref:`frame_common_attrs`
    
.. _frame_design:

design
------
    
    (Dojo attribute): define the layout of the element. For more information, check the
    :ref:`design` page. Default value is ``headline``
    
.. _frame_framecode:

frameCode
---------
        
    MANDATORY. Create a :ref:`nodeid` for the framePane AND create hierarchic :ref:`nodeIds
    <nodeid>` for every framePane child
      
    **Example**::
      
        frameCode='frame1'
        
.. _frame_sides:
    
sides
-----
    
    Every *side* can be highly customized with regard to the look and with regard to its tools.
    
    To customize these regions, you have to follow this procedure:
    
    * create your framePane, assigning a name, like::
    
        frame = pane.framePane(...)
        
      (where ``pane`` is a :ref:`layout element <layout>` to which you attached the framePane)
      
    * attach to the framePane name the region to which you want to work on:
    
        * use ``top`` for the top region
        * use ``bottom`` for the top region
        * use ``left`` for the top region
        * use ``right`` for the top region
        
        Example::
        
            frame.bottom.div('This is my bottom')
            
    * To attach something to the ``center`` region, you have to attach it to the name of your
      framePane, like in the following lines::
      
        frame = pane.framePane(...)
        frame.div('Hello!')
        
    **Example**:
    
        In the *top side* you can keep a :ref:`slotToolbar <toolbar>` with a title and a button
        that executes an action::
        
            class GnrCustomWebPage(object):
                def main(self, root, **kwargs):
                    frame = root.framePane(frameCode='frame1',height='200px',margin='10px',
                                           shadow='3px 3px 5px gray',border='1px solid #bbb',
                                           rounded=20,design='sidebar')
                    top = frame.top.slotToolbar(slots='*,test_xx,*,my_button,50',background='blue')
                    top.test_xx.div('This is a title',width='100px',background='red')
                    top.my_button.button('I am a button', action="alert('hi')")
                    frame.div('Here goes the \"center\" content.',margin='20px')
                    
        As you can see in the example, you can attach an object (like a slotToolbar) to the
        top region of your framePane through: ``frame.top.slotToolbar()``
        
.. _frame_common_attrs:

common attributes
-----------------

    For common attributes, check the :ref:`layout_common_attributes` section.
    
.. _frame_examples:

examples
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
    
    (where *rounded* is the CSS :ref:`css_border_radius` attribute, *shadow* is the CSS
    :ref:`css_box_shadow` attribute)
    
.. _toolbar_example:

slotToolbar, slotBar example
----------------------------
    
    For some examples with the slotToolbar and the slotBar, please check the
    :ref:`relative <toolbar>` documentation page
    