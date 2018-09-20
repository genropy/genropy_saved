# encoding: utf-8
from gnr.core.gnrbag import Bag,DirectoryResolver
import os
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('service', pkey='service_name', name_long='!!Service', name_plural='!!Services',caption_field='code')
        self.sysFields(tbl,id=False)
        tbl.column('service_name', size=':30', name_long='!!Code') #service_name
        tbl.column('service_type', size=':30', name_long='!!Service type')
        tbl.column('resource', name_long='!!Resource')
        tbl.column('parameters', dtype='X', name_long='!!Parameters')

    @public_method
    def getAvailableServiceTree(self):
        result = Bag()
        page = self.db.currentPage
        site = self.db.application.site
        resdirs = site.resource_loader.getResourceList(page.resourceDirs,'services')
        resdirs.reverse()
        for service_root in resdirs:
            service_types = os.listdir(service_root)
            for service_type in service_types:
                stypedir = os.path.join(service_root,service_type)
                if not os.path.isdir(stypedir):
                    continue
                for resource in os.listdir(stypedir):
                    resname,ext = os.path.splitext(resource)
                    if ext == '.py':
                        respath = os.path.join(service_root,service_type,resource)
                        result.setItem([service_type,resname],None,resource=resource,
                                        resname=resname,service_type=service_type,
                                        respath=respath,
                                        default_kw=dict(resource=resname,service_type=service_type,respath=respath))
        return result