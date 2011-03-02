.. _genro_simplearea:

==============
simpleTextarea
==============

    .. note:: The Genro simpleTextarea has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's simpleTextarea_ documentation.

    .. _simpleTextarea: http://docs.dojocampus.org/dijit/form/SimpleTextarea
    
    * :ref:`simplearea_def`
    * :ref:`simplearea_description`
    * :ref:`simpletextarea_attributes`
    * :ref:`simpletextarea_examples`

.. _simplearea_def:

Definition
==========

    .. method:: pane.simpleTextarea([**kwargs])

.. _simplearea_description:

Description
===========

    With simpletextarea you can add an area for user writing.

.. _simpletextarea_attributes:

Attributes
==========

    **simpleTextarea attributes**:
    
    * *default*: Add a text to the area. Default value is ``None``
    
    **common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page
    
.. _simpletextarea_examples:

Examples
========

    Let's see a code example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.simpleTextarea(value='^.area',height='80px',width='30em',
                                    colspan=2,color='blue',font_size='1.2em',
                                    default='A simple area to contain text.', lbl='text area')