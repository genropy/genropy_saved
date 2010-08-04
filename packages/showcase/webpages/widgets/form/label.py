# -*- coding: UTF-8 -*-

# label.py
# Created by Niso on 2010-08-04.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        cp = root.contentPane(margin='1em',padding='10px')
        fb = cp.formBuilder(datapath='myform')
        
        fb.div('############### button ##############')
        fb.button(lbl='text_1')
        fb.button(label='text_2')
        fb.button('text_3')
        
        fb.div('############### checkbox #############')
        fb.checkbox(lbl='text_1')
        fb.checkbox(label='text_2')
        fb.checkbox('text_3')
        
        fb.div('############# combobox #############')
        fb.combobox(lbl='text_1')
        fb.combobox(label='text_2')
        fb.combobox('text_3')
        
        fb.div('############# currencyTextbox #############')
        fb.currencyTextbox(lbl='text_1')
        fb.currencyTextbox(label='text_2')
        fb.currencyTextbox('text_3')
        
        fb.div('############# dateTextBox #############')
        fb.dateTextBox(lbl='text_1')
        fb.dateTextBox(label='text_2')
        fb.dateTextBox('text_3')
        
        fb.div('############# dbSelect ##############')
        fb.dbSelect(lbl='text_1')
        fb.dbSelect(label='text_2')
        fb.dbSelect('text_3')
        
        fb.div('################ div ################')
        fb.div(lbl='text_1')
        fb.div(label='text_2') # --> non compare
        fb.div('text_3')
        
        fb.div('########### dropdownbutton ##########')
        fb.toolbar().dropdownbutton(lbl='text_1').menu()
        fb.toolbar().dropdownbutton(label='text_2').menu()
        fb.toolbar().dropdownbutton('text_3').menu()
        
        fb.div('############## field ###############')
        fb.field('showcase.cast.person_id',lbl='text_1',zoom=False)
        fb.field('showcase.cast.person_id',label='text_2',zoom=False) # --> il label è sbagliato (appare "people"!)
        #fb.field('text_3','showcase.cast.person_id',zoom=False)        --> da' errore!
        
        fb.div('############# filteringSelect ##########')
        fb.filteringSelect(lbl='text_1')
        fb.filteringSelect(label='text_2')
        fb.filteringSelect('text_3')
        
        fb.div('############# horizontalSlider ##########')
        fb.horizontalSlider(lbl='text_1')
        fb.horizontalSlider(label='text_2')
        fb.horizontalSlider('text_3')
        
        fb.div('############### menu ###############')
        menu = fb.dropdownbutton(lbl='menu con \'lbl\'').menu()
        menu.menuline(lbl='text_1')
        menu.menuline(label='text_2')
        menu.menuline('text_3')
        
        menu = fb.dropdownbutton(label='menu con \'label\'').menu()
        menu.menuline(label='text_2')
        
        menu = fb.dropdownbutton('menu con \' \'').menu()
        menu.menuline(label='text_2')
        
        fb.div('############# numberSpinner ##########')
        fb.numberSpinner(lbl='text_1')
        fb.numberSpinner(label='text_2')
        fb.numberSpinner('text_3')
        
        fb.div('############# numberTextbox ##########')
        fb.numberTextbox(lbl='text_1')
        fb.numberTextbox(label='text_2')
        fb.numberTextbox('text_3')
        
        fb.div('############# radiobutton ##########')
        fb.radiobutton(lbl='text_1',group='radio')
        fb.radiobutton(label='text_2',group='radio')
        fb.radiobutton('text_3',group='radio')
        
        fb.div('########### simpleTextarea ###########')
        fb.simpleTextarea(lbl='text_1')
        fb.simpleTextarea(label='text_2')
        fb.simpleTextarea('text_3')
                
        fb.div('############### span ###############')
        fb.span(lbl='text_1')
        fb.span(label='text_2')
        fb.span('text_3')
        
        fb.div('########## td (table data) ###########')
        fb.td(lbl='text_1')
        fb.td(label='text_2')
        fb.td('text_3')
        
        fb.div('############### textArea ###############')
        fb.textArea(lbl='text_1')
        fb.textArea(label='text_2')
        fb.textArea('text_3')
        
        fb.div('############### textbox ###############')
        fb.textbox(lbl='text_1')
        fb.textbox(label='text_2')
        fb.textbox('text_3')
        
        fb.div('############# timeTextbox #############')
        fb.timeTextbox(lbl='text_1',iconClass="dijitRadioIcon")
        fb.timeTextbox(label='text_2',iconClass="dijitRadioIcon")
        fb.timeTextbox('text_3',iconClass="dijitRadioIcon")
        
        fb.div('############# toggleButton #############')
        fb.toggleButton(lbl='text_1',iconClass="dijitRadioIcon")
        fb.toggleButton(label='text_2',iconClass="dijitRadioIcon")
        fb.toggleButton('text_3',iconClass="dijitRadioIcon")
        
        