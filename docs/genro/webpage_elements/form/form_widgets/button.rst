.. _genro_button:

======
button
======

    * :ref:`button_def`
    * :ref:`button_description`
    * :ref:`button_attributes`
    * :ref:`button_icon`
    * :ref:`button_examples`: :ref:`button_action`, :ref:`button_example_macro`
    
.. _button_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.button
    
.. _button_description:

Description
===========

    The Genro button takes its basic structure from the Dojo button: it is a Dojo widget used as a
    representation of an html button.
    
    **Added Genro feature**: You may define a javascript callback through the *action* attribute (explained below).

.. _button_attributes:

Attributes
==========

    **button attributes**:
    
    * *action*: allow to execute a javascript callback. For more information, check the :ref:`button_action` section below
    * *iconClass*: the button icon. Default value is ``None`` Check the :ref:`button_icon` section for the complete list.
    * *showLabel*: (boolean). If ``True``, show the button label. Default value is ``True``
    
    **commons attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information,
      check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check
      the :ref:`genro_hidden` documentation page
    * *label*: the label of the widget.
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath`
      documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page

.. _button_icon:

Icons
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

Examples
========

.. _button_action:

action
------

    The *action* attribute is a javascript onclick callback that receives all the ``**kwargs`` parameters.
    
    For example, to create an alert message you have to write this line::
    
        pane.button('I\'m a button',action="alert('Hello!')")
        
    where ``'I\'m a button'`` is the label of the button.
    
    Other *action* examples::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2)
                fb.div('The action attribute allow to write javascript code.',
                        font_size='.9em',text_align='justify',colspan=2)
                fb.button('Button',action="alert('Hello!')",tooltip='click me!')
                fb.div("""Create an alert message through "action" attribute.
                          There is a tooltip, too.""",
                        font_size='.9em',text_align='justify')
                fb.button('Format your system', action='confirm("Sure?")')
                fb.div('Create a confirm message through "action" attribute.',
                        font_size='.9em',text_align='justify')
                fb.button('Calculate Res', action="SET .res = screen.width+' x '+screen.height;")
                fb.textbox(lbl='res',value='^.res',width='6em')
    
.. _button_example_macro:

Genro macros
------------
    
    With the *action* attribute you can also use one of the Genro macro [#]_; for example
    you can use the :ref:`genro_fire` macro within the "action" attribute: it will launch
    an alert message. The syntax is::
    
        action="FIRE 'javascript command'"
        
    So, you can create an example using a button with the ``FIRE`` command combined with a
    dataController, using the following syntax::
    
        pane.dataController('write-JS-Here!',_fired="^startJS")     # in place of "write-JS-here" you have
                                                                    #     to write some Javascript code
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

.. [#] In Genro there are different macros used as a shortcut that you can use in place of some Javascript command. For a complete list and relative explanation, check the :ref:`genro_macro` documentation page.