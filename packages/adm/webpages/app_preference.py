#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#



class GnrCustomWebPage(object):
    maintable ='adm.preference'
    py_requires="""public:Public"""
    
    def pageAuthTags(self, **kwargs):
        return 'user'
        
    def windowTitle(self):
         return '!!Preference panel'
         
    def mainLeftContent(self,parentBC,**kwargs):
        return
        
    def rootWidget(self, root, **kwargs):
        return root.tabContainer(_class='pbl_root',datapath='preferences',**kwargs)
        
    def main(self, rootTC, **kwargs):
        self.prefpane_application(rootTC,title='!!Application',datapath='._application_')
        for pkg in self.db.packages.values():
            panecb = getattr(self,'prefpane_%s' %pkg.name,None)
            
            if panecb:
                panecb(rootTC,title=pkg.name_full,datapath='.%s' %pkg.name)
        
    def prefpane_application(self,tc,**kwargs):
        appPane = tc.contentPane(**kwargs)
        fb = appPane.formbuilder(cols=2, border_spacing='4px')
        fb.textbox(value='^.prova',lbl='Prova')
        fb.textbox(value='^.foo',lbl='FOo')

        
    def onIniting(self, url_parts, request_kwargs):
        for pkgname in self.db.packages.keys():
            try:
                cl=self.site.loadResource(pkgname,'preference:AppPref')
                self.mixin(cl) 
            except:
                pass       