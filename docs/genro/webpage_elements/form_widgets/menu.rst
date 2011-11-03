.. _menu:

====
menu
====
    
    *Last page update*: |today|
    
    .. note:: menu features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`menu_def`
    * :ref:`menu_examples`:
    
        * :ref:`menu_examples_simple`
        * :ref:`menu_examples_alert`
    
.. _menu_def:
    
definition and description
==========================

    **Menu creation**:
    
    You can create a *menu*:
    
    1. appending it to a :ref:`dropdownbutton`:
    
        .. image:: ../../_images/widgets/menu.png
        
      ::
      
        ddb = pane.dropdownbutton('NameOfTheMenu')
        menu = ddb.menu()
        # other lines...
        
    2. appending it to a div:
    
        .. image:: ../../_images/widgets/menu_div.png
        
      ::
      
        menudiv = pane.div('-MENU-', height='20px', width='50px', background='teal')
        menu = menudiv.menu()
        # other lines...
        
    **Menu features**:
    
    A menu has a hierarchic structure:
    
    #. you can set lines through the **menuline** attribute:
       
        .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.menuline
        
       *In the image: the third menuline contains the "checked"*
       *attribute set to* **True** *(highlighted in yellow)*
       
       *Below the "Load" menuline there's a dividing line*
       
        .. image:: ../../_images/widgets/menu_checked.png
        
    #. You can set submenus creating a menu inside a menu::
       
           ddb = pane.dropdownbutton('NameOfTheMenu')
           menu = ddb.menu()
           menu.menuline('First Line')
           submenu = menu.menuline('I have submenues').menu() # With this line you create a submenu
           submenu.menuline('First Line')
            
    #. You can use the :ref:`action_attr` attribute (both on menu or on menulines) to create a
       javascript callback after mouse click. Check the :ref:`menu_examples_alert`
       
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
            
alert example
-------------

    An example of the :ref:`action_attr` attribute; it is set both on menu and on its menulines::
    
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