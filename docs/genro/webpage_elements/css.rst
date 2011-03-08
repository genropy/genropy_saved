.. _genro_css:

============
CSS elements
============

    * :ref:`css_introduction`
    * :ref:`css_dojo_themes`
    * :ref:`css_genro_themes`

.. _css_introduction:

Introduction
============

    CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.
    
    * When you use CSS on a Genro :ref:`webpages_webpages` keep in mind that the only difference
      with standard CSS lies in this rule:
      
      **you have to use the "_" symbol in place of the "-" symbol**::
    
        <!-- normal CSS style -->
        font-size='40pt'
        margin-top='40px'
        
        <!-- Genro webpage CSS style  -->
        font_size='40pt'
        margin_top='40px'
        
    You should also know that:
        
    * You can import css files in your :ref:`genro_structure_mainproject` through the *css_requires* variable: check the :ref:`webpages_css_requires` section for further details.
    
    * Genro allows to use :ref:`css_dojo_themes` and :ref:`css_genro_themes`.
    
.. _css_dojo_themes:

Dojo themes
===========

    The default Dojo theme for all the :ref:`webpages_webpages`\s is 'tundra'.
    
    You can change a Dojo theme directly in your webpage: check the :ref:`webpages_dojo_theme` section for
    the correct syntax, the complete reference list of compatible Dojo themes and more.
    
.. _css_genro_themes:

Genro themes
============

    Genro themes are css themes that modify the current Dojo theme of your webpage, adding or deleting some of their features.
    
    You can define your default Genro theme in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`.
    
    We list here the main Genro themes currently available:
    
    * *aqua*
    * *blue*
    * *elephant*
    * *pro*
