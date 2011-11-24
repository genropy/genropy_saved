.. _css:

===
CSS
===
    
    *Last page update*: |today|
    
    * :ref:`css_intro`
    * :ref:`css_dojo_themes`
    * :ref:`css_themes`
    * :ref:`css_icons`
    
.. _css_intro:

introduction
============

    CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.
    
    There are two ways of adding CSS style in Genro:
    
    #. The first way is the nearest to the standard way to use CSS. You have to create a CSS
       file with the *standard CSS syntax*, put it into your :ref:`intro_resources` folder of
       your :ref:`project` and call it into your page.
       
       To call the CSS file in your python webpage, you obviously can't use the standard HTML
       syntax (``<link href="stile/name_of_CSS_file.css" rel="stylesheet" type="text/css" />``)
       but you have to add the following :ref:`webpage variable <webpages_variables>`::
       
           css_requires = 'name_of_CSS_file' # write the CSS filename without its ``.css`` extension!
           
       For more information on ``css_requires`` please check the :ref:`css_requires section
       <css_requires>`
       
    #. The second way is to use CSS style directly in your Genro :ref:`webpage`.
       When you do this, please pay attention that the CSS syntax is a little different
       from the standard CSS syntax; infact, you have to:
       
       #. use the underscore (``_``) character in place of the dash (``-``) character
       #. use the equal (``=``) character in place of the colon (``:``) character
       #. use the comma (``,``) character in place of the semi colon (``;``) character
       
       Let's see an example:
       
       The normal CSS style looks like this::
        
        font-size:'20pt';
        background-color:'teal';
        
       While the same CSS style in a Genro webpage has to be written in this way::
       
        font_size='20pt',
        background_color='teal',
        
       When you write CSS on a single element the effect will be::
       
        root.textbox(font_size='20pt',background_color='teal',value='^hello')
        
    .. note:: you can use both the ways we just explained to you in a single file: you can
              import a CSS file with the :ref:`css_requires` and at the same time
              you can write additional style on some webpage elements.
       
    You should also know that:
    
    * Genro allows to use some CSS preset style:
    
        * :ref:`css_dojo_themes`
        * Genro :ref:`css_themes`
        * :ref:`css_icons`
        
    * If you need to use CSS3 attributes in a Genro :ref:`webpage` you have to check the
      :ref:`css3_names` section for the complete list with the Genro names
      
.. _css_dojo_themes:

Dojo themes
===========

    The default Dojo theme for all the :ref:`webpages <webpage>` is 'tundra'.
    
    You can change a Dojo theme in your webpage: check the :ref:`webpages_dojo_theme` section
    for the correct syntax, the complete reference list of compatible Dojo themes and more.
    
.. _css_themes:

CSS themes
==========

    CSS themes are Genro themes that modify the current Dojo theme of your webpage, adding or
    deleting some of their features.
    
    You can define your default CSS theme for all your pages in the :ref:`siteconfig_gui` tag
    of your :ref:`sites_siteconfig` or in a single :ref:`webpage` through the
    :ref:`webpages_css_theme` webpage variable.
    
    We list here the main Genro themes currently available:
    
    * *aqua*
    * *blue*
    * *elephant*
    * *pro*
    
.. _css_icons:

CSS icons
=========

    To use a set of CSS icons you need to type one of the following :ref:`css_icons webpage
    variable <webpages_css_icons>` in your webpage:
    
    * retina/blue
    * retina/gray
    * retina/lime
    * retina/red
    * retina/violet
    
    The default value is the value you specify in the :ref:`siteconfig_css_icons` tag of your
    :ref:`sites_siteconfig`. Otherwise, the default value is ``retina/gray``
    
    **Example**::
    
      css_icons='retina/lime'
      
    For a complete list of retina icons, check the :ref:`iconclass_retina` section
      