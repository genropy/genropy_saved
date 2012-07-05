
# # -*- coding: UTF-8 -*-
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
FONTFAMILIES = """Arial, Helvetica, sans-serif
Courier, monospace
'Comic Sans MS', cursive
Verdana, Geneva, sans-serif
'Palatino Linotype', 'Book Antiqua', Palatino, serif
'Times New Roman', Times, serif"""

class AppPref(object):
    def prefpane_sys(self, tc, **kwargs):
        tc = tc.tabContainer(**kwargs)
        stylepane = tc.contentPane(title='Styling')
        fb = stylepane.formbuilder(cols=1, border_spacing='4px',datapath='.theme')
        fb.filteringSelect(value='^.default_fontsize',values='!!12px:Small,13px:Medium,14px:Large,15px:Extra Large',lbl='Font size')
        fb.comboBox(value='^.rootstyle.font_family',values=FONTFAMILIES,lbl='Font family',width='20em')        
        
        pdfpane = tc.contentPane(title='Pdf render')
        fb = pdfpane.formbuilder(cols=1, border_spacing='4px',datapath='.pdf_render')
        fb.textbox(value='^.margin_top',lbl='Margin top')
        fb.textbox(value='^.margin_bottom',lbl='Margin bottom')
        fb.textbox(value='^.margin_left',lbl='Margin left')
        fb.textbox(value='^.margin_right',lbl='Margin right')



class UserPref(object):
    def prefpane_sys(self, tc, **kwargs):
        tc = tc.tabContainer(**kwargs)
        self.pref_cache(tc.contentPane(title='Caching', datapath='.cache'))
        self.pref_sound(tc.contentPane(title='Sounds', datapath='.sounds'))
        self.pref_theme(tc.contentPane(title='Theme', datapath='.theme'))

    def pref_theme(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.checkbox(value='^.bordered_icons',label='Bordered icons')
        fb.filteringSelect(value='^.rootstyle.font_size',values='!!12px:Default,12px:Small,13px:Medium,14px:Large,15px:Extra Large',lbl='Font size')
        fb.comboBox(value='^.rootstyle.font_family',values=FONTFAMILIES,lbl='Font family')

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
        fb.button('Reset session storage', action='if(sessionStorage){sessionStorage.clear();}')
        fb.button('Reset local storage', action='if(localStorage){localStorage.clear();}')


    def _allSounds(self):
        return """Basso:Basso,Blow:Blow,Bottle:Bottle,
                  Frog:Frog,Funk:Funk,Glass:Glass,Hero:Hero,
                  Morse:Morse,NewMessage:NewMessage,Ping:Ping,
                  Pop:Pop,Purr:Purr,Sosumi:Sosumi,sound1:Sound1,
                  Submarine:Submarine,Tink:Tink"""