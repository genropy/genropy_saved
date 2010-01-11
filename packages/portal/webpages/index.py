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
        layout.dataRemote('pippo','pippo')
        self.site_header(layout.contentPane(region='top',_class='site_header'))
        self.site_footer(layout.contentPane(region='bottom',_class='site_footer',height='15px'))
        left=self.site_left(layout.borderContainer(region='left',width='25%'))

        right=self.site_right(layout.borderContainer(region='right',width='25%'))
        
        self.site_center(layout.borderContainer(region='center'))
    
    def rpc_pippo(self):
        return Bag(dict(pippo='pluto',paperino=12))

    def site_center(self,bc):
        bc = bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        tc = bc.tabContainer(region='center',margin='10px')
        self.page_0(tc.contentPane(title='Page 0',nodeId='tab0'))
        self.ajaxContent('page_1',tc.contentPane(title='Page 1',nodeId='tab1'))
        #self.lazyContent('page_2',tc.contentPane(title='Page 2',onShow='this.updateRemoteContent(false);',
        #                    nodeId='tab2'))
        self.lazyContent('page_2',tc.contentPane(title='Page 2'))
        self.page_3(tc.contentPane(title='Page 3'))

    def page_0(self,pane):
        """docstring for page_0"""
        pane.div('page 0')
        
    def remote_page_1(self,pane):
        """docstring for page_1"""
        pane.div('page 1')
        
    def remote_page_2(self,pane):
        """docstring for page_2"""
        pane.div('page 2')


    def page_3(self,pane):
        """docstring for page_3"""
        pane.div('page 3')
        
    def site_footer(self,bc):
        pass
        
    def site_left(self,bc):
        
        bc.borderContainer(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        
    def site_right(self,bc):
        pane=bc.contentPane(region='top',_class='site_pane',margin=self.margin_default,height='60px')
        bc.contentPane(region='bottom',_class='site_pane',margin=self.margin_default,height='60px')
        center=bc.borderContainer(region='center',_class='site_pane',margin=self.margin_default)
        fb = pane.formbuilder(cols=1,border_spacing='4px',margin=self.margin_default)
        fb.textbox(value='^tabs',lbl='Tabs',width='16em')        
        self.ajaxContent('tabContent',center.tabContainer(region='center',margin='8px'),tabs='^tabs')

    def remote_tabContent(self,tc,tabs='pippo,pluto'):
        tabs=tabs.split(',')
        for t in tabs:
            p=tc.contentPane(title=t,height='100%')
            p.button(t)            
                        
