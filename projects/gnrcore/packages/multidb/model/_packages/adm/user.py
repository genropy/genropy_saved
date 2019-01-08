# encoding: utf-8
from gnr.core.gnrdecorator import public_method


class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('user')
        tbl.column('dbstore', name_long='!!Dbstore',plugToForm=True)        

    @public_method
    def newStoreUser(self,dbstore=None,mail_message=None,mail_subject=None,mail_async=None,**userdata):
        try:
            record = self.newrecord(**userdata)
            record['status'] = 'new'
            record['dbstore'] = dbstore
            site = self.db.application.site
            record['avatar_rootpage'] = '%s/%s' %(site.homepage,dbstore)
            self.db.table('adm.user').insert(record)
            site = self.db.application.site
            email = record['email']
            if email and mail_message:
                record['link'] = site.currentPage.externalUrlToken(record['avatar_rootpage'], userid=record['id'],max_usages=1)
                record['greetings'] = record['firstname'] or record['lastname']
                body = '%s <br/> $link' %mail_message 
                self.getService('mail').sendmail_template(record,to_address=email,
                                    body=body, subject=mail_subject or 'Confirm user',
                                    async=mail_async or False,html=True)
            self.db.commit()
        except Exception,e:
            return dict(error=str(e))

