.. _simpletextarea:

==============
SimpleTextarea
==============
    
    *Last page update*: |today|
    
    .. note:: SimpleTextArea features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`simpletextarea_def`
    * :ref:`simpletextarea_description`
    * :ref:`simpletextarea_attributes`
    * :ref:`simpletextarea_examples`: :ref:`simpletextarea_examples_simple`

.. _simpletextarea_def:

Definition
==========

    .. method:: pane.simpleTextarea([**kwargs])

.. _simpletextarea_description:

Description
===========

    With simpletextarea you can add an area for user writing.

.. _simpletextarea_attributes:

Attributes
==========

    **simpleTextarea attributes**:
    
    * *default*: Add a text to the area. Default value is ``None``
    
.. _simpletextarea_examples:

Examples
========

.. _simpletextarea_examples_simple:

simple example
--------------

    Let's see a simple example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.simpleTextarea(value='^.area',height='80px',width='30em',
                                    colspan=2,color='blue',font_size='1.2em',lbl='text area')