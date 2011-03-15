.. _genro_button:

======
button
======

    * :ref:`button_def`
    * :ref:`button_description`
    * :ref:`button_attributes`
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
    
    **Added Genro feature**: You may define its purpose through the *action* attribute (explained below),
    a javascript command executed by clicking on the button itself.

.. _button_attributes:

Attributes
==========

    **button attributes**:
    
    * *action*: allow to execute a javascript callback. For more information, check the :ref:`button_action` section below
    
    **common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *label*: the label of the widget.
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page

.. _button_examples:

Examples
========

.. _button_action:

action
======

    The *action* attribute is a javascript onclick callback that receives all the ``**kwargs`` parameters.
    
    For example, to create an alert message you have to write this line::
    
        pane.button('I\'m a button',action="alert('Hello!')")
        
    where ``'I\'m a button'`` is the label of the button.
    
.. _button_example_macro:

Usage of some Genro macro
=========================
    
    With the *action* attribute you can also use one of the four Genro macro [#]_; for example you can use the :ref:`genro_fire` macro within the "action" attribute: it will launch an alert message. The syntax is::
    
        action="FIRE 'javascript command'"
        
    So, you can create an example using a button with the ``FIRE`` command combined with a dataController, using the following syntax::
    
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
        
    It is important for you to know that the ``FIRE`` command in the button is a shortcut for a script that puts ``True`` in the destination path (allowing to the action of the button to be executed) and then put again ``False`` (allowing to the button to be reusable!).

**Footnotes:**

.. [#] In Genro there are four macros used as a shortcut that you can use in place of some Javascript command. They are ``FIRE``, ``GET``, ``SET``, ``PUT``. For more details, check the :ref:`genro_macro` page.