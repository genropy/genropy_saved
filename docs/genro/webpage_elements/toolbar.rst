.. _genro_toolbar:

=======
toolbar
=======
    
    .. warning:: to be completed!! add???
    
    * :ref:`toolbar_def`
    * :ref:`toolbar_attributes`
    * :ref:`toolbar_examples`: :ref:`toolbar_examples_simple`

Clipboard
=========

    **slotToolbar e slotBar**
    
    toolBar e slottoolbar NON sono form widget, sono tipo menu
    toolBar e slotToolbar sono appendibili ad ogni cosa, non solo al framePane
    
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
            * "searchOn" --> ??? si può non definire un "nodeId" SE è definito un frameCode
                                 in un framePane di cui il searchOn è figlio!
            
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

.. _toolbar_def:

Definition
==========

    add???

.. _toolbar_attributes:

Attributes
==========

    add???

.. _toolbar_examples:

Examples
========

    add???

.. _toolbar_examples_simple:

simple example
--------------

    **Example**::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                add???
