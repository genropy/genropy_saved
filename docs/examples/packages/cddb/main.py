#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

from gnr.core.gnrbag import Bag

class Package(object):
        
    def config_attributes(self):
        return dict(comment='My cd catalog',name_short='CDDB',name_long='CD Catalog', name_full='CD Catalog')
    
    def config_db(self,pkg):
        author = pkg.table('author', name_short='Aut',name_long='Author')
        autid = author.stringColumn('id', len_max='22').isPkey()
        author.stringColumn('name', name_short='N.',name_long='Name', name_full='Author name', len_min='1',len_show='30', len_max='100').isIndexed()
        
        genre = pkg.table('genre', name_short='Tr.',name_long='Track')
        genreid = genre.stringColumn('id', len_max='22').isPkey()
        genre.stringColumn('name', name_short='N',name_long='Name', name_full='Genre name', len_min='1',len_show='30', len_max='100').isIndexed()

        album = pkg.table('album', name_short='CD',name_long='Album')
        albumid = album.stringColumn('id', len_max='22').isPkey()
        album.stringColumn('originalid', len_max='22').isIndexed()
        album.column('title', name_short='Tit',name_long='Title', name_full='Album title', len_min='1',len_show='30')
        album.intColumn('year', name_short='Y.',name_long='Year', name_full='Album year').isIndexed()
        album.stringColumn('genreid', len_max='22').isIndexed().relate(genreid)
        album.boolColumn('compilation')
        album.stringColumn('authorid', len_max='22').isIndexed().relate(autid)
        album.column('tracksbag')
        
        track = pkg.table('track', name_short='Tr.',name_long='Track')
        track.stringColumn('id', len_max='22').isPkey()
        track.column('title', name_short='Tit',name_long='Title', name_full='Track title', len_min='1',len_show='30')
        track.intColumn('number', name_short='N.',name_long='Number', name_full='Track number')
        track.stringColumn('albumid', len_max='22').isIndexed().relate(albumid)
        
        
    def config_menu():
        pass
        
    def importFolder(self, path):
        import os
        files = os.listdir(path)
        
        if path.endswith('/'):
            path = path[:-1]
        basegenre = os.path.basename(path)
        
        tblgenre = self.application.db.table('cddb.genre')
        tblauthor = self.application.db.table('cddb.author')
        tblalbum = self.application.db.table('cddb.album')
        
        for i, fname in enumerate(files):
            f = file(os.path.join(path,fname))
            cdtxt = f.read()
            f.close()
            
            cdtxt = unicode(cdtxt, 'latin-1', 'ignore')
            cdtxt = cdtxt.replace('\r','\n')
            info = [r.split('=',1) for r in cdtxt.split('\n') if r and not r.startswith('#') and '=' in r]
            info = dict([r for r in info if r[1]])
            
            dgenre = info.get('DGENRE', basegenre)
            dgenre = dgenre[:100]
            genreid = tblgenre.query(columns='$id', where='$name = :dgenre', dgenre=dgenre).fetch()
            if len(genreid)==0:
                genreid = self.application.db.getUuid()
                recordData = dict(name=dgenre, id=genreid)
                tblgenre.insert(recordData)
            else:
                genreid = genreid[0][0]
                
            authorname = ''
            authorid = None
            albumtitle = info.get('DTITLE','')
            if '/' in albumtitle:
                authorname, albumtitle = [t.strip() for t in albumtitle.split('/', 1)]
                
            if authorname:
                authorname = authorname[:100]
                authorid = tblauthor.query(columns='$id', where='$name = :authorname', authorname=authorname).fetch()
                if len(authorid)==0:
                    authorid = self.application.db.getUuid()
                    recordData = dict(name=authorname, id=authorid)
                    tblauthor.insert(recordData)
                else:
                    authorid = authorid[0][0]
                
            
            tracksbag = Bag()
            for k in [k for k in info.keys() if k.startswith('TTITLE')]:
                tracksbag['%s.title' % k] = info[k]
                tracksbag['%s.number' % k] = int(k[6:])
                
            recordData = dict(originalid=info.get('DISCID'), title=albumtitle, genreid=genreid, authorid=authorid,
                          year=info.get('DYEAR'), compilation=(not(authorid)), tracksbag=tracksbag.toXml())
            tblalbum.insert(recordData)
            
            if (i % 1000) == 0:
                self.application.db.commit()
                self.application.db.analyze()
                print i
                
class Table(object):
    def onInserting(self, record_data):
        if not record_data.get('id'):
            record_data['id'] = self.dbroot.getUuid()
        
        
class Table_album(object):
    def onUpdating(self, record_data):
        tracktable = self.dbroot.table('cddb.track')
        sel = tracktable.query(columns='$id', where='$albumid=:myalbumid', myalbumid=record_data['id']).fetch()
        for r in sel:
            tracktable.delete({id:r[0]})
            
    def onInserted(self, record_data):
        tracksbag = Bag(record_data['tracksbag'])
        tracktable = self.dbroot.table('cddb.track')
        for v in tracksbag.values():
            tracktable.insert(v)
            
    onUpdated = onInserted
        
        
if __name__ == '__main__':
        main()
