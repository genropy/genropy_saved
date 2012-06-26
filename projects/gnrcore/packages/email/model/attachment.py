# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('attachment', rowcaption='title', pkey='id', name_long='!!Attachment', name_plural='!!Attachments')
        self.sysFields(tbl)
        #tbl.column('title',name_long='!!Title')
        tbl.column('filename',name_long='!!Filename')
        tbl.column('mime_type',name_long='!!Mime Type')
        tbl.column('size',name_long='!!Size')
        tbl.column('path',name_long='!!path')
        tbl.column('message_id',size='22',name_long='!!Message id').relation('email.message.id', mode='foreignkey',deferred=True, 
                                                                             onDelete_sql='cascade',relation_name='attachments')
