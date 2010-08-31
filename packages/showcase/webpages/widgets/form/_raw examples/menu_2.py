#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main_(self,root):
        root.data('values.states',self.tableData_states())
        root.css('.colorpalettemenu .dijitMenuItemHover','background-color:transparent;')
        root.css('.colorpalettemenu .dijitMenuItem td','padding:0;')
        root.css('.colorpalettemenu .dijitMenuItemIcon','display:none;')
        root.data('tempcolor','emptypath')
        root.div().menu(modifiers='*',id='colorPalettemenu',_class='colorPaletteMenu',
                            connect_onOpen="""
                                            var path= this.widget.originalContextTarget.sourceNode.absDatapath();
                                            SET tempcolor=path;""",
                        ).menuItem(datapath='^tempcolor').colorPalette(value='^.color')
        root.dataController("sourceNode=dijit.byId('colorPalettemenu').originalContextTarget.sourceNode;",color="^temp.color")
        for i in range (1,5):
            root.div(width='20px',height='20px',border='1px solid gray',
                     background_color='^.color',connectedMenu='colorPalettemenu',datapath='c%i' % i)
            
    def main(self,root):
        root.data('values.states', self.tableData_states())
        fb = root.formbuilder(cols=1, border_spacing='4px')
        x = fb.div(height='30px',width='50px',background_color='red')
        x.menu(modifiers='*',storepath='values.states',action='alert($1.caption);',selected_id='aaa')
        x.div('^aaa')
        fb.filteringSelect(storepath='values.states',selected_caption='aaa')
        fb.button('addItem to menu',action='genro.setData("values.states.r6",null,{caption:"Washington",id:"WA"})')
        fb.button('delItem to menu',action='genro._data.pop("values.states.r6");')
        
    def tableData_states(self):
        mytable=Bag()
        mytable.setItem('r1',None,id='CA',caption='California')
        mytable.setItem('r2',None,id='IL',caption='Illinois')
        mytable.setItem('r3',None,id='NY',caption='New York')
        mytable.setItem('r4',None,id='TX',caption='Texas')
        mytable.setItem('r5',None,id='AL',caption='Alabama')        
        return mytable