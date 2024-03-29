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
        * :ref:`menu_examples_action`
        
.. _menu_def:

definition and description
==========================

    **Menu creation**:
    
    You can create a *menu*:
    
    1. appending it to a :ref:`dropdownbutton`:
    
        .. image:: ../../../_images/widgets/menu/menu.png
        
      ::
      
        ddb = pane.dropdownbutton('NameOfTheMenu')
        menu = ddb.menu()
        # other lines...
        
    2. appending it to a div:
    
        .. image:: ../../../_images/widgets/menu/menu_div.png
        
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
       
        .. image:: ../../../_images/widgets/menu/menu_checked.png
        
    #. You can set submenus creating a menu inside a menu::
       
           ddb = pane.dropdownbutton('NameOfTheMenu')
           menu = ddb.menu()
           menu.menuline('First Line')
           submenu = menu.menuline('I have submenues').menu() # With this line you create a submenu
           submenu.menuline('First Line')
            
    #. You can use the :ref:`action_attr` attribute (both on menu or on menulines) to create a
       javascript callback after mouse click. Check the :ref:`menu_examples_action`
       
.. _menu_examples:

examples
========

.. _menu_examples_simple:

simple example
--------------

    * `Menu [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/menu/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`dropdownbutton`, :ref:`formbuilder`
                
    * **Code**::
    
          # -*- coding: UTF-8 -*-
          """menu_simple"""

          class GnrCustomWebPage(object):
              py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
              
              def test_1_basic(self,pane):
                  """simple menu"""
                  fb = pane.formbuilder(cols=3)
                  ddb = fb.dropdownbutton(iconClass='iconbox print', showLabel=False)
                  dmenu = ddb.menu()
                  dmenu.menuline('Print...', action="alert('Printing...')")
                  dmenu.menuline('-')
                  submenu = dmenu.menuline('Advanced options').menu() # With this line you create a submenu
                  submenu.menuline('Preview', action="alert('Creating preview...')")
                  submenu.menuline('PDF', action="alert('Making PDF...')")
                  dmenu.menuline('-')
                  dmenu.menuline('Cancel', action="alert('Abort print...')")

                  ddb = fb.dropdownbutton('Save', iconClass='iconbox save')
                  dmenu = ddb.menu()
                  dmenu.menuline('Save', action="alert('Saved')")
                  dmenu.menuline('Save as...', action="alert('Saved as...')")

                  ddb = fb.dropdownbutton('Load', height='22px')
                  dmenu = ddb.menu()
                  dmenu.menuline('Load template', action="alert('Loaded')")
                  dmenu.menuline('Load from file', action="alert('Loaded')")
                  
    .. _menu_examples_action:

action example
--------------

    * `Menu [action] <http://localhost:8080/webpage_elements/widgets/form_widgets/menu/2>`_
    * **Description**: an example of the :ref:`action_attr` attribute; it is set both on menu
      and on its menulines; the third menuline (labelled "menuline n.3") contains an action,
      so this action prevails on the menu action (``action='alert($1.foo)'``)
      
      .. note:: example elements' list:

                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`dropdownbutton`
                
    * **Code**::
      
          # -*- coding: UTF-8 -*-
          """menu_action"""
          
          class GnrCustomWebPage(object):
              py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
              
              def test_2_alert(self, pane):
                  """menu with alert attribute"""
                  menudiv = pane.dropdownbutton('Menu')
                  menu = menudiv.menu(action='alert($1.foo)')
                  menu.menuline('menuline n.1', foo=36)
                  menu.menuline('I\'m disabled', foo=60, disabled=True)
                  menu.menuline('menuline n.3', action='alert("I\'m different")',checked=True)
                  menu.menuline('-')
                  submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
                  submenu.menuline('submenuline n.1', bar=36)
                  submenu.menuline('submenuline n.2', bar=60)
                  