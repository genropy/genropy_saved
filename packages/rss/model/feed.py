# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('feed', pkey='id', name_long='!!Feed Rss')
        self.sysFields(tbl)
        tbl.column('topic', name_long='!!Topic', validate_notnull=True,
                   validate_notnull_error='!!Required', validate_case='c'
                   )
        tbl.column('title', name_long='!!Title', validate_notnull=True, validate_notnull_error='!!Required',
                   validate_case='c'
                   )
        tbl.column('description', name_long='!!Description')
        tbl.column('url', name_long='!!Address', validate_notnull=True, validate_notnull_error='!!Required')
        tbl.column('username', name_long='!!User').relation('adm.user.username', mode='foreignkey', onDelete='cascade')


    def getFeeds(self, user=None):
        b = self.query(where='$username=:user', user=user).selection().totalize(group_by=['topic', 'title'],
                                                                                keep=['id', 'url'], key='id')

        def epuratore(node):
            if node.value:
                node.attr = None

        b.walk(epuratore)
        return b   
            
            

