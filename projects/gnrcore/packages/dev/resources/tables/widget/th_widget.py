#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_name')
        r.fieldcell('summary')

    def th_order(self):
        return 'hierarchical_name'

    def th_query(self):
        return dict(column='hierarchical_name', op='contains', val='')



class Form(BaseComponent):
    py_requires ="""gnrcomponents/dynamicform/dynamicform:DynamicForm"""

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2)
        fb.field('name',width='20em')
        fb.field('server',html_label=True)

        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='!!Parameters').fieldsGrid(margin='2px',rounded=6,border='1px solid silver') #ok
        bc = tc.borderContainer(title='!!Documentation')
        bc.roundedGroupFrame(title='!!Summary',region='top',height='50%',splitter=True).simpleTextArea('^#FORM.record.summary',colspan=3,height='100px',editor=True)
        bc.contentPane(region='center').bagGrid(storepath='#FORM.record.docrows',title='!!Parameters doc',
                                                                struct=self.documentation_struct,
                                                                addrow=False,delrow=False,pbl_classes=True,
                                                                margin='2px')

        tc.dataController("""
                var new_docrows = new gnr.GnrBag();
                var old_docrows = old_docrows || new gnr.GnrBag();
                fieldsdata.forEach(function(n){
                        var v = n.getValue();
                        var old_v = old_docrows.getItem(n.label) || new gnr.GnrBag();
                        var docv = new gnr.GnrBag({code:v.getItem('code'),documentation:old_v.getItem('documentation'),datatype:old_v.getItem('datatype') || v.getItem('data_type')});
                        new_docrows.setItem(n.label,docv);
                    });

                SET #FORM.record.docrows = new_docrows;
            """,fieldsdata='^#FORM.record.df_fields',old_docrows='=#FORM.record.docrows',_delay=500)


    def documentation_struct(self,struct):
        r = struct.view().rows()
        r.cell('code',width='10em',name='!!Code')
        r.cell('datatype',name='Type',width='8em',edit=dict(tag='ComboBox',values='Text,Bool,Int,Decimal,Date,Bag,list,callable,json,Other'))
        r.cell('documentation',name='!!Documentation',width='40em',edit=dict(tag='quickEditor'))


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',hierarchical=True,duplicate=True)
