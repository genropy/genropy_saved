.. _menu:

====
menu
====
    
    *Last page update*: |today|
    
    .. note:: To create a menu, you have to use the ``dropdownbutton`` form widget. For more information,
              check the :ref:`dropdownbutton` page.
    
    * :ref:`menu_def`
    * :ref:`menu_attributes`
    * :ref:`menu_examples`:
    
        * :ref:`menu_examples_simple`
        * :ref:`menu_examples_alert`
    
.. _menu_def:
    
definition and description
==========================
    
    .. method:: dropdownbutton.menu([**kwargs])
    
        *In the image, a menu*
        
        .. image:: ../_images/widgets/menu.png
    
    **Menu creation**:
    
    You can create a *menu*:
    
    #. appending it to a :ref:`dropdownbutton`::
    
        ddb = pane.dropdownbutton('NameOfTheMenu')
        menu = ddb.menu()
        
    #. appending it to a div::
    
        menudiv = pane.div(height='50px',width='50px',background='teal')
        menu = menudiv.menu()
        
    **Menu features**:
    
    #. A menu has a hierarchic structure; you can set lines through the **menuline**
       attribute:
       
        .. method:: menu.menuline(label=None[,**kwargs])
        
       * You can set submenus creating a menu inside a menu::
       
            ddb = pane.dropdownbutton('NameOfTheMenu')
            menu = ddb.menu()
            menu.menuline('First Line')
            submenu = menu.menuline('I have submenues').menu() # With this line you create a submenu
            submenu.menuline('First Line')
            
    #. You can use the *action* attribute to create a javascript callback after mouse click
       (check the :ref:`attributes section <menu_attributes>` for more information)
          
    #. To create a dividing line use ``-`` in a ``menuline`` in place of its label::
       
        menuline('-')
        
.. _menu_attributes:

attributes
==========
    
    .. note:: You can use the following attributes both on the menu definition
              or on one of the menulines
              
    **menu attributes**:
    
    * *action*: allow to execute a javascript callback. For more information, check
      the :ref:`action_attr` page and the :ref:`following example <menu_examples_alert>`
    * *checked*: boolean (by default is ``False``). If ``True``, allow to set a "V"
      mark on the left side of a *menuline*
      
        *The third menuline contains the "checked" attribute set to* **True**
        
        .. image:: ../_images/widgets/menu_checked.png
        
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`hidden` page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, you have
      to give it to the dropdownbutton. Check the :ref:`menu_examples_simple`.
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page

.. _menu_examples:

examples
========

.. _menu_examples_simple:

simple example
--------------

    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                ddb = root.dropdownbutton('Menu')
                dmenu = ddb.menu()
                dmenu.menuline('Open...',action="alert('Opening...')")
                dmenu.menuline('Close',action="alert('Closing...')")
                dmenu.menuline('-')
                submenu = dmenu.menuline('I have submenues').menu() # With this line you create a submenu
                submenu.menuline('To do this',action="alert('Doing this...')")
                submenu.menuline('Or to do that',action="alert('Doing that...')")
                dmenu.menuline('-')
                dmenu.menuline('Quit',action="alert('Quitting...')")
                
.. _menu_examples_alert:
            
alert on menu
-------------

    An example of the *action* attribute; it is set both on menu and on its menulines::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                pane = root.contentPane(height='300px',**kwargs)
                menudiv = pane.div(height='50px',width='50px',background='teal')
                menu = menudiv.menu(action='alert($1.foo)',modifiers='*')
                menu.menuline('abc', foo=35, checked=True)
                menu.menuline('xyz', foo=60, disabled=True)
                menu.menuline('alpha',action='alert("I am different")',checked=True)
                menu.menuline('-')
                submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
                submenu.menuline('cat',bar=35)
                submenu.menuline('dog',bar=60)