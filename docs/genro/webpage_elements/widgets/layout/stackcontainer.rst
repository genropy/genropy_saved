.. _genro_stackcontainer:

==============
stackContainer
==============
    
    .. note:: The Genro stackContainer has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's stackContainer_ documentation.

    .. _stackContainer: http://docs.dojocampus.org/dijit/layout/StackContainer

    * :ref:`stack_def`
    * :ref:`stack_attributes`
    * :ref:`stack_examples`

.. _stack_def:

Definition
==========
    
    .. method:: pane.stackContainer([**kwargs])
    
    A container that has multiple children, but shows only one child at a time (like looking at the pages in a book one by one).
    
    This container is good for wizards, slide shows, and long lists or text blocks.
    
.. _stack_attributes:

Attributes
==========
    
    **stackContainer's attributes**:
    
    * *selectedPage*: allow to select a determined page. You have to define the *pageName* attribute
      in stackContainer's children.
    
    **attributes of the stackContainer's children**:
    
    * *pageName*: allow to identify the selected page.
    
    **common attributes**:
    
        For common attributes, see :ref:`genro_layout_common_attributes`

.. _stack_examples:

Examples
========

    **Simple example:** Here we show you a simple code containing a ``stackContainer``, in which the *selectedPage*
    is linked with the filteringSelect keys::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = pane.borderContainer(height='100px')
                top = bc.contentPane(region='top', height='18px', background='#2B65AC').filteringSelect(value='^.selectedPage',
                                                                                                        values='lb:light blue,le:light yellow,blue:blue')
                sc = bc.stackContainer(region='center', selectedPage='^.selectedPage')
                sc1 = sc.contentPane(background='#7CBEF8', pageName='lb')
                sc1.div('Hello!', color='white')
                sc2 = sc.contentPane(background='#EFE237', pageName='le')
                sc3 = sc.contentPane(background='blue', pageName='blue')
            