# encoding: utf-8
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,BagResolver

class MailboxResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'parent_id': None,
                   'account_id':None,
                   'user_id':None,
                   '_page':None}
    classArgs = ['parent_id']

    def resolverSerialize(self):
        attr = super(MailboxResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    def load(self):
        page = self._page
        mailbox_tblobj = page.db.table('email.mailbox')
        where = '$parent_id IS NULL'
        if self.parent_id:
            where='$parent_id=:p_id' #sottopratiche
        elif self.account_id:
            where = '$account_id =:a_id AND $parent_id IS NULL' 
        elif self.user_id:
            where='user_id=:u_id AND $parent_id IS NULL' 
        else:
            where = '$parent_id IS NULL AND $user_id IS NULL AND $account_id IS NULL'

        q = mailbox_tblobj.query(where=where,p_id=self.parent_id,columns='*,$child_count',
                                        a_id=self.account_id,u_id=self.user_id,order_by='$system_code,$name')
        result = Bag()
        mailboxes = q.fetch()
        for mb in mailboxes:
            record = dict(mb)
            caption = mb['name']
            pkey = record['id']
            result.setItem(pkey,MailboxResolver(_page=page,parent_id=pkey),
                            caption=caption,
                            child_count=record['child_count'],pkey=pkey,
                            account_id=record['account_id'],system_code=record['system_code'],
                            parent_id=self.parent_id)

        return result

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('mailbox', rowcaption='$name',
                        caption_field='name', 
                        pkey='id', name_long='!!Mailbox', 
                        name_plural='!!Mailboxes')
        self.sysFields(tbl,hierarchical=True) #,hierarchical='name'
        tbl.column('name',name_long='!!Name')
        tbl.column('account_id',size='22',group='_',name_long='Account id').relation('account.id', mode='foreignkey', 
                                                                                    onDelete='raise',relation_name='mailboxes')
        tbl.column('user_id',size='22',group='_',name_long='User id').relation('adm.user.id', mode='foreignkey', onDelete='cascade', 
                    relation_name='mailboxes')
        tbl.column('system_code',name_long='!!System code')
                    
    def createMbox(self,name,account_id=None,user_id=None,order=None):
        system_code = '0%i' %order if order else None
        self.insert(dict(name=name,account_id=account_id,user_id=user_id,system_code=system_code))
    
    @public_method
    def getMailboxResolver(self, user_id=None,account_id=None,parent_id=None):
        page = self.db.application.site.currentPage
        return MailboxResolver(_page=page,parent_id=parent_id,user_id=user_id,account_id=account_id)
    
