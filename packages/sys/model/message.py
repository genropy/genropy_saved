# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('message',  pkey='id',name_long='!!Messages',
                      name_plural='!!Messages')
        tbl.column('id',size='22',name_long='!!id')
        tbl.column('datetime','DH',name_long='!!Date and Time')
        tbl.column('expiry','DH',name_long='!!Expiry')
        tbl.column('dst_page_id',size='22',name_long='!!Destination page_id',indexed=True)
        tbl.column('dst_user',size=':32',name_long='!!Destination user',indexed=True)
        tbl.column('dst_connection_id',size='22',name_long='!!Connection Id',indexed=True)
        tbl.column('message_type',size='12',name_long='!!Message Type')
        tbl.column('body',dtype='X',name_long='!!Message body')