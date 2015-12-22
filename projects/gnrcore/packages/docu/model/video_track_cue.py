#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('video_track_cue', pkey='id', name_long='!!Video track cue', 
                        name_plural='!!Video track cues',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('video_id',size='22' ,group='_',
                    name_long='!!Video').relation('video.id',
                                                relation_name='cues',mode='foreignkey',onDelete='cascade')
        tbl.column('kind' ,size=':20',name_long='!!Kind',values='subtitles,chapters,captions,metadata,descriptions')
        tbl.column('start_time',dtype='R',name_long='!!Start')
        tbl.column('end_time',dtype='R',name_long='!!End')
        tbl.column('subtitles',dtype='X',name_long='!!Subtitles')
        tbl.column('options',dtype='X',name_long='!!Options')
