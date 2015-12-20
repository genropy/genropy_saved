#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('video', pkey='id', name_long='!!Video', 
                        name_plural='!!Video',caption_field='title')
        self.sysFields(tbl)
        tbl.column('url',name_long='!!Url')
        tbl.column('player_url',name_long='!!Player Url')
        tbl.column('hosted_by' ,size=':100',name_long='!!Hosted by')
        tbl.column('external_id' ,size=':20',name_long='!!External ID')#inside sourcebag is id
        tbl.column('title',name_long='!!Title')
        tbl.column('description' ,name_long='!!Description')
        tbl.column('thumbnail_small','P',name_long='!!thumbnail_small')
        tbl.column('thumbnail_medium','P',name_long='!!thumbnail_medium')
        tbl.column('thumbnail_large','P',name_long='!!thumbnail_large')
        tbl.column('duration','L',name_long='!!Duration')
        tbl.column('video_width','L',name_long='!!Width') # inside sourcebag is width
        tbl.column('video_height','L',name_long='!!Height') # inside sourcebag is height
        tbl.column('video_tags',name_long='!!Video tags')# inside sourcebag is tags


    @public_method
    def updateScreencasts(self):
        source = Bag('http://vimeo.com/api/v2/genropy/videos.xml')
        videos = source['#0']
        if not videos:
            return
        for v in videos.values():
            with self.recordToUpdate(vimeo_id=v['id'],insertMissing=True) as r:
                r.update(dict(vimeo_id=v['id'],title=v['title'],description=v['description'],
                                        url=v['url'],
                                        player_url='//player.vimeo.com/video/%s' %v['id'],
                                        thumbnail_small=v['thumbnail_small'],
                                        thumbnail_medium=v['thumbnail_medium'],
                                        thumbnail_large=v['thumbnail_large'],
                                         duration=int(v['duration']),
                                         video_width=int(v['width']),
                                         video_height=int(v['height']),
                                        video_tags=v['tags']))
        self.db.commit()