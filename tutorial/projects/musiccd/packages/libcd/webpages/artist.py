#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def windowTitle(self):
         return '!!Artist'

    def main(self, root, **kwargs):
        self.formbox(root)

    
    def formbox(self,root):
        box = root.div(height='400px',width='400px',datapath='artista',background='silver',margin='20px')
        fb = box.formbuilder(cols=1,border_spacing='4px')
        fb.textbox(value='^.fullname',lbl='Name')
        fb.textbox(value='^.description',lbl='Description')
        fb.checkbox(value='^.is_band',label='Band')
        fb.button('Salva',fire='save')
        box.dataRpc('result','saveArtist',data='=artista',_fired='^save')
        box.dataController("alert(msg)",msg="^result")

    def rpc_saveArtist(self,data):
        tblartisti = self.db.table('libcd.artist')
        tblartisti.insert(data)
        self.db.commit()
        return 'ok'
        
