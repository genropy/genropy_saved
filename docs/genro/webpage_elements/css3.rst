.. _css3:

====
CSS3
====

    *Last page update*: |today|
    
    .. note:: before reading this page please read the :ref:`introduction to CSS in Genro
              <css_intro>`, in order to learn how to use CSS in Genro
    
    * :ref:`css3_intro`
    * :ref:`css3_names`:
    
        * :ref:`css_border_radius`
        * :ref:`css_box_shadow`
        * :ref:`css_gradient_color`
        * :ref:`css_transform`
        * :ref:`css_transition`
        
    * :ref:`css3_examples`:
    
        * :ref:`css3_examples_rounded`
        * :ref:`css3_examples_shadow`
        * :ref:`css3_examples_gradient`
        * :ref:`css3_examples_transform`
        * :ref:`css3_examples_transition`
        
.. _css3_intro:

introduction
============

    CSS3 has introduced great improvements to CSS. But, as you know, the attributes change a little
    if you pass for example from Mozilla to WebKit. In Genro we remap all the CSS3 features, so
    every CSS only the Genro name
    
    **Example**:
    
        *-moz-linear-gradient* and *-webkit-gradient* become in Genro *gradient_color*
    
.. _css3_names:

CSS3 names
==========

    In this section we list all the CSS3 attributes with their Genro name.
    
    Click on the standard CSS name to go to the documentation line on the corresponding
    Genro CSS attribute:
    
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
        
    Check also the :ref:`css3_examples_rounded`
    
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
        
    Check also the :ref:`css3_examples_shadow`
    
.. _css_gradient_color:

-moz-linear-gradient, -webkit-gradient
--------------------------------------
    
    * Genro CSS name:
    
        * gradient_from_
        * gradient_to_
        * gradient_deg_
        * gradient_color_
        
.. _gradient_from:
    
    #. **gradient_from**:
       
       It is the starting color of the nuance (teal, black, #0065E7, #E3AA00, #960000)
       
       * Syntax: gradient_from=COLOR
       * Example::
       
           pane.div(gradient_from='black', gradient_to='white')
       
       .. _gradient_to:
    
    #. **gradient_to**:
       
       It is the ending color of the nuance (white, red, #29DFFA, #F4DC7F, #FD4042)
       
       * Syntax: gradient_to=COLOR
       * Example::
       
           pane.div(gradient_from='black', gradient_to='white')
       
       .. _gradient_deg:
    
    #. **gradient_deg**:
       
       It is the inclination angle of the color nuances. It can be any of the value
       between 0 and 360. To understand the numerical convention, think to a cartesian
       coordinate system. So:
       
       * 0   --> the color nuance follows the x axis towards the positive numbers
       * 90  --> the color nuance follows the y axis towards the positive numbers
       * 180 --> the color nuance follows the x axis towards the negative numbers
       * 270 --> the color nuance follows the y axis towards the negative numbers
       * 360 --> same meaning of the 0 value
       
       * Syntax: gradient_deg=NUMBER
       * Example::
       
          pane.div(gradient_from='black', gradient_to='white', gradient_deg=36)
          
       .. _gradient_color:
    
    #. **gradient_color**:
    
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
                  
    Check also the :ref:`css3_examples_gradient`
    
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
        
    Check also the :ref:`css3_examples_transform`
    
    .. _css_transition:

transition
----------

    * Genro CSS name: transition
    * Example::
        
        transition='all 3s'
        transition_function=linear # possible values: linear,ease,ease-in,ease-out,ease-in-out
        transition_duration=NUMBER # NUMBER of seconds
        
    Check also the :ref:`css3_examples_transition`
    
    .. _css3_examples:

examples
========

.. _css3_examples_rounded:

rounded example
---------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                sl = root.slotBar('fld,test,*')
                fb = sl.fld.formbuilder(cols=2,lbl_position='L',
                                        lbl_font_size='10px',lbl_color='teal')
                fb.horizontalSlider(value='^.top_left',minimum=0,maximum=30,
                                    intermediateChanges=True,width='150px',
                                    discreteValues=31,lbl='top_left')
                fb.numbertextbox(value='^.top_left',width='4em')
                fb.horizontalSlider(value='^.top_right',minimum=0,maximum=30,
                                    intermediateChanges=True,width='150px',
                                    discreteValues=31,lbl='top_right')
                fb.numbertextbox(value='^.top_right',width='4em')
                fb.horizontalSlider(value='^.bottom_left',minimum=0,maximum=30,
                                    intermediateChanges=True,width='150px',
                                    discreteValues=31,lbl='bottom_left')
                fb.numbertextbox(value='^.bottom_left',width='4em')
                fb.horizontalSlider(value='^.bottom_right',minimum=0,maximum=30,
                                    intermediateChanges=True,width='150px',
                                    discreteValues=31,lbl='bottom_right')
                fb.numbertextbox(value='^.bottom_right',width='4em')
                sl.test.div(margin='5px',margin_left='100px',display='inline-block',
                            border='1px solid gray',width='200px',height='80px',
                            rounded_top_left='^.top_left',
                            rounded_top_right='^.top_right',
                            rounded_bottom_left='^.bottom_left',
                            rounded_bottom_right='^.bottom_right')
                            
.. _css3_examples_shadow:

shadow example
--------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                sl = root.slotBar('x,y,blur,color,inset,*,test1,*',
                                  lbl_font_size='10px',lbl_width='12px',
                                  lbl_position='L',lbl_transform_rotate='-90',lbl_color='teal',
                                  cell_border='1px dotted gray')
                sl.x.verticalSlider(value='^.x',minimum=-30,maximum=30,intermediateChanges=True,
                                    height='100px',lbl='X')
                sl.y.verticalSlider(value='^.y',minimum=-30,maximum=30,intermediateChanges=True,
                                    height='100px',lbl='Y')
                sl.blur.verticalSlider(value='^.blur',minimum=-30,maximum=30,intermediateChanges=True,
                                       height='100px',lbl='blur')
                sl.color.comboBox(value='^.color',width='90px',lbl='color',
                                  values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                                            navy,olive,purple,red,silver,teal,white,yellow
                                            """)
                sl.inset.checkbox(value='^.inset',label='shadow_inset')
                sl.test1.div(margin='5px',display='inline-block',border='1px solid gray',
                             width='100px', height='80px',shadow='3px 3px 5px gray inset',
                             shadow_x='^.x',shadow_y='^.y',shadow_blur='^.blur',
                             shadow_color='^.color',shadow_inset='^.inset')
                             
.. _css3_examples_gradient:

gradient example
----------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                sl = root.slotBar('deg,fld,*,test,*,test1,*',lbl_position='B',lbl_font_size='8px')
                sl.deg.verticalSlider(value='^.deg',minimum=0,maximum=360,default=10,
                                      intermediateChanges=True,height='100px',lbl='Deg')
                fb = sl.fld.formbuilder(cols=6, border_spacing='2px')
                fb.data('.from','#4BA21A')
                fb.data('.to','#7ED932')
                fb.numbertextbox(value='^.deg',lbl='deg',width='4em')
                fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                                   values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                             #E3AA00:dark Orange,#C413A9:dark Pink,
                                             #960000:Dark Red""")
                fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                                   values="""#29DFFA:light Blue,#7ED932:light Green,
                                             #F4DC7F:light Orange,#FFCCED:light Pink,
                                             #FD4042:light Red""")
                sl.test.div(margin='5px', display='inline-block',
                            border='1px solid gray',width='100px',height='80px',
                            gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
                sl.test1.div(margin='5px', display='inline-block',
                             border='1px solid gray', width='100px', height='80px',
                             gradient_color_0='pink,15',gradient_color_1='yellow,50',gradient_color_2='red,100',
                             gradient_deg='^.deg')
                             
.. _css3_examples_transform:

transform example
-----------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                sl = root.slotBar('fld,*,test,*')
                fb = sl.fld.formbuilder(lbl_font_size='10px',lbl_color='teal')
                fb.horizontalSlider(value='^.rotate',minimum=0,maximum=180,lbl='rotate',
                                    intermediateChanges=True,width='150px',default_value=0)
                fb.horizontalSlider(value='^.translate_x',minimum=-100,maximum=100,lbl='translate_x',
                                    intermediateChanges=True,width='150px',default_value=0)
                fb.horizontalSlider(value='^.translate_y',minimum=-100,maximum=100,lbl='translate_y',
                                    intermediateChanges=True,width='150px',default_value=0)
                fb.horizontalSlider(value='^.scale_x',minimum=0,maximum=1,lbl='scale_x',
                                    intermediateChanges=True,width='150px',default_value=1)
                fb.horizontalSlider(value='^.scale_y',minimum=0,maximum=1,lbl='scale_y',
                                    intermediateChanges=True,width='150px',default_value=1)
                fb.horizontalSlider(value='^.skew_x',minimum=0,maximum=360,lbl='skew_x',
                                    intermediateChanges=True,width='150px',default_value=0)
                fb.horizontalSlider(value='^.skew_y',minimum=0,maximum=360,lbl='skew_y',
                                    intermediateChanges=True,width='150px',default_value=0)
                sl.test.div(margin='100px',display='inline-block',border='1px solid gray',width='90px',height='120px',
                            transform_rotate='^.rotate',
                            transform_translate_x='^.translate_x',transform_translate_y='^.translate_y',
                            transform_scale_x='^.scale_x',transform_scale_y='^.scale_y',
                            transform_skew_x='^.skew_x',transform_skew_y='^.skew_y')
            
.. _css3_examples_transition:

transition example
------------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                sl = root.slotBar('w,color,mode,duration,*,test',lbl_position='T',
                                   lbl_font_size='10px',lbl_color='teal')
                sl.w.textbox(value='^.w',lbl='width',default='3px',width='5em')
                sl.color.textbox(value='^.color',lbl='color',default='red',width='6em')
                sl.mode.combobox(value='^.function',default='linear',width='8em',
                                 values='linear,ease,ease-in,ease-out,ease-in-out')
                sl.duration.numbertextbox(lbl='duration',default=2,value='^.duration',width='8em')
                sl.test.div(width='^.w',background='^.color',height='50px',border='1px solid gray',
                            transition='all 3s',transition_function='.^function',transition_duration='^.duration')
            
            def test_6_gradient_color(self, pane):
                """gradient_color"""
                root.div('hello',width='8em',
                          gradient_color_3='blue,15',
                          gradient_color_7='teal,36',
                          gradient_color_1='yellow,50',
                          gradient_color_0='pink,80',
                      gradient_color_2='red,100')
        
    