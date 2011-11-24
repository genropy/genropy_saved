.. _stackcontainer:

==============
StackContainer
==============
    
    *Last page update*: |today|
    
    .. note:: StackContainer features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`stack_def`
    * :ref:`stack_attributes`
    * :ref:`stack_examples`:
    
        * :ref:`stack_examples_simple`

.. _stack_def:

definition
==========
    
    .. method:: pane.stackContainer([**kwargs])
    
    A container that has multiple children, but shows only one child at a time
    (like looking at the pages in a book one by one)
    
.. _stack_attributes:

attributes
==========
    
    **stackContainer's attributes**:
    
    * *selectedPage*: allow to select a determined page. You have to define the *pageName*
      attribute in stackContainer's children
      
    **attributes of the stackContainer's children**:
    
    * *pageName*: allow to identify the selected page
    
.. _stack_examples:

examples
========

.. _stack_examples_simple:

simple example
--------------

    * `stackContainer [basic] <http://localhost:8080/webpage_elements/widgets/layout/stackcontainer/1>`_
    * **Description**: the *selectedPage* is linked to the stackContainer with a :ref:`filteringselect` set on
      a :ref:`slotToolbar <slotbar>`
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`contentpane`,
                  :ref:`filteringselect`, :ref:`stackcontainer`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Stack container"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_1_basic(self, pane):
                """Stack page"""
                bc = pane.borderContainer(height='300px')
                top = bc.contentPane(region='top') # height is given automatically through the slotToolbar
                sb = top.slotToolbar(slots='10,my_slot,*')
                sb.my_slot.filteringSelect(value='^.selectedPage',values='one:page one,two:page two,three:page three')
                center = bc.contentPane(region='center')
                sc = center.stackContainer(region='center', selectedPage='^.selectedPage')
                stack_one = sc.contentPane(background='#F0F1A5', pageName='one')
                stack_one.div('A div included in the first stack page',
                               margin='1em', display='inline-block',
                               border='3px solid gray', width='400px', height='100px',
                               rounded=5, font_size='1.3em', text_align='justify')
                stack_two = sc.contentPane(background='#ABDCEA', pageName='two')
                stack_two.div('A div included in the second stack page',
                               margin='2em', display='inline-block',
                               border='3px solid gray', width='400px', height='100px',
                               rounded=5, font_size='1.3em', text_align='justify')
                stack_three = sc.contentPane(background='#77C67C', pageName='three')
                stack_three.div('A div included in the third stack page',
                                 margin='3em', display='inline-block',
                                 border='3px solid gray', width='400px', height='100px',
                                 rounded=5, font_size='1.3em', text_align='justify')