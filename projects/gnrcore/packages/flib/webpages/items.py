#!/usr/bin/env python
# encoding: utf-8

# item_category.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

class GnrCustomWebPage(object):
    maintable = 'flib.item'
    py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!File Items'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'user'

    def barTitle(self):
        return '!!File Items'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts', name='!!Inserted on', width='8em')
        r.fieldcell('title', name='!!Title', width='8em')
        r.fieldcell('description', name='!!Description', width='18em')
        r.fieldcell('url', name='Url', width='10em')
        return struct

    def formBase(self, parentBC, disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        base = bc.contentPane(region='center', _class='pbl_roundedGroup', margin='5px')
        base.div('!!File Items', _class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em', border_spacing='7px', margin_top='1em')
        fb.field('title', width='10')
        fb.field('description', width='30em')
        fb.field('url', width='30em')


    def orderBase(self):
        return '__ins_ts'

    def conditionBase(self):
        pass

    def queryBase(self):
        return dict(column='title', op='contains', val='%')