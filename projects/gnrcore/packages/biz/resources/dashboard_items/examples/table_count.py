# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from gnrpkg.biz.dashboard import BaseDashboardItem

caption = 'Dashboard count'
description = 'Dashboard count records'
objtype = 'dash_example_tablecounter'
item_parameters = [{'value':'^.pkg','lbl':'Package','tag':'packageSelect'},
                    {'value':'^.table','lbl':'Table','tag':'tableSelect','validate_notnull':True,'pkg':'=.pkg'}]


class Main(BaseDashboardItem):
    title_template = '$title $table color $conf.color'

    def content(self,pane,table=None,**kwargs):
        count = self.db.table(table).query().count()
        pane.div(count,color='^.conf.color',
                   font_size='^.conf.size',**kwargs)

    def configuration(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.color',lbl='Color')
        fb.textbox(value='^.size',lbl='Size')

