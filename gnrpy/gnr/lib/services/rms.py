
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrmail : gnr mail controller
# Copyright (c) : 2004 - 2007 Softwell sas - Milano
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

import urlparse
from gnr.app.gnrconfig import gnrConfigPath

from gnr.core.gnrbag import Bag,NetBag
from gnr.app.gnrapp import GnrApp
from gnr.app.gnrdeploy import PathResolver
from gnr.app.gnrconfig import getRmsOptions,setRmsOptions

class RMS(object):
    def __init__(self):
        self.options = getRmsOptions()
    
    def __getattr__(self,attr):
        return self.options.get(attr)

    def registerPod(self):
        if self['url'] and not self['token']:
            result =  NetBag(self['url'],'register_pod',code=self['code'],
                                customer_code=self['customer_code'])()
            if result and result.get('client_token'):
                setRmsOptions(token=result['client_token'])
    

    @property
    def authenticatedUrl(self):
        sp = urlparse.urlsplit(self['url'])
        return '%s://%s:%s@%s%s' %(sp.scheme,'gnrtoken',self['token'],sp.netloc,sp.path)

    def buildRmsService(self,instancename,rmskw,rmspath):
        app = GnrApp(instancename,enabled_packages=['gnrcore:sys','gnrcore:adm'])
        db = app.db
        usertbl = db.table('adm.user')
        if not usertbl.checkDuplicate(username='DEPLOY_SERVER'):
            user_rec = usertbl.newrecord(username='DEPLOY_SERVER',md5pwd=usertbl.newPkeyValue())
            usertbl.insert(user_rec)
            htagtbl = db.table('adm.htag')
            tag_id = htagtbl.sysRecord('_SYSTEM_')['id']
            db.table('adm.user_tag').insert({'tag_id':tag_id,'user_id':user_rec['id']})
        service_tbl = db.table('sys.service')
        if not service_tbl.checkDuplicate(name=instancename,service_type='rms'):
            domain = rmskw.get('domain')
            deploy_token = self.db.table('sys.external_token').create_token(exec_user=user_rec['username'])
            servicetbl = service_tbl.addService(service_type='rms',name=instancename,
                                                            token=deploy_token,
                                                            domain=domain)
        rmsbag = Bag()
        rmsbag.setItem('rms',None,token=deploy_token,domain=domain,instance_name=instancename)
        rmsbag.toXml(rmspath)
        db.commit()
        return rmsbag


    def registerInstance(self,name):
        p = PathResolver()
        siteconfig = p.get_siteconfig(name)
        rmspath = os.path.join(gnrConfigPath(),'rms','{name}.xml'.format(name=name))
        siteattr = siteconfig.getAttr('rms')
        if not siteattr.get('domain'):
            return
        if not os.path.exists(rmspath):
            rmsbag = self.buildRmsService(name,siteattr,rmspath)
        else:
            rmsbag = Bag(rmspath)
        rms_instance_attr = rmsbag.getAttr('rms')
        result =  NetBag(self.authenticatedUrl,'register_instance',code=name,
                            domain=rms_instance_attr.get('domain'),
                            pod_token=self['token'],
                            instance_token= rms_instance_attr['token'],
                            customer_code=rms_instance_attr.get('customer_code') or self['customer_code'])()
        