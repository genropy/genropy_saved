#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Examples & Tutorials """

#from gnr.core.gnrbag import Bag
from gnr.core.gnrbag import Bag, DirectoryResolver
import os



class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.dataRemote('tree','diskDirectory')
        root.data('resetUrl', self.package.attributes.get('startpage'))
        
        root.dataRpc('currentUrl','currentUrl' ,relpath='^selected.relpath')
        root.dataRpc('lesson.response','setInd',frameSrc='^sendPage')
        layout = self.rootLayoutContainer(root,padding='2px',height='100%')
        layout = layout.layoutContainer(height='100%',_class='demoleft_container')
        top = layout.contentPane(layoutAlign='top',background_color='gray')
        top.button('Invia',action='FIRE sendPage = genro.myIframe.contentDocument.location.href')
        top.button('Reset',action='SET currentUrl = GET resetUrl; FIRE sendPage = GET resetUrl')
        
        client = layout.contentPane(layoutAlign='client',padding='2px').splitContainer(height='100%')
        left = client.contentPane(_class='demoleft', sizeShare=15)
        tree = left.tree(storepath='tree',isTree=False,inspect='shift',selected_rel_path='selected.relpath')
        right = client.contentPane(sizeShare=85, _class='demoright')
        right.iframe(gnrId='myIframe',border='0px', width='100%', height='100%',src='^currentUrl')
        

# ------------  Rpc custom Calls ------------  
    def rpc_currentUrl(self,relpath):
        siteroot=self.package.attributes.get('siteroot')
        return self.request.construct_url(siteroot+relpath)
        
    def rpc_diskDirectory(self):
        path=self.package.attributes.get('sitepath')
        return DirectoryResolver(path)
    
    def rpc_setInd(self,frameSrc ='',**kwargs):
        oframeSrc = frameSrc
        testurl = self.request.construct_url('')
        if frameSrc.startswith(testurl):
            frameSrc = frameSrc.replace(testurl,'')
        filepath=os.path.join(self.siteFolder, 'data', 'common','selectedURL.txt')
        f = self.createFileInData(filepath)
        f.write(frameSrc)
        f.close()
        return 'ok'

