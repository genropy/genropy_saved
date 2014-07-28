#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable = 'sys.external_token'
    py_requires = 'public:Public,standard_tables/tablehandler,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Tokens'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def tableWriteTags(self):
        return 'admin'

    def tableDeleteTags(self):
        return 'admin'

    def barTitle(self):
        return '!!External token'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('datetime', width='10em')
        r.fieldcell('expiry', width='8em')
        r.fieldcell('allowed_user', width='10em')
        r.fieldcell('connection_id', width='10em')
        r.fieldcell('max_usages', width='5em')
        r.fieldcell('allowed_host', width='10em')
        r.fieldcell('page_path', width='10em')
        r.fieldcell('method', width='10em')
        r.fieldcell('parameters', width='10em')
        return struct

    def orderBase(self):
        return 'datetime'

    def queryBase(self):
        return dict(column='datetime', op='contains', val='')

    ############################## FORM METHODS ##################################
    def formBase(self, parentBC, disabled=False, **kwargs):
        bc = parentBC.borderContainer(margin='5px', **kwargs)
        self.includedViewBox(bc, label='Tokens in use', datapath='current_tokens',
                             nodeId='current_tokens', table='sys.external_token_use', autoWidth=True,
                             struct=self.token_use_struct,
                             reloader='^form.record.id', externalChanges=True,
                             selectionPars=dict(where='external_token_id=:t_id', t_id='=form.record.id'))

    def token_use_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('datetime', width='10em')
        r.fieldcell('host', width='10em')