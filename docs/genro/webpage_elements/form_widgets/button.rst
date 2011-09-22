.. _button:

======
button
======
    
    *Last page update*: |today|
    
    **Type**: :ref:`Dojo-improved form widget <dojo_improved_form_widgets>`
    
    * :ref:`button_def`
    * :ref:`button_description`
    * :ref:`button_attributes`
    * :ref:`button_icon`
    * :ref:`button_examples`: :ref:`button_example_macro`
    
.. _button_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.button
    
.. _button_description:

description
===========

    The Genro button takes its basic structure from the Dojo button: it is a Dojo widget used as a
    representation of an html button.
    
    **Added Genro feature**: You may define a javascript callback through the *action* attribute.
    
.. _button_attributes:

attributes
==========

    **button attributes**:
    
    * *action*: allow to execute a javascript callback. For more information, check the :ref:`action` section
    * *iconClass*: the button icon. Default value is ``None``. For more information, check the
      :ref:`button_icon` section
    * *showLabel*: (boolean). If ``True``, show the button label. Default value is ``True``
    
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check
      the :ref:`hidden` page
    * *label*: the label of the widget.
    * *value*: specify the path of the widget's value. For more information, check the :ref:`datapath` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page

.. _button_icon:

icons
=====

    There an icon set in the framework; to use them, you need to write the name of the icon
    as a string of the iconClass attribute.
    
    For the complete list of icons, check the gnrbase.css file at the path::
    
        ~/yourRootPathForGenro/genro/gnrjs/gnr_d11/css/gnrbase.css
        
    Where:
    
    * ``yourRootPathForGenro`` is the path where you set the framework
    * ``gnr_dNUMBER`` is the folder with the version you're using for Dojo
      (example: write ``gnr_d11`` to use Dojo 1.1, ``gnr_d16`` to use Dojo 1.6 and so on)
        
        **Example**: let's look to the css of the icon ``building.png`` ::
            
            .icnBuilding{
                background: url(icons/base16/building.png) no-repeat center center;
                width: 16px;
                height: 16px;
            }
            
        To add it, just write in the button ``iconClass='icnBuilding'``::
            
            class GnrCustomWebPage(object):
                def main(self,root,**kwargs):
                    root.button('Click me',action='alert("Hello!")',iconClass='icnBuilding')

.. _button_examples:

examples
========
    
.. _button_example_macro:

Genro macros
------------
    
    With the *action* attribute you can also use one of the Genro macro [#]_; for example
    you can use the :ref:`fire` macro within the "action" attribute: it will launch
    an alert message. The syntax is::
    
        action="FIRE 'javascript command'"
        
    So, you can create an example using a button with the ``FIRE`` command combined with a
    dataController, using the following syntax::
    
        pane.dataController('write-JS-Here!',_fired="^startJS")     # in place of "write-JS-here" you have
                                                                    #     to write some javascript code
        pane.button('Unleash the dataController!',fire='^startJS')  # when this button is clicked, the JS wrote in the
                                                                    #     dataController will be executed
                                                                    
    We now show you two different syntaxes to do the same thing:
    
    **syntax 1**::
    
        pane.dataController('''alert(msg);''', msg='^msg')
        pane.button('Click me!',action="FIRE msg='Click!';")
        
    **syntax 2**::
    
        pane.dataController('''alert(msg);''', msg='^msg')
        pane.button('Click me!', fire_Click = 'msg')
        
    It is important for you to know that the ``FIRE`` command in the button is a shortcut for a
    script that puts ``True`` in the destination path (allowing to the action of the button to be
    executed) and then put again ``False`` (allowing to the button to be reusable!).

**Footnotes:**

.. [#] In Genro there are different macros used as a shortcut that you can use in place of some javascript command. For a complete list and relative explanation, check the :ref:`macro` page.