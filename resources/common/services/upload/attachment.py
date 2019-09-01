#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
import urllib2
import os
import json
from gnr.sql.gnrsql_exceptions import GnrSqlMissingTable


class Main(GnrBaseService):
    public = True
    content_type = 'text/json'
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def __call__(self,**kwargs):
        attachment = kwargs.pop('attachment', None)
        pkg = kwargs.pop('pkg', None)
        tbl = kwargs.pop('tbl', None)
        try:
            table = self.parent.db.table('%s.%s'%(pkg,tbl))
        except GnrSqlMissingTable as e:
            return self.parent.not_found_exception(debug_message='Table not found: %s.%s'%(pkg,tbl))
        attachment_table_name = table.attributes.get('atc_attachmenttable')
        try:
            attachment_table = self.parent.db.table(attachment_table_name)
        except GnrSqlMissingTable as e:
            return self.parent.not_found_exception(debug_message='Attachment table for table %s.%s not found'%(pkg,tbl))
        return json.dumps(dict(message='qui'))
        attachment_table.addAttach
        f = attachment.file
        content = f.read()
        if pkg and tbl and attachment:
            print(x)
        return json.dumps(kwargs)