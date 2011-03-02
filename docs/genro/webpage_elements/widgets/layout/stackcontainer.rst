.. _genro_stackcontainer:

==============
stackContainer
==============

    .. warning:: This page has to be completed!!
    
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
    
    add???
    
    **attributes of the stackContainer's children (???)**:
    
    **common attributes**:
    
        For common attributes, see :ref:`genro_layout_common_attributes`

.. _stack_examples:

Examples
========

**Simple example:** Here we show you a simple code containing a ``stackContainer``::

    class GnrCustomWebPage(object):
        def main(self,root,**kwargs):
            ???
            