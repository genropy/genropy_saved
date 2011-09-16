# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('message', rowcaption='subject', pkey='id', name_long='!!Message', name_plural='!!Messages')
        self.sysFields(tbl)
        tbl.column('to',name_long='!!To')
        tbl.column('from',name_long='!!From')
        tbl.column('cc',name_long='!!Cc')
        tbl.column('bcc',name_long='!!Bcc')
        tbl.column('uid',name_long='!!UID')
        tbl.column('body',name_long='!!Body')
        tbl.column('body_plain',name_long='!!Plain Body')
        tbl.column('html','B',name_long='!!Html')
        tbl.column('subject',name_long='!!Subject')
        tbl.column('date','DH',name_long='!!Date')
        tbl.column('sent','B',name_long='!!Sent')
        tbl.column('user_id',size='22',name_long='!!User id').relation('adm.user.id', mode='foreignkey', relation_name='messages')
        tbl.column('account_id',size='22',name_long='!!Account id').relation('email.account.id', mode='foreignkey', relation_name='messages')
        
    def sendmail(self, datasource=None, to_address=None, cc_address=None, bcc_address=None, subject=None,
                              from_address=None, body=None, attachments=None, account=None,
                              html=False, charset='utf-8', **kwargs):
        # 
        def get_templated(field):
            value = datasource.getItem('_meta_.%s' % field)
            if not value:
                value = datasource.getItem(field)
            if value:
                return templateReplace(value, datasource)
        if datasource:
            get_templated = get_templated
        else:
            get_templated = lambda x:None
        to_address = to_address or get_templated('to_address')
        cc_address = cc_address or get_templated('cc_address')
        bcc_address = bcc_address or get_templated('bcc_address')
        #from_address = from_address or get_templated('from_address')
        subject = subject or get_templated('subject')
        body = body or get_templated('body')
        body = templateReplace(body, datasource) if datasource else body
        
    