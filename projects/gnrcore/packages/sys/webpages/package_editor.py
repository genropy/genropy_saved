#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Migration
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrApp
from gnr.app.gnrdeploy import ProjectMaker, InstanceMaker, SiteMaker,PackageMaker, PathResolver,ThPackageResourceMaker

class GnrCustomWebPage(object):
    py_requires="""public:Public,
                   gnrcomponents/framegrid:FrameGrid,
                   gnrcomponents/formhandler:FormHandler,
                   extdb_explorer:ExtDbExplorer,
                   table_module_editor:TableModuleEditor"""

    def windowTitle(self):
        return '!!Package editor'

    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Package editor',datapath='main',design='sidebar')
        self.extDbConnectionDialog(bc,datapath='main.external_db')
        self.packageForm(bc.frameForm(frameCode='packageMaker',region='center',datapath='.data',store='memory',store_startKey='*newrecord*'))

    @public_method
    def getProjectPath(self,value=None,**kwargs):
        p = PathResolver()
        data = Bag()
        try:
            path = p.project_name_to_path(value)
            instances_path = os.path.join(path,'instances')
            packages_path = os.path.join(path,'packages')
            instances = [l for l in os.listdir(instances_path) if os.path.isfile(os.path.join(instances_path,l,'instanceconfig.xml'))]
            packages = [l for l in os.listdir(packages_path) if os.path.isdir(os.path.join(packages_path,l))]
            data['instances'] = ','.join(instances) if instances else None
            data['packages'] =','.join(packages) if packages else None
            data['instance_name'] = instances[0] if instances else None

            return Bag(dict(errorcode=None,data=data))
        except Exception:
            return Bag(dict(errorcode='Not existing project',data=data))

    @public_method
    def makeNewProject(self,project_name=None,project_folder_code=None,language=None,base_instance_name=None,included_packages=None):
        path_resolver = PathResolver()
        base_path = path_resolver.project_repository_name_to_path(project_folder_code)

        project_maker = ProjectMaker(project_name, base_path=base_path)
        project_maker.do()
        packages = included_packages.split(',') if included_packages else []
        base_instance_name = base_instance_name or project_name
        site_maker = SiteMaker(project_name, base_path=project_maker.sites_path)
        site_maker.do()
        instance_maker = InstanceMaker(project_name, base_path=project_maker.instances_path,packages=packages)
        instance_maker.do()
        return project_name

    @public_method
    def makeNewPackage(self,package_name=None,name_long=None,is_main_package=None,project_name=None):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project_name)
        packagespath = os.path.join(project_path,'packages')
        instances = os.path.join(project_path,'instances')
        sites = os.path.join(project_path,'sites')
        package_maker = PackageMaker(package_name,base_path=packagespath,helloworld=True,name_long=name_long)
        package_maker.do()
        for d in os.listdir(instances):
            configpath = os.path.join(instances,d,'instanceconfig.xml')
            if os.path.isfile(configpath):
                b = Bag(configpath)
                b.setItem('packages.%s' %package_name,'')
                b.toXml(configpath,typevalue=False,pretty=True)
        for d in os.listdir(sites):
            configpath = os.path.join(sites,d,'siteconfig.xml')
            if os.path.isfile(configpath):
                b = Bag(configpath)
                n = b.getNode('wsgi')
                n.attr['mainpackage'] = package_name
                b.toXml(configpath,typevalue=False,pretty=True)
        return package_name

    @public_method
    def applyPackageChanges(self,project=None,instance=None,package=None,tables=None,connection_params=None,**kwargs):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project)
        if tables and not tables.isEmpty():
            for table_data in tables.values():
                filepath = os.path.join(project_path,'packages',package,'model','%s.py' %table_data['name'])
                self.makeOneTable(filepath,table_data)
        if instance:
            self.extdb_importFromExtDb(connection_params=connection_params,instance=instance,package=package)
        else:
            app = self.getFakeApplication(project,package)
        ThPackageResourceMaker(app,package=package,menu=True).makeResources()
        return 'ok'

    def packageForm(self,form):
        bar = form.top.slotToolbar('2,fbinfo,10,extdbcon,10,*')
        fb = bar.fbinfo.formbuilder(cols=5,border_spacing='3px',datapath='.record')
        fb.textbox(value='^.project_name',validate_onAccept='SET .package_name=null;',validate_onReject='SET .package_name = null;',
                    validate_notnull=True,
                    validate_remote=self.getProjectPath,lbl='Project')
        p = PathResolver()
        fb.data('projectFolders',','.join(p.gnr_config['gnr.environment_xml.projects'].keys()))
        fb.dataRpc('dummy',self.makeNewProject,subscribe_makeNewProject=True,
                    _onResult='SET .project_name=null; SET .project_name=result')
        fb.button('New Project',action="""
            genro.publish('makeNewProject',{project_name:project_name,project_folder_code:project_folder_code,
                                            language:language,included_packages:included_packages});
            """,ask=dict(title='New Project',fields=[
                        dict(name='project_name',lbl='Project name'),
                        dict(name='project_folder_code',lbl='Folder',wdg='filteringSelect',values='^projectFolders'),
                        dict(name='language',lbl='Language',wdg='filteringSelect',values='EN:English,IT:Italian'),
                        dict(name='included_packages',lbl='Packages',wdg='simpleTextArea'),
                        ]),included_packages='gnrcore:sys,gnrcore:adm',language='EN',project_name='=.project_name')
        fb.filteringSelect(value='^.package_name',lbl='Package',validate_notnull=True,
                    values='^.packages',width='7em')

        
        fb.button('New Package',action="""
            genro.publish('makeNewPackage',{package_name:package_name,project_name:project_name,
                                            is_main_package:is_main_package,name_long:name_long});
            """,package_name='=.package_name',project_name='=.project_name',
                    ask=dict(title='New Package',fields=[
                        dict(name='package_name',lbl='Package name'),
                        dict(name='name_long',lbl='Name long'),
                        dict(name='is_main_package',label='Is main package',wdg='checkbox'),
                        ]))
        fb.filteringSelect(value='^.instance_name',lbl='Instance',values='^.instances')
        fb.dataRpc('dummy',self.makeNewPackage,subscribe_makeNewPackage=True,
                    _onResult="""PUT .project_name=null; PUT .package_name=null; 
                                SET .project_name=kwargs.project_name;""")
        bar.extdbcon.slotButton('External Db',
                        action="""
                        genro.publish('openDbConnectionDialog',{project:project,package:package,instance:instance})
                        """,package='^.record.package_name',project='^.record.project_name',
                        instance='^.record.instance_name',
                        hidden='==!package || !project || !instance')
        bc =form.center.borderContainer()
        self.tablesModulesEditor(bc.contentPane(region='top',height='200px',splitter=True),storepath='#FORM.record.tables')
        bc.dataRpc('.record.tables',self.table_editor_loadPackageTables,package='^.record.package_name',
                project='=.record.project_name',
                _if='project&&package',_else='return new gnr.GnrBag();',
                subscribe_closeDbConnectionDialog=True)
        bc.contentPane(region='center',overflow='hidden')


    def tables_struct(self,struct):
        r = struct.view().rows()
        #r.cell('legacy_name',width='10em',name='Legacy Name',hidden='^#FORM.recort.tables?h=!#v')
        r.cell('name',width='10em',name='Name')
        r.cell('pkey',width='10em',name='Pkey')
        r.cell('name_long',width='20em',name='Name long')
        r.cell('name_plural',width='20em',name='Name plural')
        r.cell('caption_field',width='20em',name='Caption field')
        r.cell('status',width='20em',name='Import status')

    def tablesModulesEditor(self,pane,storepath=None,datapath='.tablesFrame'):

        tablesframe = pane.bagGrid(frameCode='tablesModulesEditor',title='Tables',
                                                storepath=storepath,
                                                datapath=datapath,
                                                struct=self.tables_struct,
                                                grid_multiSelect=False,
                                                pbl_classes=True,margin='2px',
                                                addrow=True,delrow=True)


    def getFakeApplication(self,project,package):
        custom_config = Bag()
        pkgcode='%s:%s' %(project,package)
        custom_config.setItem('packages.%s' %pkgcode,None,pkgcode=pkgcode)
        return GnrApp(custom_config=custom_config)

    def getPackagePath(self,project,package):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project)
        return os.path.join(project_path,'packages',package)

