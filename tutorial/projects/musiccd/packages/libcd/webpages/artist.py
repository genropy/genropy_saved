#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    py_requires = 'utility_music:Common'

    def windowTitle(self):
        return '!!Artist'

    def main(self, root, **kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region='left', width='50%', background='silver',
                             splitter=True, datapath='artist')
        center = bc.contentPane(region='center', background='black')
        self.formArtist(top)
        self.gridAlbum(center)
        self.formAlbum(root)

    def formArtist(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px', datapath='.record')
        fb.dbSelect(value='^artist_id', dbtable='libcd.artist', lbl='Artist', hasDownArrow=True)
        fb.textbox(value='^.fullname', lbl='Name')
        fb.textbox(value='^.description', lbl='Description')
        fb.checkbox(value='^.is_band', label='Band')
        fb.button('Salva', fire='save_artist')
        fb.button('Aggiungi disco', action='SET album_id="*newrecord*"; FIRE #album_dlg.open')
        pane.dataRecord('.record', 'libcd.artist', pkey='^artist_id',
                        _onResult='FIRE record_loaded;', _onStart=True,
                        ignoreMissing=True, default_is_band=False)
        pane.dataSelection('selection', 'libcd.album', where='$artist_id=:a_id',
                           a_id='=artist_id', _fired='^record_loaded')
        pane.dataRpc('result', 'save', data='=.record', table='libcd.artist', _fired='^save_artist')
        pane.dataController("alert(msg)", msg="^result")


    def formAlbum(self, root):
        dlg = self.edit_record_dialog(root, title='Add Album', nodeId='album_dlg', datapath='album')
        dlg.dataController("FIRE .load; FIRE .show;", _fired="^.open")
        dlg.dataRecord('.record', 'libcd.album', pkey='=album_id', _fired='^.load',
                       default_artist_id='=artist_id', default_year=self.workdate.year)
        fb = dlg.formbuilder(cols=1, border_spacing='4px', dbtable='libcd.album',
                             datapath='.record')
        fb.field('title') # fb.textbox(value='^.title',lbl='Title')
        fb.field('year')
        fb.field('rating')
        fb.button('Salva', fire='save_album')
        dlg.dataRpc('result', 'save', data='=.record', table='libcd.album', _fired='^save_album',
                    _onResult='FIRE record_loaded')

    def gridAlbum(self, pane):
        pane.includedView(storepath='selection', table='libcd.album',
                          columns='title:15,year:3,rating:3', selectedId='album_id',
                          connect_onRowDblClick="""FIRE #album_dlg.open;""",
                          autoWidth=True)

