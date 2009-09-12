#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
import hashlib

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.user'
    py_requires = 'public:Public,public:IncludedView,standard_tables:TableHandler,utils:SendMail'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def windowTitle(self):
        return '!!Manage users'
        
    def barTitle(self):
        return '!!Users'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def columnsBase(self):
        return """username:7,fullname:10,email:20,auth_tags:15"""
        
    def formBase(self,parentBC,disabled=False,**kwargs):
        userbc = parentBC.borderContainer(**kwargs)
        user = userbc.contentPane(_class='pbl_roundedGroup',margin='5px',region='left',width='30em')
        user.div('!!Manage user', _class='pbl_roundedGroupLabel')
        fb = user.formbuilder(cols=1, border_spacing='6px',disabled=disabled)
        fb.field('username',width='15em',lbl='!!Username')
        fb.field('firstname',width='15em',lbl='!!Firstname')
        fb.field('lastname',width='15em',lbl='!!Lastname')
        fb.textBox(value='^.md5pwd',lbl='Password', type='password')
        fb.field('status',tag='filteringSelect',values='!!conf:Confirmed,wait:Waiting',width='15em',
                validate_notnull=True,validate_notnull_error='!!Required')
        #fb.field('adm.user.password',width='15em',lbl='!!Password')
        
        fb.field('adm.user.email',width='15em',lbl='!!Email')
        ic = userbc.borderContainer(margin='5px',region='center')
        
        iv = self.includedViewBox(ic,label='!!Authorization tags',
                            storepath='.tag_bag', 
                            columns="""tagname""",datamode='bag',
                            table='adm.tag', autoWidth=True,
                            add_action=True,del_action=True)
        gridEditor = iv.gridEditor()
        gridEditor.dbCombobox(gridcell='tagname',columns='tagname',dbtable='adm.tag',hasDownArrow=True)
                                     

    def orderBase(self):
        return 'username'
        
    def _structTagsGrid(self):
        struct = self.newGridStruct('adm.tag')
        r = struct.view().rows()
        r.fieldcell('tagname',name='Tag',width='10em')
        return struct
        
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        tags = record['auth_tags']
        b = Bag()
        if tags:
            for n,tag in enumerate(tags.split(',')):
                b.setItem('r%i.tagname' %n,tag)
        record.setItem('tag_bag', b, _bag_md5 = tags)

    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        tagtable = self.db.table('adm.tag')
        if recordCluster:
            li = []
            recordCluster.pop('tag_bag_removed')
            tags = recordCluster.popNode('tag_bag')
            if tags:
                oldtags = tags.getAttr('oldValue')
                tags = tags.value
                for node in tags:
                    tag = node.value.getItem('tagname')
                    count_tag = tagtable.query(where='tagname=:t',t=tag).count()
                    if count_tag==0:
                        tagtable.insert(dict(tagname=tag))
                    li.append(tag)
                else:
                    tags = ''
                tags = ','.join(li)
                recordCluster.setItem('auth_tags', tags, oldValue=oldtags)
            if recordCluster['md5pwd']:
                recordCluster.setItem('md5pwd', hashlib.md5(recordCluster.pop('md5pwd')).hexdigest())

        
    #def onSaved_(self, data): 
    #    if data.getAttr('_newrecord'):
    #        data['link'] = self.externalUrl('adm/new_user.py', userid=data['id'])
    #        data['md5pwd'] = hashlib.md5(data['lastname']).hexdigest()
    #        self.sendMailTemplate('new_user.xml', data['email'], data)        
    
    def queryBase(self):
        return dict(column='username',op='contains',val='%',runOnStart=True)
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
