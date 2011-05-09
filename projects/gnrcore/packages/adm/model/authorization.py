# encoding: utf-8
import random
import string
from datetime import datetime, date

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('authorization', pkey='code', name_long='!!Authorization',
                        name_plural='!!Authorizations')
        self.sysFields(tbl, id=False)
        tbl.column('code', size=':8', validate_case='U', name_long='!!Code')
        tbl.column('user_id', size='22', name_long='!!Event').relation('user.id', mode='foreignkey')
        tbl.column('use_ts', 'DH', name_long='!!Used datetime')
        tbl.column('used_by', size=':32', name_long='!!Used by')
        tbl.column('note', name_long='!!Note')
        tbl.column('remaining_usages', 'L', name_long='!!Remaining usages', default=1)
        tbl.column('expiry_date', 'D', name_long='!!Expire Date')

    def generate_code(self):
        code = ''.join(random.Random().sample(string.letters + string.digits, 8)).upper()
        for c in (('0', 'M'), ('1', 'N'), ('O', 'X'), ('L', 'Y'), ('I', 'Z')):
            code = code.replace(c[0], c[1])
        return code

    def use_auth(self, code, username):
        record = self.record(pkey=code, for_update=True).output('bag')
        record['use_ts'] = datetime.now()
        record['used_by'] = username
        record['remaining_usages'] = record['remaining_usages'] - 1
        self.update(record)

    def check_auth(self, code):
        exists = self.query(where='$code=:code', code=code).fetch()
        if not exists:
            return False
        coupon = exists[0]
        if coupon['expiry_date'] and coupon['expiry_date'] < date.today():
            return False
        remaining_usages = coupon['remaining_usages']
        if remaining_usages <= 0:
            return False
        return True
