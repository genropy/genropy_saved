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
         rect=root.div(_class='shadow_2 rounded_medium',border='1px solid green',margin_top='20px',margin_left='20px')
        
        fb = rect.formbuilder(cols=2, border_spacing='12px',datapath='data',margin_top='20px',margin_left='20px')
        fb.dbSelect(dbtable='portal.diagnosi',columns='$codice,$descrizione',limit=30,
                    auxColumns='$codice,$descrizione',value='^.codice_diagnosi',
                    _class='gnrfield',lbl='!!Diagnosi',width='40em',hasDownArrow=True)
        fb.div('^.codice_diagnosi',lbl='!!Codice')
        fb.dbSelect(dbtable='portal.procedura',columns='$codice,$descrizione',limit=30,
                    auxColumns='$codice,$descrizione',value='^.codice_procedura',
                    _class='gnrfield',lbl='!!Procedure',width='40em',hasDownArrow=True)
        fb.div('^.codice_procedura',lbl='!!Codice')
        