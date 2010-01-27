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
Component for thermo:
"""
from gnr.web.gnrwebpage import BaseComponent

class RecordLinker(BaseComponent):
    def recordLinker(self,fb,table=None,dialogPars=None,record_template=None,record_path=None,lbl=None,
                    value=None,width=None,height=None,colspan=1,rowspan=1,disabled=False,**kwargs):
        """docstring for recordLinker"""
        selectorBox = fb.div(lbl=lbl,lbl_vertical_align='top',
                            min_height=height,width=width,colspan=colspan,
                            rowspan=rowspan,position='relative')
        selector = selectorBox.dbSelect(value=value,dbtable=table,position='absolute',
                                        left='0px',right='0px',top='0px',**kwargs)
            
        selector.button('!!Add',position='absolute',right='2px',z_index='100',iconClass='icnBaseAdd',
                        baseClass='no_background', showLabel=False,disabled=disabled,
                        connect_onclick='FIRE attestazione.pkey;',top='-3px')
        
        selectorViewer = selectorBox.div(innerHTML='==dataTemplate(_tpl,_data)',
                            _data='^%s' %record_path,
                            _tpl=record_template,_class='box_tpl',
                            position='absolute',
                            background_color='white',top='16px',bottom='0px',
                            left='1px',right='1px',border='1px solid silver',
                            border_top='0px',style="""-moz-border-radius-bottomleft:6px;
                                                      -moz-border-radius-bottomright:6px;
                                                    """)
        selectorViewer.button('!!Edit',baseClass='no_background',showLabel=False,
                    right='2px',z_index='100',bottom='2px',position='absolute',
                    action='FIRE #%s.pkey = GET %s;' %(dialogPars['dlgId'], value[1:]),
                    iconClass='icnBaseEdit',disabled=disabled)
          
        assert 'dlgId' in dialogPars, 'this param is mandatory'
        assert not 'firedPkey' in dialogPars, 'firedPkey is used by the component'     
        assert not 'savedPath' in dialogPars, 'savedPath is used by the component'                  
             
        selectorBox.dataRecord(record_path,table,pkey=value,_if='pkey')
        selectorBox.dataController("FIRE %s = savedId;" %value[1:],
                                    savedId='=#%s.savedId' %dialogPars['dlgId'],
                                    _fired='^#%s.recordSaved' %dialogPars['dlgId'])
        onSaved = ''
        if 'onSaved' in dialogPars:
            onSaved = dialogPars.pop('onSaved')
        self.recordDialog(table,firedPkey='^#%s.pkey' %dialogPars['dlgId'],
                         onSaved='FIRE #%s.recordSaved; %s' %(dialogPars['dlgId'],onSaved),
                         savedPath='#%s.savedId' %dialogPars['dlgId'],**dialogPars)

    