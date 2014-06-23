#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable = 'sys.message'
    py_requires = 'public:Public,standard_tables/tablehandler,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Message'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def tableWriteTags(self):
        return 'admin'

    def tableDeleteTags(self):
        return 'admin'

    def barTitle(self):
        return '!!Message'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('datetime', width='7em')
        r.fieldcell('expiry', width='7em')
        r.fieldcell('src_user', width='15em')
        r.fieldcell('dst_user', width='10em')
        r.fieldcell('dst_connection_id', width='15em')
        r.fieldcell('src_page_id', width='15em')
        r.fieldcell('src_user', width='15em')
        r.fieldcell('src_connection_id', width='15em')
        r.fieldcell('message_type', width='15em')

        return struct

    def orderBase(self):
        return 'dst_page_id'

    def conditionBase(self):
        pass

    def queryBase(self):
        return dict(column='dst_page_id', op='contains', val='')

    ############################## FORM METHODS ##################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        pass