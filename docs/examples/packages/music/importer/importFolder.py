from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql import GnrSqlDb
import os

class CdImporter(object):
    def __init__(self, importPath):
        self.musicdb = GnrSqlDb(implementation='postgres', dbname='music', host='applox.softwell.it', 
                           user='postgres', password='postgnr')
        self.musicdb.loadStructure()
        self.musicdb.saveStructure('config_db.xml')
        self.musicdb.startup()
        
        self.importPath = importPath
        #self.srcbag = Bag(importPath)
        
        self.authors = Bag()
        self.authids = Bag()
        self.genres = Bag()
        
    def do(self):
        cdlist=os.listdir(self.importPath)
        i=0
        k=0
        for cd in cdlist:
            try:
                self.importCd(cd)
            except:
                print 'error....%s' % cd
            i=i+1
            if i>1000:
                i=0
                k=k+1
                print k
                self.musicdb.commit()
                self.musicdb.analyze()
        
    def readCdFile(self, fname):
        f = file(fname)
        cdtxt = f.read()
        f.close()
        cdtxt = unicode(cdtxt, 'latin-1', 'ignore')
        cdtxt = cdtxt.replace('\r','\n')
        info = [r.split('=',1) for r in cdtxt.split('\n') if r and not r.startswith('#') and '=' in r]
        return dict([r for r in info if r[1]])
        
    def importCd(self, name):
        info = self.readCdFile(os.path.join(self.importPath,name))
        album_id = info.get('DISCID')
        if len(album_id)>10:
            return
        authorname = '-NoAuthor-'
        albumtitle = info.get('DTITLE','')
        if '/' in albumtitle:
            authorname, albumtitle = [t.strip() for t in albumtitle.split('/', 1)]
        if not authorname:
            return
        authorid = self.getAuthorId(authorname)
        
        genre_code = self.getGenreCode(info.get('DGENRE','undefined'))
        
        albumRecord = self.musicdb.table('public.album').record(readOnly=False, cacheTime=-1)
        albumRecord = albumRecord()
        albumRecord.save(id = album_id, 
                         title = albumtitle, 
                         genre_code = genre_code, 
                         author_id = authorid,
                         year = info.get('DYEAR')
                     )
        
        for k in [k for k in info.keys() if k.startswith('TTITLE')]:
            trackRecord = self.musicdb.table('public.track').record(readOnly=False, cacheTime=-1)
            trackRecord = trackRecord()
            number=int(k[6:])
            trackRecord.save(album_id=album_id, title=info[k], number=number, id='%s_%02i' % (album_id, number))
            
    def getGenreCode(self, genredsc):
        genrecode = genredsc[:20].upper().replace('.','').replace(' ','_')
        if not genrecode in self.genres:
            self.genres[genrecode] = self.musicdb.table('public.genre').record(code=genrecode, readOnly=False, cacheTime=-1)
        genreRecord = self.genres[genrecode]
        if genreRecord.isNew:
            genreRecord.save(code = genrecode, description=genredsc[:60].capitalize())
        return genreRecord['code']
        
    def getAuthorId(self, authorname):
        authorcode = authorname.replace('.','')
        if not authorcode in self.authors:
            self.authors[authorcode] = self.musicdb.table('public.author').record(name=authorname, readOnly=False, cacheTime=-1)
        authorRecord = self.authors[authorcode]
        if authorRecord.isNew:
            authorRecord.save(id=self.newAuthorId(authorname), name=authorname)
        return authorRecord['id']
    
    def newAuthorId(self, authorname):
        idprefix = authorname[:3].ljust(3, '_')
        if not idprefix in self.authids:
            self.authids[idprefix] = self.musicdb.count('public.author', where='name ILIKE :authstart', 
                                           authstart = authorname[:3]+'%', readOnly=False, cacheTime=-1)
        else:
            self.authids[idprefix] = self.authids[idprefix] + 1
        return '%s_%03i' % (idprefix, self.authids[idprefix])
        
 
if __name__=='__main__':
    import sys
    imp = CdImporter(sys.argv[1])
    imp.do()
    