#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    def rootPage(self,*args, **kwargs):
        self.response.content_type = 'application/xml'
        request_method = self.request.method
        self.db.table('task.task').runScheduled(self)