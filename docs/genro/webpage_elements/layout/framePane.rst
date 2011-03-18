.. _genro_framepane:

=========
framePane
=========
    
    .. warning:: to be completed!! add???
    
    * :ref:`frame_def`
    * :ref:`frame_attributes`
    * :ref:`frame_examples`
    
    ::
    
        Clipboard
            
            **Struct method**
                
                from gnr.web.gnrwebstruct import struct_method
                
                ...
                
                top.bar.myslot()
                
                ...
                
                ::
                
                    @struct_method
                    def myslot(self,pane):
                        pane.button(label='Bar',iconClass='icnBaseAdd',lbl='Bar',showLabel=False)
                        
.. _frame_def:

Definition
==========
    
    A framePane is a :ref:`genro_contentpane` with *sides* attribute added:
    *top*, *bottom*, *left* and *right* side [#]_.
    
    In the *sides* we can add buttons, icons, menus and so on and use them to execute 'tasks'.
    In the *top side* we usually keep a :ref:`genro_toolbar` and in the *bottom side* a footer.
    Every *side* can be highly customized with regard to the look and with regard to its tools.
    
    Some tools are *standard*: you may have a button to export excel, one for print and so on.
    
    A toolbar may contain a selector for :ref:`genro_table`\'s records [#]_ or just
    a message that will inform the user of the proper execution of an action and so on.
    
.. _frame_attributes:

Attributes
==========
    
    **framePane's attributes**:
    
    * *frameCode*: MANDATORY - add??? --> create the frameId...
    * *design='sidebar'* add???
    * *center*:
    
        *center_border='5px solid #bbb'*
        *center_background='#A7A7A7'*
    
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
                
**Footnotes**:

.. [#] The internal code defines it as a :ref:`genro_bordercontainer`, but you have to see it as a ``contentPane`` with *sides*.
.. [#] Like a :ref:`iv_searchbox` of the :ref:`genro_includedview` component