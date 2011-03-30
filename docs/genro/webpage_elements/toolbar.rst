.. _genro_toolbar:

=======================
slotToolbar and slotBar
=======================
    
    * :ref:`toolbar_def`
    * :ref:`toolbar_attributes`
    * :ref:`toolbar_examples`: :ref:`toolbar_examples_simple`
    
.. _toolbar_def:

Definition
==========

    The slotToolbar and the slotBar are used to create easily a toolbar. With toolbar
    we mean a set of icons, buttons, widgets and more over objects.
    
    The only difference between the slotToolbar and slotBar is their transparency.
    The slotBar is transparent while the slotToolbar is not.
    
    Since the others features are common, we talk only about the slotToolbar.
    
    The slotToolbar can be attached to any div::
    
         class GnrCustomWebPage(object):
                def main(self,root,**kwargs):
                    root.div('Hello!',margin='20px').slotToolbar(...)
        
    You can use it in combo with a :ref:`genro_framepane`::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                frame = root.framePane(...)
                top = frame.top.slotToolbar(...)
                left = frame.left.slotToolbar(...)
                right = frame.right.slotToolbar(...)
                bottom = frame.bottom.slotBar(...)
                
.. _toolbar_attributes:

Attributes
==========

    * *slotbarCode*: MANDATORY - autocreate a :ref:`genro_nodeid` for the slotToolbar AND autocreate
      hierarchic nodeIds for every slotToolbar child. Default value is ``None``.
    * *slots*: MANDATORY - create a configurable UI inside the div or pane in which the
      slotToolbar is defined.
      
      **syntax**::
      
        slots='firstParam,secondParam,...,lastParam'
        
      An important feature of the *slots* attribute is that the toolbars are coded with the help
      of the :ref:`attributes_childname`. This fact implies that you can call any of the slots
      through their slot name::
      
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                top = root.div().slotToolbar(slotbarCode='top',slots='test,foo,dummy')
                top.test.div('Hello!')
                top.foo.div('MyTitle',font_size='14pt',color='^.color')
                top.dummy.button(label='add',iconClass='icnBaseAdd',action="alert('Added!')")
                
      **parameters**:
      
      * A vertical bar (``|``) creates a splitter bar
      * A NUMBER creates a white space equal to NUMBER pixels
      * A star (``*``) creates a white space, occupying the free space of the slotToolbar, that is the space
        that is not filled by slots parameter. If you use more than one star, then they take all the
        free space dividing it in equal parts::
        
            slotToolbar(slots='20,*,|,*')
            
        In this example we have an empty space of 20 pixels followed by two empty star spaces
        separated by a vertical bar. The two stars occupied all the space that "20" and "|"
        didn't take.
        
      * *orientation* add??? V (vertical), H (horizontal) default???
      * You can add color nuances with the following three attributes:
      
        * *gradient_from*: the starting color
        * *gradient_to*: the ending color
        * *gradient_deg*: the inclination angle of the color nuances. It can be any of the
          value between 0 and 360. To understand the numerical convention, think to a
          cartesian plane. So:
            
            * 0   --> the color nuance follows the x axis towards the positive numbers
            * 90  --> the color nuance follows the y axis towards the positive numbers
            * 180 --> the color nuance follows the x axis towards the negative numbers
            * 270 --> the color nuance follows the y axis towards the negative numbers
            * 360 --> same meaning of the 0 value
            
        * *gradient_color_NUMBER*: you can specify more than two colors in place of the
          colors defined through the *gradient_from* and the *gradient_to* attributes::
            
            gradient_color_0='pink,15',gradient_color_1='yellow,50',gradient_color_2='red,100'
            
        Pay attention: if you use the slotToolbar you CAN'T modify the *gradient_deg* attribute.
        You can only modify the *gradient_from* and the *gradient_to* attributes::
        
            class GnrCustomWebPage(object):
                def main(self,root,**kwargs):
                    root.div().slotToolbar(slotbarCode='top',slots='hello,foo,dummy',
                                           gradient_from='red',gradient_to='white')
        
        If you use the slotBar, remember that by default it is transparent, but you
        can use all gradient color features (*gradient_from*, *gradient_to* and *gradient_deg*)::
            
            class GnrCustomWebPage(object):
                def main(self,root,**kwargs):
                    root.div().slotBar(slotbarCode='yeah',slots='hello,*,hello2',
                                       gradient_from='red',gradient_to='white',
                                       gradient_degree='36')
                  
        Here is another example::
        
          class GnrCustomWebPage:
              def main(self,root,**kwargs):
                  sl = root.slotBar('deg,fld,*,test,*,test1,*',lbl_position='B',lbl_font_size='8px')
                  
                  sl.deg.verticalSlider(value='^.deg',minimum=0,maximum=360,
                                        intermediateChanges=True,height='100px',lbl='Deg')
                  fb = sl.fld.formbuilder(cols=6, border_spacing='2px')
                  fb.numbertextbox(value='^.deg',lbl='deg',width='4em')
                  sl.test.div(margin='5px', display='inline-block',
                              border='1px solid gray', width='100px', height='80px',
                              gradient_from='white',gradient_to='navy',gradient_deg='^.deg')
                              
                  sl.test1.div(margin='5px', display='inline-block',
                               border='1px solid gray', width='100px', height='80px',
                               gradient_color_0='pink,15',gradient_color_1='yellow,50',
                               gradient_color_2='red,100',gradient_deg='^.deg')
                                 
      * You can specify the position of slots label. Pay attention that, as the toolbars are built
        on the :ref:`genro_formbuilder`, to modify the labels you have to use the *lbl* attribute,
        not the *label* attribute::
        
            lbl_position='T' # possible values: 'T' (top), 'B' (bottom), 'L' (left), 'R' (right)
            lbl_font_size='7px' # possible values: px, em, ex
            lbl_color='red' # possible values: any of the RGB color
            lbl_width='12px' # possible values: px, em, ex
            lbl_transform_rotate='-90' # a value from 0 to 360 (or from -360 to 0)
            
      * You can also add :ref:`iv_searchbox`, :ref:`iv_searchon` or :ref:`iv_messageBox`, attributes of
        the includedView component::
        
            slots='20,messageBox,*,searchOn'
            
        For more information, check the :ref:`genro_includedview` documentation page
        
.. _toolbar_examples:

Examples
========

.. _toolbar_examples_simple:

simple example
--------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                workdate = str(datetime.datetime.now().date())
                root.data('.color','white')
                root.data('.from','#4BA21A')
                root.data('.to','#7ED932')
                
                frame = root.framePane(frameCode='framecode',height='400px',
                                       shadow='3px 3px 5px gray',rounded=10,
                                       border='1px solid #bbb',margin='10px',
                                       center_background='#E1E9E9')
                top = frame.top.slotToolbar(slotbarCode='top',slots='10,hello,*,foo,*,dummy',
                                            height='25px',gradient_from='^.from',gradient_to='^.to')
                top.hello.div(workdate,color='^.color')
                top.foo.div('Schedule',font_size='14pt',color='^.color')
                top.dummy.button(label='add',iconClass='icnBaseAdd',showLabel=False,
                                 action="alert('Added a row in your grid')")
                top.dummy.button(label='del',iconClass='icnBaseDelete',showLabel=False,
                                 action="alert('Deleted a row in your grid')")
                top.dummy.button(label='email',iconClass='icnBaseEmail',showLabel=False,
                                 action="alert('Sended your schedule by email')")
                top.dummy.button(label='pdf',iconClass='icnBasePdf',showLabel=False,
                                 action="alert('PDF created')")
                top.dummy.button(label='',iconClass='icnBaseExport',showLabel=False,
                                 action="alert('Exported in an Excel file')")
                top.dummy.button(label='print',iconClass='icnBasePrinter',showLabel=False,
                                 action="alert('Printed')")
                                 
                left = frame.left.slotBar(slotbarCode='left',slots='10,foo,*',width='40px',
                                          gradient_from='^.from',gradient_to='^.to',gradient_deg='0')
                left.foo.button('new grid',action="alert('New schedule!')")
                left.foo.button('save grid',action="alert('Saved!')")
                left.foo.button('load grid',action="alert('Loaded!')")
                left.foo.button('exit', action="alert('Exited!')")
                
                right = frame.right.slotBar(slotbarCode='left',slots='20,dummy,*',width='130px',
                                            gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
                fb = right.dummy.formbuilder(lbl_color='^.color',cols=2)
                fb.div('Settings',font_size='12pt',color='^.color',colspan=2)
                fb.comboBox(lbl='color',value='^.color',width='90px',colspan=2,
                            values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                                      navy,olive,purple,red,silver,teal,white,yellow
                                      """) # A complete list of CSS 3 basic color keywords
                fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                                   values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                             #E3AA00:dark Orange,#C413A9:dark Pink,
                                             #960000:Dark Red""")
                fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                                   values="""#29DFFA:light Blue,#7ED932:light Green,
                                             #F4DC7F:light Orange,#FFCCED:light Pink,
                                             #FD4042:light Red""")
                fb.verticalSlider(value='^.deg',minimum=0,maximum=360,discreteValues=361,
                                  intermediateChanges=True,height='100px',lbl='Deg')
                fb.numbertextbox(value='^.deg',lbl='deg',width='3em')
                
                bottom = frame.bottom.slotToolbar(slots='300,bar,*,searchOn',height='20px',
                                                  gradient_from='^.from',gradient_to='^.to')
                bottom.bar.div('Here goes the messages for user',color='^.color')
                
                sb = frame.div('Remember: a slotToolbar (or a slotBar) can be attached to any div!',
                                margin='20px',color='black').slotToolbar(slotbarCode='top',slots='10,hello,*,dummy',
                                                                         height='25px',gradient_from='^.from',gradient_to='^.to')
                sb.hello.button('Click me!',action='alert("Hello!!!")')
                sb.dummy.button(label='',iconClass='icnBasePref',showLabel=False,
                                action="alert('A wonderful action!')")
                frame.div('Here goes the \"center\" content.',margin='20px')