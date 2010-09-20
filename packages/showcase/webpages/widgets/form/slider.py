# -*- coding: UTF-8 -*-

# slider.py
# Created by Niso on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Slider"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =========
     Sliders
    =========

    .. currentmodule:: form

    .. class:: Sliders -  Genropy sliders
    
    **Definition**: same definition of Dojo slider (version 1.4). To show it, click here_.
    
    .. _here: http://docs.dojocampus.org/dijit/form/Slider

    	Here we introduce the sliders, form widgets inherit from Dojo. It is a scale with a handle you can drag left/right for horizontal slider (or up/down for vertical one) to select a value.

    	+-------------------------+---------------------------------------------------------+-------------+
    	|   Attribute             |          Description                                    |   Default   |
    	+=========================+=========================================================+=============+
    	| ``default='NUMBER'``    | Add a default value in your slider                      |  ``0``      |
    	+-------------------------+---------------------------------------------------------+-------------+
    	| ``intermediateChanges`` | (Boolean) If True, it allows to changes value of slider |  ``False``  |
    	|                         | during slider move                                      |             |
    	+-------------------------+---------------------------------------------------------+-------------+
    	| ``maximum='NUMBER'``    | Add the maximum value of a slider                       |  ``100``    |
    	+-------------------------+---------------------------------------------------------+-------------+
    	| ``minimum='NUMBER'``    | Add the minimum value of a slider                       |  ``0``      |
    	+-------------------------+---------------------------------------------------------+-------------+

    	It is strongly advised to use "width" attribute for horizontal slider and "height" attribute for vertical slider.
    	
    	#NISO: ho visto che per Dojo 1.1 c'è un attributo chiamato showButtons che sembra non funzionare... (e tra l'altro c'è anche in Dojo 1.5...) la domanda è: "ci sono degli attributi che non avete riportato da Dojo, o è un errore?"

    		Example::

    			pane.horizontalSlider(value='^integer_number',width='200px',
    								  maximum=50,discreteValues=51)
    """
    
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to slider.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       action          --> button.py
    #       button          --> button.py
    #       comboBox        --> combobox.py
    #       filteringSelect --> filteringSelect.py
    #       formbuilder     --> formbuilder.py
    #       numberTextBox   --> textbox.py
    #       splitter        --> webpages/widgets/layout/border.py
    #       value           --> datapath.py
    
    def test_1_simple(self,pane):
        """Simple vertical slider"""
        fb=pane.formbuilder(datapath='test1',cols=2)
        fb.verticalSlider(value='^.number',height='100px')
        fb.numberTextbox(value='^.number',lbl='height')
        
    def test_2_simple(self,pane):
        """Simple horizontal slider"""
        fb=pane.formbuilder(datapath='test2',cols=4)
        pane.data('test2.decimals','2')
        fb.horizontalSlider(value='^.integer_number',width='200px',maximum=50,
                            discreteValues=51,lbl='!!Integer number')
        fb.numberTextBox(value='^.integer_number',width='4em',colspan=2)
        fb.div("""With "discreteValues", "minimum" and "maximum" attributes you can allow to
                  write only integer numbers.""",
                font_size='.9em',text_align='justify')
                
        fb.horizontalSlider(value='^.float_number',width='200px',minimum=10,
                            default=25,lbl='!!Float number')
        fb.numberTextBox(value='^.float_number',width='4em',places='^.decimals')
        fb.numberSpinner(value='^.decimals',width='4em',min=0,max=15,lbl='decimals')
        fb.div("""Here you can choose the number of decimals.""",
                font_size='.9em',text_align='justify')
        
    def test_3_hslider(self,pane):
        """Horizontal slider"""
        fb=pane.formbuilder(datapath='test3',cols=4)
        fb.data('.icon','icnBaseOk')
        fb.data('.fontfam','Courier')
        fb.dataFormula('.width_calc','w+umw',w='^.width',umw='^.um_width')
        fb.dataFormula('.font_size','font+umf',font='^.font',umf='^.um_font')
        
        fb.horizontalSlider(value='^.width',width='200px',default=8,minimum=3,
                            intermediateChanges=True,lbl='!!Width button')
        fb.numberTextBox(value='^.width',width='4em')
        fb.comboBox(value='^.um_width',width='5em',values='em,px,%',default='em')
        fb.br()
        
        fb.horizontalslider(value='^.font',width='200px',default=11,minimum=4,
                            discreteValues=97,intermediateChanges=True,lbl='!!Width font')
        fb.numberTextBox(value='^.font',width='4em')
        fb.comboBox(value='^.um_font',width='5em',values='pt,px',default='pt')
        fb.filteringSelect(value='^.fontfam',width='8em',lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
        fb.filteringSelect(value='^.icon',width='5em',colspan=4,lbl='icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')
        fb.button('Save it',action="alert('Saving!')",tooltip='click me',colspan=4,
                  ffont_size='^.font_size',font_family='^.fontfam',
                  iconClass='^.icon',width='^.width_calc')
