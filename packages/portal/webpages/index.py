#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """

from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='publicsite:SiteLayout,foundation/tools:RemoteBuilder'
    def main(self, root,**kwargs):
        layout = root.borderContainer(_class='site_body')
        self.site_header(layout.contentPane(region='top',_class='site_header'))
        self.site_footer(layout.contentPane(region='bottom',_class='site_footer'))
        self.site_left(layout.borderContainer(region='left',_class='site_left site_pane'))
        self.site_right(layout.borderContainer(region='right',_class='site_right site_pane'))
        self.site_center(layout.contentPane(region='center',_class='site_pane'))
    

    def site_center(self,pane):
        pane.div(_class='logobig')
        
    def site_footer(self,bc):
        pass
    def site_left(self,bc):
        pass
    def site_right(self,bc):
        pane = bc.contentPane(region='top',height='100px')
        fb = pane.formbuilder(cols=1,border_spacing='4px',margin_top='10px')
        fb.textbox(value='^tabs',lbl='tabs',width='5em')        
        self.buildRemote('tabContent',bc.tabContainer(region='center'),tabs='^tabs')

    def remote_tabContent(self,tc,tabs='pippo,pluto'):
        tabs=tabs.split(',')
        for t in tabs:
            p=tc.contentPane(title=t,height='100%')
            p.button(t)            
                        
