.. _iconclass:

=========
iconClass
=========

    *Last page update*: |today|
    
    .. note:: **validity** - the *iconClass* attribute is supported by:
              
              * :ref:`button`
              * :ref:`dropdownbutton`
              * :ref:`togglebutton`
              * :ref:`slotbutton`
              
    There is an icon set in the framework; to use them, you need to write the name of the icon
    as a string of the iconClass attribute.
    
    For the complete list of icons, check the gnrbase.css file at the path::
    
        ~/yourRootPathForGenro/genro/gnrjs/gnr_dNUMBER/css/gnrbase.css
        
    Where:
    
    * ``yourRootPathForGenro`` is the path where you set the framework
    * ``gnr_dNUMBER`` is the folder with the version you're using for Dojo
      (example: write ``gnr_d11`` to use Dojo 1.1, ``gnr_d16`` to use Dojo 1.6 and so on)
      
    .. note:: you can find the Genro compatible versions of Dojo :ref:`here <version_dojo>`
        
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