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
        self.margin_default='7px'
        layout = root.borderContainer(_class='site_body')
        self.site_header(layout.contentPane(region='top',_class='site_header'))
        self.site_footer(layout.contentPane(region='bottom',_class='site_footer',height='15px'))
        left=self.site_left(layout.borderContainer(region='left',width='25%'))

        right=self.site_right(layout.borderContainer(region='right',width='25%'))
        
        self.site_center(layout.borderContainer(region='center'))
    

    def site_center(self,bc):
        bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)

        
    def site_footer(self,bc):
        pass
    def site_left(self,bc):
        
        bc.borderContainer(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        
    def site_right(self,bc):
        pane=bc.contentPane(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.contentPane(region='bottom',_class='site_pane',margin=self.margin_default,height='60px')
        center=bc.contentPane(region='center',_class='site_pane',margin=self.margin_default)
        fb = pane.formbuilder(cols=1,border_spacing='4px',margin=self.margin_default)
        fb.textbox(value='^tabs',lbl='Tabs',width='16em')        
        self.buildRemote('tabContent',center.tabContainer(region='center',margin='8px'),tabs='^tabs')

    def remote_tabContent(self,tc,tabs='pippo,pluto'):
        tabs=tabs.split(',')
        for t in tabs:
            p=tc.contentPane(title=t,height='100%')
            p.button(t)            
                        
