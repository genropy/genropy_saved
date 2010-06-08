# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
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

"""
Component for referto:
"""

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return ''
         
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='devlang.developer',value='^developer_id',rowcaption='$last_name,$first_name')
        center = bc.contentPane(region='center')
        center.remote('language_form',developer_id='^developer_id') #so the center has a remote content
    
    def remote_language_form(self,pane,developer_id=None,**kwargs):
        #IMPORTANT developer_id is being evaluated so is the real pkey
        languages = self.db.table('devlang.dev_lang').query(columns='*,@language_id.name AS lang_name',where='$developer_id=:d_id',
                                                            d_id=developer_id).fetch()
        for lang in languages:
            row = pane.div()
            row.div(lang['lang_name'],float='left')
            for i in range(int(lang['level'])):
                row.div(height='3px',width='3px',background='green',float='left',margin='2px')
            
            pane.br()
            