.. _genro_framepane:

=========
framePane
=========
    
    .. warning:: to be completed!!
    
    * :ref:`frame_def`
    * :ref:`frame_attributes`
    * :ref:`frame_examples`
    * :ref:`frame_attr_exp`

Clipboard
=========
    
    **framePane**
    
        * *frameCode*: add???
        * *rounded* (add in CSS!)
        * *design='sidebar'* add???
        * *center*:
        
            *center_border='5px solid #bbb'*
            *center_background='#A7A7A7'*
        * **:
    
    **New Syntax**
    
        ``frame.top.slotBar``
    
    **slotToolbar e slotBar**
    
        - la slotToolbar ha già i gradienti di colore di default.
        
        Example::
            
            frame = pane.framePane(frameCode='frame3',height='200px',width='300px',shadow='3px 3px 5px gray',
                                   border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                   center_background='gray',rounded=10,rounded_bottom=0)
            top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
            left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')  
            bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
            right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
            
        - la slotBar non ha i gradienti di colore di default
        
        * *slots* (height obbligatorio?):
        
            * "|" --> splitter bar
            * "*" --> white space
            
        * *slotbarCode='myslotbar'* (or slottoolbarCode???)
        
        * *orientation* --> V (vertical)
                        --> H (horizontal) default: orientation='H'
        
        * *gradient_deg* 0 --> x axis, positive numbers
                        90 --> y axis, positive numbers
                       180 --> x axis, negative numbers
                       270 --> y axis, negative numbers
                       
        * *gradient_from* --> a color
        * *gradient_to* --> another color
        * *lbl_position='T'* *lbl_color='red'* *lbl_font_size='7px'* (slotBar attributes, or CSS attributes
                                                                      for every object?)
          LBL! not label (infact the slotBar is built on formbuilder... right???)
        * *border_bottom='1px solid #bbb'*
        * *showLabel=False* --> bottom.foo.button('!!Save',iconClass="icnBaseOk",showLabel=False) (default --> True)
        
    **Struct method**
        
        from gnr.web.gnrwebstruct import struct_method
        
        ...
        
        top.bar.myslot()
        
        ...
        
        @struct_method
        def myslot(self,pane):
            pane.button(label='Bar',iconClass='icnBaseAdd',lbl='Bar',showLabel=False)
            
.. _frame_def:

Definition
==========
    
    A :ref:`genro_contentpane` with some added features.
    
.. _frame_attributes:

Attributes
==========
    
    **framePane's attributes**:
    
    * *add???*:
    
    **attributes of the framePane's children (paneContainers)**:
    
    * *add???*:
    
    .. _border-common-attributes:
    
    **Common attributes**:
    
        For commons attributes, see add??? --> :ref:`genro_layout_common_attributes`
        
.. _frame_examples:

Examples
========

.. _frame_examples_simple:

simple example
--------------

    Here we show you a simple code::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = root.borderContainer(height='400px')
                add???
                
.. _frame_attr_exp:

Attributes explanation
======================

.. _frame_???:

??? attribute
=============

    add???