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

import os
import random

class AppPref(object):
    def permission_adm(self,**kwargs):
        return 'admin'

    def prefpane_adm(self,tc,**kwargs):
        tc = tc.tabContainer(**kwargs)
        tab_logo = tc.contentPane(title='!!Logo')
        fb = tab_logo.formbuilder(cols=2, border_spacing='4px')
        fb.numberTextBox(value='^.personal',lbl='!!Personal info')
        logobox = tab_logo.div(height='135px',width='135px',
                                    margin_left='3em',margin_top='40px',
                                padding='0px',background_color='white')
        logobox.img(style='width: 135px;',src='^aux.app.logoPath',_fired='^uploaded')

        tab_logo.button('!!Upload logo',action='FIRE aux.app.uploadLogo;',
                    margin_left='6em',margin_top='4ex',width='135px')
        
        tab_logo.dataRpc('aux.app.logoPath','logoUrl',_onStart=True,_fired='^aux.app.uploaded')
        tab_logo.dataController('genro.dlg.upload(msg,"uploadLogo","imgPath",{},label,cancel,send,fireOnSend)',
                               msg='!!Choose file',cancel='!!Cancel',label='!!Browse...',
                               send='!!Send', fired='^aux.app.uploadLogo',fireOnSend='aux.app.uploaded')
                               
        
    def template_name_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('name', name='!!Name', width='12em')
        r.cell('design', name='!!Design', width='6em')
        return struct


    def rpc_logoUrl(self):
        return '%s?nocache=%i'%(self.app_logo_url(),random.randint(1,1000))

    def rpc_uploadLogo(self,fileHandle=None,ext=None,**kwargs):
        f=fileHandle.file
        content=f.read()
        current_logo = self.custom_logo_path()
        if current_logo:
            if os.path.isfile(current_logo):
                os.remove(current_logo)
        filename='custom_logo%s' % ext
        old_umask = os.umask(2)
        path=self.site.site_static_path('_resources','images','logo',filename)
        dirname=os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        outfile=file(path, 'w')
        outfile.write(content)
        outfile.close()
        os.umask(old_umask)
        result=self.app_logo_url()
        return "<html><body><textarea>%s</textarea></body></html>" % (str(result))