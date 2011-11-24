.. _framepane:

=========
framePane
=========

    *Last page update*: |today|
    
    .. note:: framePane features:
    
              * **Type**: :ref:`Genro widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`frame_def`
    * :ref:`frame_attributes`:
    
        * :ref:`frame_design`
        * :ref:`frame_framecode`
        
    * :ref:`frame_examples`:
    
        * :ref:`frame_examples_simple`
        * :ref:`frame_examples_slotbar`
        
.. _frame_def:

definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.framepane
    
    In the framePane you have at disposition five sides, that are: ``top``, ``bottom``, ``left``,
    ``right``, ``center``.
    
    Every *side* can be highly customized with regard to the look and with regard to its tools.
    
    To customize these regions, you have to follow this procedure:
    
    #. Create your framePane, assigning a name, like::
       
         GnrCustomWebPage(object):
             def test_1_sides(self, pane):
                 frame = pane.framePane(...)
                 
       (where ``pane`` is a :ref:`layout element <layout>` to which you attached the framePane)
       
    #. Use one of the five sides to attach your elements:
    
         * use ``top`` for the top region
         * use ``bottom`` for the top region
         * use ``left`` for the top region
         * use ``right`` for the top region
         
         Example::
         
             frame.bottom.div('This is my bottom')
             
    #. In order to attach something to the ``center`` region, you have to attach it to the name
       of your framePane, like in the following lines::
       
         frame = pane.framePane(...)
         frame.div('Hello!')
         
    For more information, check the :ref:`frame_examples_simple`
    
.. _frame_attributes:

attributes
==========

.. _frame_design:

design
------
    
    (Dojo attribute): define the layout of the element. For more information, check the
    :ref:`design` page. Default value is ``headline``
    
.. _frame_framecode:

frameCode
---------
        
    MANDATORY. Create a :ref:`nodeid` for the framePane AND create hierarchic :ref:`nodeIds
    <nodeid>` for every framePane child
      
    **Example**::
      
        frameCode='frame1'
        
.. _frame_examples:

examples
========

.. _frame_examples_simple:

simple example
--------------

    * `framePane [autoslots] <http://localhost:8080/webpage_elements/widgets/layout/framepane/1>`_
    * **Description**: an example of the autoslots you can use in the framePane
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`includedview`, :ref:`testhandlerfull`
                * **widgets**: :ref:`datetextbox`, :ref:`slotBar <toolbar>`, :ref:`slotbutton`,
                  :ref:`slotToolbar <toolbar>`
                  
    * **Introduction**: pay attention to the following things:
    
        * In line 14 we attach to the framePane a slotToolbar::
        
            frame.top.slotToolbar
            
          we don't define anywhere ``top``, infact it is one of the framePane autoslots
          
        * Like line 14, we can see the others in the following lines:
        
          * line 20 - "bottom" slot: ``frame.bottom.slotToolbar``)
          * line 24 - "left" slot: ``frame.left.slotToolbar``)
          * line 26 - "right" slot: ``frame.right.slotToolbar``)
          * to attach some elements to the "center" slot, you have to attach them to
            framePane name (line 9 - in this example, "frame". In line 28 we attach
            a div to the center
          
    * **Code**::
    
        1   # -*- coding: UTF-8 -*-
        2   """framePane"""
        3   
        4   class GnrCustomWebPage(object):
        5       py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
        6       
        7       def test_1_basic(self, pane):
        8           """Basic example"""
        9           frame = pane.framePane(frameCode='test1', design='headline',
       10                                  height='400px', width='855px', shadow='3px 3px 5px gray',
       11                                  rounded=5, border='1px solid #bbb', margin='10px',
       12                                  center_border='1px solid #bbb',
       13                                  center_background='#E7EDF5')
       14           top = frame.top.slotToolbar(slots='30,foo,*,my_buttons,50,boooo,15',height='20px')
       15           top.foo.div('Title...', font_size='1.2em')
       16           for i in ['info', 'key', 'keyboard', 'inbox', 'money', 'paper_plane', 'revert']:
       17               top.my_buttons.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s action')" %i)
       18           for i in ['add_record', 'delete_record', 'lock']:
       19               top.boooo.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s action')" %i)
       20           bottom = frame.bottom.slotToolbar(slots='30,btoh,*,goofy,30', height='30px')
       21           for i in range(1,11):
       22               bottom.btoh.slotButton(label=i, action='alert("Action of button n.%s")' %i)
       23           bottom.goofy.dateTextbox(width='14em')
       24           left = frame.left.slotToolbar('*,pr,*', height='342px')
       25           left.pr.slotButton('!!Prev',iconClass="iconbox previous", action='alert("Passing to the previous one...")')
       26           right = frame.right.slotToolbar('*,nxt,*', height='342px')
       27           right.nxt.slotButton('!!Next',iconClass="iconbox next", action='alert("Passing to the next one...")')
       28           frame.div('This is the center', margin='20px')
       
.. _frame_examples_slotbar:

slotToolbar, slotBar example
----------------------------

    * `framePane [toolbars] <http://localhost:8080/webpage_elements/widgets/layout/framepane/2>`_
    * **Description**: an example of :ref:`toolbars <slotbar>` with :ref:`css3`
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`includedview`, :ref:`testhandlerfull`
                * **methods**: :meth:`~gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.gridStruct`,
                  :meth:`~gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.selectionStore`
                * **widgets**: :ref:`combobox`, :ref:`contentpane`, :ref:`data`, :ref:`filteringselect`,
                  :ref:`formbuilder`, :ref:`numbertextbox`, :ref:`slotBar <slotbar>`, :ref:`slotbutton`,
                  :ref:`slotToolbar <slotbar>`, :ref:`verticalSlider <slider>`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """slotBar and slotToolbar"""
        
        import datetime
        
        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                             foundation/includedview"""
            workdate = datetime.datetime.now().date()
            
            def test_2_toolbars(self, pane):
                """slotBar, slotToolbar and CSS3"""
                pane.data('.color','black')
                pane.data('.from','#C4BFBD')
                pane.data('.to','#D6D1CE')
                pane = pane.framePane(frameCode='test2',height='350px',width='700px',
                                      shadow='3px 3px 5px gray',rounded=10,
                                      border='1px solid #bbb',margin='10px',
                                      center_background='#E1E9E9')
                top = pane.top.slotToolbar(slots='10,hello,*,foo,*,searchOn',
                                           height='25px',gradient_from='^.from',gradient_to='^.to')
                view = pane.includedView(_newGrid=True)
                struct = view.gridStruct('name')
                view.selectionStore(table='showcase.person',order_by='$name',
                                    _onStart=True,storeCode='mystore')
                top.hello.div(str(self.workdate),color='^.color')
                top.foo.div('Schedule',font_size='14pt',color='^.color')

                left = pane.left.slotToolbar(slotbarCode='left',slots='10,foo,*',width='40px',
                                             gradient_from='^.from',gradient_to='^.to')
                for i in ['star', 'save', 'print']:
                    left.foo.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s')" %i)

                right = pane.right.slotBar(slotbarCode='right',slots='20,dummy,*',width='130px',
                                           gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
                fb = right.dummy.formbuilder(lbl_color='^.color',cols=2)
                fb.div('Settings',font_size='12pt',color='^.color',colspan=2)
                fb.comboBox(lbl='color',value='^.color',width='90px',colspan=2,
                            values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                                      navy,olive,purple,red,silver,teal,white,yellow
                                      """) # A complete list of CSS 3 basic color keywords
                fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                                   values="""#8CBAD5:Blue,#FEFE87:Yellow,
                                             #E3AA00:Orange,#C4BFBD:Gray,
                                             #FB4343:Red""")
                fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                                   values="""#9FE5F8:light Blue,#FFFED7:light Yellow,
                                             #F4DC7F:light Orange,#D6D1CE:light Gray,
                                             #FE6E61:light Red""")
                fb.verticalSlider(value='^.deg',minimum=0,maximum=360,discreteValues=361,
                                  intermediateChanges=True,height='100px',lbl='Deg')
                fb.numbertextbox(value='^.deg',lbl='deg',width='3em')

                bottom = pane.bottom.slotToolbar(slots='300,bar,*',height='20px',
                                                 gradient_from='^.from',gradient_to='^.to')
                bottom.bar.div('Here goes the messages for user',color='^.color')