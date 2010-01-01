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
        bc = root.borderContainer()
        top = bc.contentPane(region='left',width='50%',background='silver',
                                splitter=True,datapath='record_artist')
        center = bc.contentPane(region='center',background='black')
        self.formArtist(top)
        self.gridAlbum(center)
        self.formAlbum(root)

    
    def formArtist(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.dbSelect(value='^artist_id',dbtable='libcd.artist',lbl='Artist',hasDownArrow=True)
        fb.textbox(value='^.fullname',lbl='Name')
        fb.textbox(value='^.description',lbl='Description')
        fb.checkbox(value='^.is_band',label='Band')
        fb.button('Salva',fire='save_artist')
        fb.button('Aggiungi disco',fire='add_album')
        pane.dataController("genro.wdgById('album_dlg').show();",_fired="^add_album",
                            _if='artist_id',artist_id='=artist_id')
        
        
        pane.dataRecord('record_artist','libcd.artist',pkey='^artist_id',_onResult='FIRE record_loaded;')
        pane.dataSelection('selection','libcd.album',where='$artist_id=:a_id',
                           a_id='=artist_id',_fired='^record_loaded')
        pane.dataRpc('result','saveArtist',data='=record_artist',_fired='^save_artist')
        pane.dataController("alert(msg)",msg="^result")
        

    def formAlbum(self,root):
        dlg = root.dialog(title='Add Album',height='400px',width='400px',nodeId='album_dlg',datapath='record_album')
        fb = dlg.formbuilder(cols=1,border_spacing='4px',dbtable='libcd.album')
        fb.dataFormula("^.artist_id", "artist_id",artist_id="^artist_id")
        fb.field('title') # fb.textbox(value='^.title',lbl='Title')
        fb.field('year') 
        fb.field('rating')
        fb.button('Salva',fire='save_album')
        dlg.dataRpc('result','saveAlbum',data='=record_album',_fired='^save_album',
                    _onResult='FIRE record_loaded')
        
    def gridAlbum(self,pane):
        pane.includedView(storepath='selection',table='libcd.album',columns='title:15,year:3,rating:3',
                        autoWidth=True)

    def rpc_saveArtist(self,data):
        tblartisti = self.db.table('libcd.artist')
        tblartisti.insert(data)
        self.db.commit()
        return 'ok'
        
    def rpc_saveAlbum(self,data):
        tblalbum = self.db.table('libcd.album')
        tblalbum.insert(data)
        self.db.commit()
        return 'ok'
