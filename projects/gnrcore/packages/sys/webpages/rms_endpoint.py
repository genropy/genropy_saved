# -*- coding: utf-8 -*-
            
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from datetime import datetime
import re

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:NetBagRpc'


    @public_method #(tags='ext')
    def netbag_register_pod(self,code=None,customer_code=None,**kwargs):
        tblpod = self.db.table('deploy.pod')
        podrecord = tblpod.record(code=code,customer_code=customer_code,ignoreMissing=True).output('dict')
        oldrecord = dict(podrecord)
        podrecord.update(kwargs)
        if not podrecord:
            podrecord['code'] = code
            podrecord['customer_code'] = customer_code
            tblpod.insert(podrecord)
        else:
            tblpod.update(podrecord,oldrecord)
        self.db.commit()
        return Bag(podrecord)