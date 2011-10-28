.. _button:

======
button
======
    
    *Last page update*: |today|
    
    .. note:: Button features:
    
              * **Type**: :ref:`Dojo-improved form widget <dojo_improved_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`button_def`
    * :ref:`button_examples`: :ref:`button_example_macro`
    
.. _button_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.button
    
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