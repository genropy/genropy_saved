#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable = 'sys.locked_record'
    py_requires = 'public:Public,standard_tables/tablehandler,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Locked records'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def tableWriteTags(self):
        return 'admin'

    def tableDeleteTags(self):
        return 'admin'

    def barTitle(self):
        return '!!Locked records'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('id')
        r.fieldcell('lock_ts')
        r.fieldcell('lock_table')
        r.fieldcell('lock_pkey')
        r.fieldcell('page_id')
        r.fieldcell('connection_id')
        r.fieldcell('username')

        return struct

    def orderBase(self):
        return 'lock_ts'

    def conditionBase(self):
        pass

    def queryBase(self):
        return dict(column='lock_table', op='contains', val='')

    ############################## FORM METHODS ##################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        pass