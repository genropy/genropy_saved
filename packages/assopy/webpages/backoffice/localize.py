#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """
import os

from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip

class GnrCustomWebPage(object):

    def pageAuthTags(self, method=None, **kwargs):
        return 'traduttore,superadmin'
        
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.dataRpc('response_save', 'saveLoc', data='=locbag', _POST=True,_onResult='alert("saved")',fired='^dosave')
        locbag=Bag(os.path.join(self.application.packages[self.packageId].packageFolder,'localization.xml'))
        root.data('locbag',locbag)
        lc=root.layoutContainer(height='100%')
        top=lc.contentPane(layoutAlign='top',height='2.8em',border='1px solid silver',margin='3px')
        #top.filteringselect(value='lang',values='it:Italian,en:English,de:Deutsch,fr:French',margin='5px')
        top.button('Save',fire='dosave')
        client=lc.contentPane(layoutAlign='client',border='1px solid silver',margin='3px')
        tc=client.tabContainer(height='100%')
        for lang in ['it','en']:
            pane=tc.contentPane(title=lang)
            
            #fb=pane.formbuilder(cols=1,border_spacing='4px')
            tbl = pane.table(border_collapse='collapse',_class='localizetool').tbody()
            for k,key,loc in locbag.digest('#k,#a._key,#a.%s'%lang):
                r = tbl.tr()
                r.td(key, width='20em' ,_class='localizetool_lbl')
                r.td(_class='localizetool_fld').textbox(width='60em', value='^locbag.%s?%s'%(k,lang))
                
        
    def rpc_saveLoc(self, data, **kwargs):
        old_umask = os.umask(2)

        locbagpath=os.path.join(self.application.packages[self.packageId].packageFolder,'localization.xml')
        data.toXml(locbagpath)
        
        os.umask(old_umask)
        return 'saved' 
        

