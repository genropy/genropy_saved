# -*- coding: utf-8 -*-

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:NetBagRpc'


    @public_method(tags='EXT')
    def netbag_write(self,tbl=None,data=None,description=None,send_ts=None,**kwargs):
        result = self.db.table('lgcy.transaction').storeTransaction(tbl=tbl,data=data,description=description,send_ts=send_ts)
        if result.get('transaction_id'):
            self.db.commit()
        return result
