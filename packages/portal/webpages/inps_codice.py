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

class GnrCustomWebPage(object):
    def windowTitle(self):
        return 'Codici'
         
    def main(self, root, **kwargs):
        bc=root.borderContainer()
        top=bc.contentPane(height='30px',background_color='#2e0215',color='white')
        bc.iframe(src='http://www.inps.it',height='100%',width='100%',border='0px')
        fb = top.formbuilder(cols=2, border_spacing='3px',datapath='data',
                              margin_top='3px',margin_left='5px',float='left')
        
        fb.dbSelect(dbtable='portal.diagnosi',columns='$codice,$descrizione',limit=30,
                    auxColumns='$codice,$descrizione',value='^.codice_diagnosi',
                    _class='gnrfield',lbl='!!Diagnosi',width='50em',hasDownArrow=True,lbl_color='white')
        fb.textbox(value='^.codice_diagnosi',lbl='!!Codice',readOnly=True,width='5em',lbl_color='white',lbl_width='10em')
        top.div('Genropy',margin_right='10px',margin_top='10px',font_size='.8em',float='right')
         
        