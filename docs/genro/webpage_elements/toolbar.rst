.. _genro_toolbar:

=======================
slotToolbar and slotBar
=======================
    
    * :ref:`toolbar_def`
    * :ref:`toolbar_attributes`
    * :ref:`toolbar_examples`: :ref:`toolbar_examples_simple`
    
.. _toolbar_def:



    The slotToolbar and the slotBar are used to create easily a toolbar. With toolbar we mean a set
    of icons, buttons, widgets and more over objects.
    
    The only difference between the slotToolbar and slotBar is their transparency. The slotBar is
    transparent while the slotToolbar is not.
    
    .. image:: add??? image!
    
    
    Since the others features are common, we refer only
    to the slotToolbar.
    
Definition
==========
    
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
    * *slots*: MANDATORY - create a configurable UI. You have to write every param followed by a comma.
      
      **syntax**::
      
        slots='firstParam,secondParam,...,lastParam'
        
      The toolbars are coded with the help of the :ref:`attributes_attachname`, so you can
      --> dire che gli slots sono attachnam-ati!
      
      :parameters:
      
      * A vertical bar (``|``) creates a splitter bar.
      * A NUMBER creates a white space equal to NUMBER pixels::
      
            slots='20,|,10,'
        
        In this example we have an empty space of 20 pixels followed by a vertical bar followed by an empty
        space of 10 pixels.
        
      * A star (``*``) creates a white space, occupying the free space of the slotToolbar, that is the space
        that is not filled by slots parameter. If you use more than one star, then they take all the
        free space dividing it in equal parts.
        
        Example::
        
            slotToolbar(slots='20,*,|,*')
            
        In this example we have an empty space of 20 pixels followed by two empty star spaces separated by
        a vertical bar. The two stars occupied all the space that "20" and "|" didn't take.
        
      * *orientation* add??? V (vertical), H (horizontal) default???
      **gradient color features**:
      
      You can add color nuances with the following three attributes:
      
      .. note:: if you use the slotToolbar you CAN'T modify the *gradient_deg* attribute (but you can modify the
                *gradient_from* and the *gradient_to* attributes)
                
                If you use the slotBar, remember that by default it is transparent, but you can use all gradient
                color features: *gradient_from*, *gradient_to* and *gradient_deg*.
      
      * *gradient_from*: the starting color
      * *gradient_to*: the ending color
      * *gradient_deg*: the inclination angle of the color nuances:
        0   --> x axis, positive numbers
        90  --> y axis, positive numbers
        180 --> x axis, negative numbers
        270 --> y axis, negative numbers
        
        Here is an example::
        
            class GnrCustomWebPage:
                def main(self,root,**kwargs):
                    sl = pane.slotBar('deg,fld,*,test,*,test1,*',lbl_position='B',lbl_font_size='8px')
                    
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
                                 
      * *lbl_position='T'* *lbl_color='red'* *lbl_font_size='7px'* (slotBar attributes, or CSS attributes
                                                                    for every object?)
        LBL! not label (infact the slotBar is built on formbuilder... right???)
      * *border_bottom='1px solid #bbb'*
      * *showLabel=False* --> bottom.foo.button('!!Save',iconClass="icnBaseOk",showLabel=False) (default --> True)
      * You can also add :ref:`iv_searchbox`, :ref:`iv_searchon` or :ref:`iv_messageBox`, attributes of
        the :ref:`genro_includedview` component::
        
            slots='20,dummy,*,searchOn'
            
.. _toolbar_examples:

Examples
========

    add???

.. _toolbar_examples_simple:

simple example
--------------

    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                workdate = str(datetime.datetime.now().date())
                pane.root('color','white')
                pane.root('from','#4BA21A')
                pane.root('to','#7ED932')
                
                frame = root.framePane(frameCode='framecode',height='400px',
                                       shadow='3px 3px 5px gray',rounded=10,
                                       border='1px solid #bbb',margin='10px',
                                       center_background='#E1E9E9')
                top = frame.top.slotToolbar(slotbarCode='top',slots='10,hello,*,foo,*,dummy',
                                            height='25px',gradient_from='^from',gradient_to='^to')
                top.hello.div(workdate,color='^color')
                top.foo.div('Schedule',font_size='14pt',color='^color')
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
                                 
                left = frame.left.slotToolbar(slotbarCode='left',slots='10,foo,*',width='40px',
                                              gradient_from='^from',gradient_to='^to')
                left.foo.button('new grid',action="alert('New schedule!')")
                left.foo.button('save grid',action="alert('Saved!')")
                left.foo.button('load grid',action="alert('Loaded!')")
                left.foo.button('exit', action="alert('Exited!')")
                
                right = frame.right.slotToolbar(slotbarCode='left',slots='20,dummy,*',
                                                width='200px',gradient_from='^from',gradient_to='^to')
                fb = right.dummy.formbuilder(lbl_color='^color')
                fb.div('Settings',font_size='12pt',color='^color')
                fb.comboBox(lbl='color',value='^color',width='90px',
                            values='black,white,yellow,red,brown,grey,green,blue')
                fb.filteringSelect(lbl='gradient_from',value='^from',width='90px',
                                   values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                             #E3AA00:dark Orange,#C413A9:dark Pink,
                                             #960000:Dark Red""")
                fb.filteringSelect(lbl='gradient_to',value='^to',width='90px',
                                   values="""#29DFFA:light Blue,#7ED932:light Green,
                                             #F4DC7F:light Orange,#FFCCED:light Pink,
                                             #FD4042:light Red""")
                                             
                bottom = frame.bottom.slotToolbar(slots='300,bar,*,searchOn',height='20px',
                                                  gradient_from='^from',gradient_to='^to')
                bottom.bar.div('Here goes the messages for user',color='^color')
                
                sb = frame.div('Remember: a slotToolbar (or a slotBar) can be attached to any div!',
                                margin='20px',color='black').slotToolbar(slotbarCode='top',slots='10,hello,*,dummy',
                                                                         height='25px',gradient_from='^from',gradient_to='^to')
                sb.hello.button('Click me!',action='alert("Hello!!!")')
                sb.dummy.button(label='',iconClass='icnBasePref',showLabel=False,
                                action="alert('A wonderful action!')")
                frame.div('Here goes the \"center\" content',margin='20px')