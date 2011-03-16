.. _genro_css:

============
CSS elements
============

    * :ref:`css_introduction`
    * :ref:`css_dojo_themes`
    * :ref:`css_genro_themes`
    * :ref:`css_genro_names`

.. _css_introduction:

Introduction
============

    CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.
    
    * When you use CSS on a Genro :ref:`webpages_webpages` keep in mind that the main difference
      with standard CSS lies in this rule:
      
      **you have to use the "_" symbol in place of the "-" symbol**::
    
        <!-- normal CSS style -->
        font-size='40pt'
        margin-top='40px'
        
        <!-- Genro webpage CSS style  -->
        font_size='40pt'
        margin_top='40px'
        
    You should also know that:
        
    * You can import css files in your :ref:`genro_structure_mainproject` through the *css_requires*
      variable: check the :ref:`webpages_css_requires` section for further details.
    
    * Genro allows to use :ref:`css_dojo_themes` and :ref:`css_genro_themes`.
    
    * There are some CSS attributes that have a different name respect to their standard CSS name:
      check the :ref:`css_genro_names` section for the complete list
    
.. _css_dojo_themes:

Dojo themes
===========

    The default Dojo theme for all the :ref:`webpages_webpages`\s is 'tundra'.
    
    You can change a Dojo theme directly in your webpage: check the :ref:`webpages_dojo_theme` section for
    the correct syntax, the complete reference list of compatible Dojo themes and more.
    
.. _css_genro_themes:

CSS themes
==========

    CSS themes are Genro themes that modify the current Dojo theme of your webpage, adding or deleting some of their features.
    
    You can define your default CSS theme in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig` or in a single
    :ref:`webpages_webpages` through the :ref:`webpages_css_theme` webpage variable.
    
    We list here the main Genro themes currently available:
    
    * *aqua*
    * *blue*
    * *elephant*
    * *pro*

.. _css_genro_names:

Genro CSS names
===============

    We list here all the CSS attributes that have a different name respect to the standard CSS name.
    
    Click on the standard CSS name to go to the documentation line on the corresponding Genro CSS attribute:
    
    **Standard CSS name**:
    
    * :ref:`border-radius <css_border_radius>`
    * :ref:`box-shadow <css_box_shadow>`
    * other attributes: add???
    
    .. _css_border_radius:
    
    **border-radius**:
    
    * Genro CSS name: rounded
    * Example::
    
        rounded=10
        
    * Features: the *rounded* attribute support the top/bottom/left/right extensions::
    
        rounded=10,rounded_bottom=0
    
    .. _css_box_shadow:
    
    **box-shadow**:
    
    * Genro CSS name: shadow
    * Example::
    
        shadow='5px 5px 5px gray' 
    
