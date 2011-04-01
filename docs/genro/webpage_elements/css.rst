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
        
    * You can import css files in your :ref:`genro_project` through the *css_requires*
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

    We list here all the CSS attributes that have a different name respect to the standard CSS name
    (or all the attributes that should have an owner name, like -moz-, -webkit- and so on).
    
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
      
      Where:

        * ``rounded``: is a keyword
        * ``NUMBER``: is a number
        
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

        * ``NUMBER1...NUMBER3``: are the shadow on the x axis, the shadow on the y axis and the blur
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
        please pay attention to not repeat NUMBER
      * ``COLOR``: the color you choose for your object
      * ``OTHER_NUMBER``: the percentage of your object width to be colored with COLOR
      
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
    