.. _genro_menu:

====
menu
====
    
    *Last page update*: |today|
    
    .. note:: To create a menu, you have to use the ``dropdownbutton`` form widget. For more information,
              check the :ref:`genro_dropdownbutton` documentation page.
    
    * :ref:`menu_def`
    * :ref:`menu_attributes`
    * :ref:`menu_examples`: :ref:`menu_examples_simple`
    
.. _menu_def:
    
definition and description
==========================
    
    .. method:: dropdownbutton.menu([**kwargs])
    
    Constructs a button that opens a :ref:`genro_menu` or a ``tooltipdialog``.
    
    * You can create a *menu* appending it to a dropdownbutton::
    
        ddb = pane.dropdownbutton('NameOfTheMenu')
        menu = ddb.menu()
        
    * Every *menuline* is created through the ``menuline`` attribute:
    
        .. method:: menu.menuline(label=None[,**kwargs])
        
    in the ``**kwargs`` lies the :ref:`genro_action` attribute::
    
        menuline('Open...',action="alert('Opening...')")
        
    * To create a dividing line use ``-`` in a ``menuline`` in place of its label::
    
        menuline('-')

.. _menu_attributes:

attributes
==========
    
    **menu attributes**:
    
    * *action*: allow to execute a javascript callback. For more information, check the :ref:`genro_action`
      documentation page
          
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, you have
      to give it to the dropdownbutton. Check the :ref:`menu_examples_simple`.
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page

.. _menu_examples:

examples
========

.. _menu_examples_simple:

simple example
--------------

    **Example**::
        
        def main(self,root,**kwargs):
            ddb = root.dropdownbutton('Menu')    # Same meaning: ddb=pane.dropdownbutton(label='Menu')
            dmenu = ddb.menu()
            dmenu.menuline('Open...',action="alert('Opening...')")
            dmenu.menuline('Close',action="alert('Closing...')")
            dmenu.menuline('-')
            submenu = dmenu.menuline('I have submenues').menu() # With this line you create a submenu
            submenu.menuline('To do this',action="alert('Doing this...')")
            submenu.menuline('Or to do that',action="alert('Doing that...')")
            dmenu.menuline('-')
            dmenu.menuline('Quit',action="alert('Quitting...')")