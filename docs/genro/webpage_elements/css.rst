.. _genro_css:

===
CSS
===

    * :ref:`css_introduction`
    * :ref:`css_dojo_themes`
    * :ref:`css_genro_themes`
    * :ref:`css_genro_names`

.. _css_introduction:

Introduction
============

    CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.
    
    There are two ways of adding CSS style in Genro:
    
    #. The first way is the nearest to the standard way to use CSS. You have to create a CSS
       file, put it into your :ref:`genro_intro_resources` and call it into your page.
       
       .. warning:: you probably know the following syntax::
                    
                        <link href="stile/name_of_CSS_file.css" rel="stylesheet" type="text/css" />
                        
                    This syntax WON'T work.
                    
       In Genro you have to write in your :ref:`webpages_webpages` the following line::
       
        css_requires = 'name_of_CSS_file'
        
       (write the CSS filename without its ``.css`` extension).
       
       The ``css_requires`` is a :ref:`webpage variable <webpages_variables>`. For more information
       on it, check the :ref:`webpages_css_requires` documentation section.
       
    #. The second way is to use CSS style directly in your Genro :ref:`webpages_webpages`.
       When you do this, please pay attention that the CSS syntax is a little different
       from the standard CSS syntax; infact, you have to:
       
       #. use the underscore (``_``) character in place of the dash (``-``) character
       #. use the equal (``=``) character in place of the colon (``:``) character
       #. use the comma (``,``) character in place of the semi colon (``;``) character
       
       Let's see an example:
       
       The normal CSS style looks like this::
        
        font-size:'20pt';
        background-color:'teal';
        
       While the same CSS style in a Genro webpage looks like this::
        
        font_size='20pt',
        background_color='teal',
        
       When you write them on a single element the effect will be::
       
        root.textbox(font_size='20pt',background_color='teal',value='^hello')
        
    .. note:: you can use both the ways we just explained to you in a single file: you can
              import a CSS file with the :ref:`webpages_css_requires` and at the same time
              you can write additional style on some webpage elements.
       
    You should also know that:
    
    * Genro allows to use some CSS preset style: the :ref:`css_dojo_themes` and the Genro
      :ref:`css_genro_themes`
    * When you use CSS style directly in a Genro webpage there are some CSS attributes that
      have a different name respect to their standard CSS name: check the
      :ref:`css_genro_names` section for the complete list
      
.. _css_dojo_themes:

Dojo themes
===========

    The default Dojo theme for all the :ref:`webpages <webpages_webpages>` is 'tundra'.
    
    You can change a Dojo theme in your webpage: check the :ref:`webpages_dojo_theme` section
    for the correct syntax, the complete reference list of compatible Dojo themes and more.
    
.. _css_genro_themes:

CSS themes
==========

    CSS themes are Genro themes that modify the current Dojo theme of your webpage, adding or
    deleting some of their features.
    
    You can define your default CSS theme for all your pages in the :ref:`siteconfig_gui` tag
    of your :ref:`sites_siteconfig` or in a single :ref:`webpages_webpages` through the
    :ref:`webpages_css_theme` webpage variable.
    
    We list here the main Genro themes currently available:
    
    * *aqua*
    * *blue*
    * *elephant*
    * *pro*

.. _css_genro_names:

Genro CSS names
===============

    In the first section of this page (:ref:`css_introduction` section) we explain that you can
    use CSS style directly in your Genro :ref:`webpages_webpages`. In this section we list all
    the CSS attributes that have a different name respect to the standard CSS name.
    
    Click on the standard CSS name to go to the documentation line on the corresponding Genro CSS attribute:
    
    **Standard CSS name**:
    
    * :ref:`border-radius <css_border_radius>`
    * :ref:`box-shadow <css_box_shadow>`
    * :ref:`-moz-linear-gradient, -webkit-gradient<css_gradient_color>`
    * :ref:`css_transform`: :ref:`rotate <css_rotate>`, :ref:`translate <css_translate>`,
      :ref:`scale <css_scale>`, :ref:`skew <css_skew>`
    * :ref:`css_transition`
    
    .. _css_border_radius:
    
border-radius
-------------
    
    * Genro CSS name: rounded
    * Syntax: rounded=NUMBER
    * Example::
    
        rounded=10
        
    * Features: the *rounded* attribute support the top/bottom/left/right extensions::
    
        rounded=10
        rounded_bottom_right=8 # you can even write "rounded_right_bottom=8"... it is the same!
    
    .. _css_box_shadow:
    
box-shadow
----------

    * Genro CSS name: shadow
    * Syntax: shadow='NUMBER1,NUMBER2,NUMBER3,COLOR,inset'
    
      Where:

        * ``NUMBER1``: is the shadow on the x axis
        * ``NUMBER2``: is the shadow on the y axis
        * ``NUMBER3``: is the blur
        * ``COLOR``: is the shadow color
        * ``inset``: keyword for inset feature
        
    * Example::
    
        shadow='3px 3px 5px gray inset'
        
      You can write them separately::
        
        shadow_x='3px'
        shadow_y='3px'
        shadow_blur='5px'
        shadow_color='gray'
        shadow_inset=True
        
    .. _css_gradient_color:
    
-moz-linear-gradient, -webkit-gradient
--------------------------------------
    
    * Genro CSS name: gradient_color
    * Syntax: gradient_color_NUMBER='COLOR,OTHER_NUMBER'
    
      Where:
      
      * ``gradient_color``: is a keyword
      * ``NUMBER``: is a keyword number. If you use more than one gradient_color,
        please pay attention to not repeat NUMBER (it is merely a counter, so it
        is not the responsible for the order of the colors in your object)
      * ``COLOR``: the color you choose for your object
      * ``OTHER_NUMBER``: the percentage of your object width to be colored with
        COLOR (this is the responsible for the order of the colors in your object)
      
      
    * Example::
    
        pane.div('hello',width='8em',
                  gradient_color_3='blue,15',
                  gradient_color_7='teal,36',
                  gradient_color_1='yellow,50',
                  gradient_color_0='pink,80',
                  gradient_color_2='red,100')
                  
    .. _css_transform:

transform
---------

    .. _css_rotate:
    
    **rotate**
    
    * Genro CSS name: rotate
    * Syntax: transform_rotate=NUMBER
    
      Where:
      
      * ``transform_rotate``: is a keyword
      * ``NUMBER``: is a periodic number [0,360]
    
    * Example::
    
        transform_rotate=-90
        
    .. _css_translate:
    
    **traslate**
    
    * Genro CSS name: translate
    * Example::
    
        transform_translate_x=10
        transform_translate_y=30
        
    .. _css_scale:
    
    **scale**
    
    * Genro CSS name: scale
    * Example::
    
        transform_scale_x=30
        transform_scale_y=45
        
    .. _css_skew:
    
    **skew**
    
    * Genro CSS name: skew
    * Example::
        
        transform_skew_x=20
        transform_skew_y=36
        
    .. _css_transition:

transition
----------

    * Genro CSS name: transition
    * Example::
        
        transition='all 3s'
        transition_function=linear # possible values: linear,ease,ease-in,ease-out,ease-in-out
        transition_duration=NUMBER # NUMBER of seconds
    