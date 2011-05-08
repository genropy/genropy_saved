# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        """user"""
        tbl = pkg.table('user', pkey='id', name_long='!!User', rowcaption='username:%s')
        self.sysFields(tbl, md5=True)
        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('username', size=':32', name_long='!!Username', unique='y', _sendback=True,
                   indexed='y', validate_notnull=True, validate_notnull_error='!!Mandatory field')
        tbl.column('firstname', size=':32', name_long='!!First name',
                   validate_notnull=True, validate_case='c', validate_notnull_error='!!Mandatory field')
        tbl.column('lastname', size=':32', name_long='!!Last name',
                   validate_notnull=True, validate_case='c', validate_notnull_error='!!Mandatory field')
        tbl.column('auth_tags', name_long='!!Authorization Tags')
        tbl.column('md5pwd', name_long='!!PasswordMD5', size=':65')
        tbl.formulaColumn('fullname', "firstname||' '||lastname", name_long=u'!!Name')

    def createPassword(self):
        password = getUuid()[0:6]
        return password

    def trigger_onUpdating(self, record, **kwargs):
        self.passwordTrigger(record)

    def trigger_onInserting(self, record, **kwargs):
        self.passwordTrigger(record)

    def passwordTrigger(self, record):
        if 'md5pwd' in record:
            password = record['md5pwd']
            if len(password) < 32:
                record['md5pwd'] = self.db.application.changePassword(None, None, password, userid=record['username'])

    def loadRecord(self, username, for_update=False):
        try:
            record = self.record(username=username, for_update=for_update).output('bag')
        except:
            record = Bag()
        return record