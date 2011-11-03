.. _dropdownbutton:

==============
DropDownButton
==============
    
    *Last page update*: |today|
    
    .. note:: DropDownButton features:
    
              * **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`ddb_def`
    * :ref:`ddb_examples`
    
.. _ddb_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.dropdownbutton
    
.. _ddb_examples:

examples
========

    ::
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                fb = root.formbuilder(cols=2)
                ddb = fb.dropdownbutton(iconClass='iconbox menubox print', showLabel=False)
                dmenu = ddb.menu()
                dmenu.menuline('Print...',action="alert('Opening...')")
                dmenu.menuline('Preset',action="alert('Closing...')")
                dmenu.menuline('-')
                submenu = dmenu.menuline('Advanced options').menu()
                submenu.menuline('Pages per sheet',action="alert('...')")
                submenu.menuline('PDF',action="alert('Making PDF...')")
                dmenu.menuline('-')
                dmenu.menuline('Quit',action="alert('Quitting...')")