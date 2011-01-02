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

class AppPref(object):
    def prefpane_sys(self, tc, **kwargs):
        pane = tc.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.numberTextBox(value='^.personal', lbl='!!Personal info')

class UserPref(object):
    def prefpane_sys(self, tc, **kwargs):
        tc = tc.tabContainer(**kwargs)
        self.pref_cache(tc.contentPane(title='Caching', datapath='.cache'))
        self.pref_sound(tc.contentPane(title='Sounds', datapath='.sounds'))


    def pref_sound(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.filteringSelect(value='^.onsaving', lbl='On saving', values=self._allSounds(),
                           validate_onAccept='genro.playSound(value);')
        fb.filteringSelect(value='^.onsaved', lbl='On saved', values=self._allSounds(),
                           validate_onAccept='genro.playSound(value);')
        fb.filteringSelect(value='^.error', lbl='On error', values=self._allSounds(),
                           validate_onAccept='genro.playSound(value);')

    def pref_cache(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.checkbox(value='^.dbselect', label='Dbselect enable')
        fb.button('Reset session storage', action='if(sessionStorage){sessionStorage.clear();}')
        fb.button('Reset local storage', action='if(localStorage){localStorage.clear();}')


    def _allSounds(self):
        return """Basso:Basso,Blow:Blow,Bottle:Bottle,
                  Frog:Frog,Funk:Funk,Glass:Glass,Hero:Hero,
                  Morse:Morse,NewMessage:NewMessage,Ping:Ping,
                  Pop:Pop,Purr:Purr,Sosumi:Sosumi,sound1:Sound1,
                  Submarine:Submarine,Tink:Tink"""