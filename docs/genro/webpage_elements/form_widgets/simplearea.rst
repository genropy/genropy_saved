.. _simplearea:

==============
SimpleTextarea
==============
    
    *Last page update*: |today|
    
    .. note:: SimpleTextArea features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`simplearea_def`
    * :ref:`simplearea_description`
    * :ref:`simplearea_attributes`
    * :ref:`simplearea_examples`: :ref:`simplearea_examples_simple`

.. _simplearea_def:

Definition
==========

    .. method:: pane.simpleTextarea([**kwargs])

.. _simplearea_description:

Description
===========

    With simpletextarea you can add an area for user writing.

.. _simplearea_attributes:

Attributes
==========

    **simpleTextarea attributes**:
    
    * *default*: Add a text to the area. Default value is ``None``
    
.. _simplearea_examples:

Examples
========

.. _simplearea_examples_simple:

simple example
--------------

    Let's see a simple example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.simpleTextarea(value='^.area',height='80px',width='30em',
                                    colspan=2,color='blue',font_size='1.2em',lbl='text area')