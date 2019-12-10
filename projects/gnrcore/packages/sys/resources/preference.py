
# # -*- coding: utf-8 -*-
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

from gnr.core.gnrdecorator import public_method

FONTFAMILIES = """Arial, Helvetica, sans-serif
Courier, monospace
'Comic Sans MS', cursive
Verdana, Geneva, sans-serif
'Palatino Linotype', 'Book Antiqua', Palatino, serif
'Times New Roman', Times, serif"""

class AppPref(object):
    def prefpane_sys(self, tc, **kwargs):
        tc = tc.tabContainer(margin='2px',**kwargs)
        stylepane = tc.contentPane(title='Styling')
        fb = stylepane.formbuilder(cols=1, border_spacing='4px',datapath='.theme')
        fb.filteringSelect(value='^.theme_variant',values='blue,red,green,yellow,orange,',lbl='Theme variant')
        fb.horizontalSlider(value='^.body.filter_rotate',intermediateChanges=True,width='150px',default_value=0,
                        minimum=0,maximum=360,lbl='Color rotate',livePreference=True)
        fb.horizontalSlider(value='^.body.filter_invert',intermediateChanges=True,width='150px',default_value=0,
                        minimum=0,maximum=1,lbl='Color invert',livePreference=True)
        fb.filteringSelect(value='^.default_fontsize',values='!!12px:Small,13px:Medium,14px:Large,15px:Extra Large',lbl='Font size')
        fb.comboBox(value='^.body.font_family',values=FONTFAMILIES,lbl='Font family',width='20em',livePreference=True)        
        fb.textbox(value='^.palette_colors',lbl='Default color palette')
        fb.textbox(value='^.palette_steps',lbl='Default color steps')


        pdfpane = tc.borderContainer(title='Print')
        fb = pdfpane.roundedGroup(title='Print Modes',
                                    region='top',height='100px').formbuilder(cols=1, border_spacing='4px')
        fb.checkbox(value='^.print.ask_options_enabled',label='!![en]Print Options Enabled')
        fb.checkBoxText(value='^.print.modes',values='pdf:PDF,server_print:Server Print,mail_pdf:PDF Mail,mail_deliver:Mail Deliver',lbl='Print modes')
        fb.checkbox(value='^.print.enable_pdfform',label='Enable pdf forms (Requires pdftk)')
        fb = pdfpane.roundedGroup(title='PDF Render',region='center').formbuilder(cols=1, border_spacing='4px',datapath='.pdf_render')
        fb.textbox(value='^.margin_top',lbl='Margin top')
        fb.textbox(value='^.margin_bottom',lbl='Margin bottom')
        fb.textbox(value='^.margin_left',lbl='Margin left')
        fb.textbox(value='^.margin_right',lbl='Margin right')
        fb.textbox(value='^.zoom',lbl='Pdf zoom',width='5em')
        fb.checkbox(value='^.keep_html',label='Keep HTML (for debug)')
        
        dev = tc.contentPane(title='Developer')
        fb = dev.formbuilder()
        fb.checkbox(value='^.jsPdfViewer',label='Extended pdf viewer')
        fb.comboBox(value='^.experimental.remoteForm',lbl='Remote forms',values='onEnter,delayed')

        self.site_config_override(tc.contentPane(title='!!Site config',datapath='.site_config'))

        pane = tc.contentPane(title='Tables Configuration')
        fb = pane.formbuilder(cols=1,border_spacing='3px',datapath='.tblconf')
        fb.textbox(value='^.archivable_tag',lbl='Archivable tag')

    def site_config_override(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.numberTextBox(value='^.cleanup?interval',lbl='Cleanup interval',placeholder=self.site.config['cleanup?interval'])
        fb.numberTextBox(value='^.cleanup?page_max_age',lbl='Page max age',placeholder=self.site.config['cleanup?page_max_age'])
        fb.numberTextBox(value='^.cleanup?connection_max_age',lbl='Connection max age',placeholder=self.site.config['cleanup?connection_max_age'])


    @public_method
    def _resetMemcached(self):
        self.site.shared_data.flush_all()


class UserPref(object):
    def prefpane_sys(self, tc, **kwargs):
        tc = tc.tabContainer(margin='2px',**kwargs)
        self.pref_cache(tc.contentPane(title='Caching', datapath='.cache'))
        self.pref_sound(tc.contentPane(title='Sounds', datapath='.sounds'))
        self.pref_shortcuts(tc.contentPane(title='Shortcuts', datapath='.shortcuts'))
        self.pref_theme(tc.contentPane(title='Theme', datapath='.theme'))



    def pref_theme(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.checkbox(value='^.bordered_icons',label='Bordered icons')
        fb.filteringSelect(value='^.rootstyle.font_size',values='!!12px:Default,12px:Small,13px:Medium,14px:Large,15px:Extra Large',lbl='Font size')
        fb.comboBox(value='^.rootstyle.font_family',values=FONTFAMILIES,lbl='Font family')

    def pref_sound(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.filteringSelect(value='^.onsaving', lbl='On saving', values=self._allSounds(),
                           validate_onAccept='if(value){genro.playSound(value);}')
        fb.filteringSelect(value='^.onsaved', lbl='On saved', values=self._allSounds(),
                           validate_onAccept='if(value){genro.playSound(value);}')
        fb.filteringSelect(value='^.error', lbl='On error', values=self._allSounds(),
                           validate_onAccept='if(value){genro.playSound(value);}')

    def pref_cache(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.button('Reset session storage', action='if(sessionStorage){sessionStorage.clear();}')
        fb.button('Reset local storage', action='if(localStorage){localStorage.clear();}')

    def pref_shortcuts(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.comboBox(value='^.save',values='f1,alt+s,cmd+s',lbl='Save',placeholder='f1')
        fb.comboBox(value='^.reload',values='f9,alt+r',lbl='Reload',placeholder='f9')
        fb.comboBox(value='^.dismiss',values='alt+up,alt+q',lbl='Dismiss',placeholder='alt+up')
        fb.comboBox(value='^.next_record',values='alt+right',lbl='Next record',placeholder='alt+right')
        fb.comboBox(value='^.prev_record',values='alt+left',lbl='Prev record',placeholder='alt+left')
        fb.comboBox(value='^.last_record',values='ctrl+alt+right',lbl='Last record',placeholder='ctrl+alt+right')
        fb.comboBox(value='^.first_record',values='ctrl+alt+left',lbl='First record',placeholder='ctrl+alt+left')
        fb.comboBox(value='^.jump_record',values='alt+j',lbl='Jump record',placeholder='alt+j')




    def _allSounds(self):
        return """Basso:Basso,Blow:Blow,Bottle:Bottle,Frog:Frog,Funk:Funk,Glass:Glass,Hero:Hero,Morse:Morse,NewMessage:NewMessage,Ping:Ping,Pop:Pop,Purr:Purr,Sosumi:Sosumi,sound1:Sound1,Submarine:Submarine,Tink:Tink"""