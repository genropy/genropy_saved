#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable = 'hosting.instance'
    py_requires = 'public:Public,public:IncludedView,standard_tables:TableHandler'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def windowTitle(self):
        return '!!Manage instances'

    def barTitle(self):
        return '!!Instance'

    def tableWriteTags(self):
        return 'admin'

    def tableDeleteTags(self):
        return 'admin'

    def columnsBase(self):
        return """code:7,
                  description:50,
                  path:50"""

    def formBase(self, parentBC, disabled=False, **kwargs):
        instancecp = parentBC.contentPane(_class='pbl_roundedGroup', margin='5px', **kwargs)
        instancecp.div('!!Manage instances', _class='pbl_roundedGroupLabel')
        fb = instancecp.formbuilder(cols=1, border_spacing='6px', disabled=disabled)
        fb.field('description', width='15em', lbl='!!Instance Name')
        fb.field('path', width='15em', lbl='!!Path')
        fb.field('site_path', width='15em', lbl='!!Site path')
        fb.dataFormula('.$creationDisabled', 'instance_exists && site_exists', site_exists='^.$site_exists',
                       instance_exists='^.$instance_exists')
        fb.button('Create', disabled='=.$creationDisabled', action='FIRE .$create;')
        instancecp.dataRpc('.$creation_result', 'createInst', instance_name='=.name',
                           instance_exists='=.$instance_exists', site_exists='=.$site_exists', _fired='^.$create',
                           _onResult='FIRE .$created')
        instancecp.dataController("""
                if (site_path){
                SET .site_path=site_path;
                SET .$site_exists=true;
                }
                if (instance_path){
                SET .path=instance_path;
                SET .$instance_exists=true;
                }
                """, site_path='=.$creation_result.site_path', instance_path='=.$creation_result.instance_path',
                                  _fired='^.$created')

    def orderBase(self):
        return 'username'

    def _structTagsGrid(self):
        struct = self.newGridStruct('adm.tag')
        r = struct.view().rows()
        r.fieldcell('tagname', name='Tag', width='10em')
        return struct

    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        instance_exists = False
        site_exists = False
        if record['path']:
            instance_exists = os.path.isfile(os.path.join(record['path'], 'instanceconfig.xml'))
        if record['site_path']:
            site_exists = os.path.isfile(os.path.join(record['site_path'], 'siteconfig.xml'))
        print site_exists
        print instance_exists
        record.setItem('$instance_exists', instance_exists)
        record.setItem('$site_exists', site_exists)

    def rpc_pippo(self, name=None, instance_exists=None, site_exists=None):
        print 'pippo'


    def rpc_createInst(self, instance_name=None, instance_exists=None, site_exists=None):
        print instance_exists
        print site_exists
        result = Bag()
        instancetbl = self.db.table(self.maintable)
        if not instance_exists:
            result['instance_path'] = instancetbl.create_instance(instance_name, self.site.instance_path,
                                                                  self.site.gnrapp.config)
        if not site_exists:
            result['site_path'] = instancetbl.create_site(instance_name, self.site.site_path, self.site.config)
        return result


    def queryBase(self):
        return dict(column='name', op='contains', val='%', runOnStart=True)
        
