# encoding: utf-8
import os

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
                                                                             onDelete_sql='cascade',
                                                                             onDelete='cascade',
                                                                             relation_name='attachments')


    def getAttachmentNode(self,date=None,filename=None, message_id = None, account_id=None,atc_counter=None):
        year = str(date.year)
        month = '%02i' %date.month
        filename = filename or 'attachment_%s' %atc_counter
        storage_identifier = self.db.application.getPreference('attachment_storage',pkg='email')
        site = self.db.application.site
        if not storage_identifier:
            storage = 'site'
        else:
            storage = storage.split('_',1)[1]
        storage = '%s:mail' %storage
        snode = site.storageNode(storage,account_id, year,month,message_id)
        counter = 0
        fname,ext = os.path.splitext(filename)

        #avoiding dup
        while snode.service.isfile(filename):
            filename = '%s_%i%s'%(fname,counter,ext)
            counter += 1
        return site.storageNode(storage,account_id, year,month,message_id,filename)