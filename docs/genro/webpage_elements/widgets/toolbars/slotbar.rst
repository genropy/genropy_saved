.. _slotbar:

=======================
slotBar and slotToolbar
=======================
    
    *Last page update*: |today|
    
    .. note:: slotBar (and slotToolbar) features:
    
              * **Type**: :ref:`Genro widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    *In the image, a slotBar*
    
    .. image:: ../../../_images/commons/attributes/childname_slotbar.png
    
    * :ref:`slotbar_def`
    * :ref:`slotbar_descr`
    * :ref:`slotbar_attributes`:
    
        * :ref:`slotbar_slots`
        * :ref:`slotbar_slots_specials`
        * :ref:`slotbar_namespace`
        
    * :ref:`slotbar_callback`
    * :ref:`slotbar_examples`:
    
        * :ref:`slotbar_examples_simple_slotbar`
        * :ref:`slotbar_examples_simple_slottoolbar`
        * :ref:`slotbar_examples_containers`
        * :ref:`slotbar_examples_framepane`
        * :ref:`slotbar_examples_cb`
        
.. _slotbar_def:

definition
==========

    **slotBar definition**:
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.slotBar
    
    **slotToolbar definition**:
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.slotToolbar
    
.. _slotbar_descr:

description
===========

    As we previously said in the :ref:`definition section <slotbar_def>`, the only differences
    between the slotToolbar and slotBar are that the slotToolbar has some preset CSS attribute
    From now on we speak only of the slotBar, pointing up the differences respect to the
    slotToolbar when we meet them within the explanation
              
    * The slotBar can be attached to any div and to any :ref:`contentpane`)::
      
        class GnrCustomWebPage(object):
               def main(self,root,**kwargs):
                   root.div().slotBar()
                   root.contentPane().slotBar()
                   
    * You can use it in combo with a :ref:`framepane`, obtaining something like this:
      
        *In the image, a framePane with four slotBars (one for each side)*:
        *check the code in the* :ref:`slotbar_examples_framepane`
        
        .. image:: ../../../_images/widgets/toolbars/slotbar_framepane.png
        
    * There are two ways to create a slotBar: the standard (and the easiest) way, that it is
      focused on the usage of the :ref:`slots` attribute, and the :ref:`slotbar_callback`.
      Continue through the next section to learn the standard way to create a slotBar
      
.. _slotbar_attributes:

attributes explanation
======================

.. _slotbar_slots:

slots
-----

    The slots attribute is MANDATORY.
    
    It is a string of parameters [#]_ (and eventually some :ref:`special characters
    <slotbar_slots_specials>`) separated by a comma
    
    **syntax**::
    
      slots = 'firstParam,secondParam,...,lastParam'
      
    Through these parameters you can append every element you need::
    
        sb = pane.slotBar(slots='goofy,*,dummy')
        sb.goofy.button('new', action='...')
        sb.goofy.button('save', action='...')
        sb.goofy.button('load', action='...')
        sb.dummy.dateTextbox('...')
        
    The ``*`` is a special character, that we discuss in the following section
    
.. _slotbar_slots_specials:
              
slots - special characters
--------------------------
              
    Within the :ref:`slotbar_slots` attribute you can also use these special characters:
    
    * vertical bar (``|``) - create a splitter bar
    * NUMBER - create a white space equal to NUMBER pixels
    * star (``*``) - create a white space, occupying the free space of the slotBar,
      that is the space that is not filled by slots parameter. If you use more than one
      star, then they take all the free space dividing it in equal parts
      
        **Example**::
        
            slotBar(slots='20,*,|,*')
            
        We have an empty space of 20 pixels followed by two empty star spaces separated by a
        vertical bar. The two stars occupied all the space that "20" and "|" didn't take. The
        width/height occupied from the slotBar is the dimension of the container in which
        it is set (or, if you define a width/height inside the slotBar, it is that space)
    * You can add any :ref:`css` or :ref:`css3` attributes (as you can do in any
      :ref:`webpage element <we>`), but pay attention that if you use
      the slotToolbar, then you CAN'T modify the :ref:`gradient_deg <css_gradient_color>`
      attribute; you can only modify the :ref:`gradient_from <css_gradient_color>` and the
      :ref:`gradient_to <css_gradient_color>` attributes::
      
          class GnrCustomWebPage(object):
              def main(self,root,**kwargs):
                  root.div().slotToolbar(slotbarCode='top',slots='hello,foo,dummy',
                                         gradient_from='red',gradient_to='white')
                                         
      If you use the slotBar, remember that by default it is transparent, but you
      can use all the gradient color features (:ref:`gradient_from <css_gradient_color>`,
      :ref:`gradient_to <css_gradient_color>`, :ref:`gradient_deg <css_gradient_color>`)::
      
          class GnrCustomWebPage(object):
              def main(self,root,**kwargs):
                  root.div().slotBar(slotbarCode='yeah',slots='hello,*,hello2',
                                     gradient_from='red',gradient_to='white',
                                     gradient_degree='36')
                                     
    * You can also add one of the :ref:`Genro default slots <slots>`::
      
          slots='20,messageBox,*,searchOn'
          
      .. _slotbar_namespace:
      
namespace
---------

    TODO
    
.. _slotbar_callback:

callback way
============

    You can create a slotBar (or a slotToolbar) through a callback
    
    **Syntax**:
    
    #. For the call method you have to write::
    
        LAYOUT.slotbar_NAME()
        
       where:
       
       * ``LAYOUT`` is a :ref:`layout widget <layout>` or a div to which you have
         attached the slotbar
       * ``slotbar`` is a keyword, and doesn't change if you are using a slotBar or
         a slotToolbar. It is *always* ``slotbar``
         
       Remember that the *slots* attribute is mandatory; you can define it with a ``0``
       or with a ``#``::
       
        LAYOUT.slotbar_NAME(slots='0') # Your callback methods will be set on the slotBar left side
        LAYOUT.slotbar_NAME(slots='#') # Your callback methods will be set on the slotBar right side
        
    #. The callback method follows this syntax::
    
        @struct_method
        def NAME2_slotbar_NAME([*params], **kwargs):
            pane.[...] # attach to this pane all the elements you need...
            
       where:
       
       * ``NAME`` is the callback name. Be sure that in the call method you write the same ``NAME``
       * ``NAME2`` is a (mandatory) prefix for the callback
       * ``slotbar`` is a keyword, and doesn't change if you are using a slotBar or a slotToolbar.
         It is *always* ``slotbar``
         
    Remember to import the :meth:`~gnr.web.gnrwebstruct.struct_method`::
    
        from gnr.web.gnrwebstruct import struct_method
    
    **Example**::
    
        1   from gnr.web.gnrwebstruct import struct_method
        2   
        3   class GnrCustomWebPage(object):
        4       def main(self, root, **kwargs):
        5           pane = root.slotToolbar(slots='0')
        6           pane.slotbar_form_dismiss()
        7           
        8   @struct_method
        9   def pippo_slotbar_form_dismiss(self, pane, caption=None, iconClass=None, **kwargs):
       10       pane.slotButton('!!Dismiss',iconClass="iconbox dismiss")
       
    * In line 1 we import the :meth:`~gnr.web.gnrwebstruct.struct_method`
    * In lines 3 and 4 we create the :ref:`gnrcustomwebpage` and the :ref:`webpages_main` method
    * In line 5 we create the slotToolbar
    * In line 6 there is the call: TODO
    
    The result is the following one:
    
    .. image:: ../../../_images/widgets/toolbars/slotbar_cb_zero.png
    
    For a more complete example, check the :ref:`slotbar_examples_cb`
    
.. _slotbar_examples:

examples
========

.. _slotbar_examples_simple_slotbar:

simple example - slotBar
------------------------

    * `slotBar [basic] <http://localhost:8080/webpage_elements/widgets/toolbars/slotbar/1>`_
      
      .. note:: example elements' list:

                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`data`, :ref:`datetextbox`, :ref:`formbuilder`, :ref:`slotbutton`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """slotBar"""

        import datetime

        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
            workdate = datetime.datetime.now().date()
            
            def test_1_basic(self,pane):
                """Basic example"""
                pane.data('.date', self.workdate)
                top = pane.div().slotBar(slotbarCode='top_0',slots='dummy,*,foo,boo,goo',
                                         gradient_from='#94E3FB', gradient_to='#BEF4FC', gradient_deg=-90)
                fb = top.dummy.formbuilder(lbl_width='3em', lbl_color='teal', fld_width='14em')
                fb.dateTextbox(lbl='Date', value='^.date')
                top.foo.slotButton('Save', iconClass='iconbox save', action="alert('Saved data')")
                top.boo.slotButton('Delete', iconClass='iconbox trash', action="alert('Deleted data')")
                top.goo.slotButton('New document', iconClass='iconbox document', action="alert('Starting new document...')")
                
    .. _slotbar_examples_simple_slottoolbar:

simple example - slotToolbar
----------------------------

    * `slotToolbar [basic] <http://localhost:8080/webpage_elements/widgets/toolbars/slottoolbar/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`data`, :ref:`datetextbox`, :ref:`formbuilder`, :ref:`slotbutton`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """slotToolbar"""

        import datetime

        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
            workdate = datetime.datetime.now().date()
            
            def test_1_basic(self,pane):
                """Basic example"""
                pane.data('.date', self.workdate)
                top = pane.div().slotToolbar(slotbarCode='top_0',slots='dummy,*,foo,boo,goo')
                fb = top.dummy.formbuilder(lbl_width='3em', lbl_color='teal', fld_width='14em')
                fb.dateTextbox(lbl='Date', value='^.date')
                top.foo.slotButton('Save', iconClass='iconbox save', action="alert('Saved data')")
                top.boo.slotButton('Delete', iconClass='iconbox trash', action="alert('Deleted data')")
                top.goo.slotButton('New document', iconClass='iconbox document', action="alert('Starting new document...')")
                
    .. _slotbar_examples_containers:

containers example
------------------

    * `toolbars [div, contentPane] <http://localhost:8080/webpage_elements/widgets/toolbars/toolbars/1>`_
    * **Description**: an example of suitable containers for the toolbars
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`button`, :ref:`contentpane`, :ref:`slotbutton`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Toolbars containers"""

        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
            
            def test_1_div(self, pane):
                """slotToolbar and toolBar attached on a div"""
                pane.div('You can attach a slotBar to any div:',
                          margin='0.5em', font_size='1.2em')
                top = pane.div().slotBar(slotbarCode='code',slots='hello,foo,dummy',
                                             gradient_from='#EED250',gradient_to='#F3DD8B',
                                             gradient_deg=-90)
                top.hello.div('Hello!')
                top.foo.div('MyTitle',font_size='14pt',color='^.color')
                top.dummy.button(label='add',iconClass='icnBaseAdd',action="alert('Added!')")

                pane.div('And you can attach a slotBar even to a contentPane:',
                          margin='0.5em', font_size='1.2em')
                cp = pane.contentPane().slotBar(slotbarCode='yeah2',height='40px',
                                                slots='*,hello',
                                                gradient_from='#ACACAC',gradient_to='#DEDEDE')
                cp.hello.slotButton('click me', iconClass='iconbox sum', action='alert("clicked!")')
        
    .. _slotbar_examples_framepane:

framePane example
-----------------

    * `toolbars [framePane, CSS3] <http://localhost:8080/webpage_elements/widgets/toolbars/toolbars/2>`_
    * **Description**: an example of toolbars with the :ref:`framepane` widget and with :ref:`css3`
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`includedview`, :ref:`testhandlerfull`
                * **methods**: :meth:`~gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.gridStruct`,
                  :meth:`~gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.selectionStore`
                * **widgets**: :ref:`combobox`, :ref:`contentpane`, :ref:`data`, :ref:`filteringselect`,
                  :ref:`formbuilder`, :ref:`framepane`, :ref:`numbertextbox`, :ref:`slotbutton`,
                  :ref:`verticalSlider <slider>`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """slotBar and slotToolbar"""

        from gnr.web.gnrwebstruct import struct_method
        import datetime

        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                             foundation/includedview"""
            workdate = datetime.datetime.now().date()
            
            def test_2_features(self,pane):
                """framePane, slotToolbar and CSS 3"""
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
                
    .. _slotbar_examples_cb:

callback example
----------------

    Let's see an example of a slotBar created through the :ref:`slotbar_callback`
    
    .. image:: ../../../_images/widgets/toolbars/slotbar_cb_one.png
    
    * `toolbars [Callback] <http://localhost:8080/webpage_elements/widgets/toolbars/toolbars/3>`_
    * **Description**: an example of toolbars with the :ref:`framepane` widget and with :ref:`css3`
    
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **methods**: :meth:`~gnr.web.gnrwebstruct.struct_method`
                * **widgets**: :ref:`slotbutton`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """slotBar and slotToolbar"""

        from gnr.web.gnrwebstruct import struct_method
        import datetime

        class GnrCustomWebPage(object):
            py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
            workdate = datetime.datetime.now().date()
            
            def test_3_cb(self, pane):
                """Callback Slotbar"""
                pane = pane.slotToolbar(slots='0')
                pane.slotbar_form_navigation()

            @struct_method
            def sb_slotbar_form_navigation(self, pane, **kwargs):
                pane = pane.div(lbl='!!Navigation',_class='slotbar_group')
                pane.slotbar_form_dismiss()
                pane.slotbar_form_first()
                pane.slotbar_form_prev()
                pane.slotbar_form_next()
                pane.slotbar_form_last()
                
            @struct_method
            def sb_slotbar_form_dismiss(self, pane, caption=None, iconClass=None, **kwargs):
                pane.slotButton('!!Dismiss',iconClass="iconbox dismiss",
                                 action='alert("Dismissing...")')

            @struct_method          
            def sb_slotbar_form_first(self,pane,**kwargs):
                pane.slotButton('!!First',iconClass="iconbox first",
                                 action='alert("Passing to the first one...")')

            @struct_method          
            def sb_slotbar_form_prev(self,pane,**kwargs):
                pane.slotButton('!!Prev',iconClass="iconbox previous",
                                 action='alert("Passing to the previous one...")')

            @struct_method          
            def sb_slotbar_form_next(self,pane,**kwargs):
                pane.slotButton('!!Next',iconClass="iconbox next",
                                 action='alert("Passing to the next one...")')

            @struct_method          
            def sb_slotbar_form_last(self,pane,**kwargs):
                pane.slotButton('!!Last',iconClass="iconbox last",
                                 action='alert("Passing to the last one...")')
                                 
    **Footnotes**:

.. [#] These parameters work as :ref:`childnames <childname>`. For an example on the usage of childnames in the *slots* attribute, please check the :ref:`childname_examples_slotbar`