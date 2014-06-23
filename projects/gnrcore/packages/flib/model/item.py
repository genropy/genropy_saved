# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('item', pkey='id', name_long='!!Item', name_plural='!!Items')
        self.sysFields(tbl)
        tbl.column('title', name_long='!!Title', indexed=True)
        tbl.column('description', name_long='!!Description')
        tbl.column('url', name_long='!!Url')
        tbl.column('path', name_long='!!Path')

        tbl.column('thumb_url', name_long='!!Url')
        tbl.column('thumb_path', name_long='!!Path')

        tbl.column('file_type', name_long='!!File type')
        tbl.column('ext', name_long='!!Extension')

        tbl.column('metadata', 'X', name_long='!!Metadata')

        tbl.column('versions', 'X', name_long='!!Versions')

        tbl.column('username', name_long='!!User name', indexed=True).relation('adm.user.username')
        self.setTagColumn(tbl, group='zz')

    def zoomUrl(self):
        return 'flib/items' 

    def getUploadPath(self):
        return 'site:uploaded_files'