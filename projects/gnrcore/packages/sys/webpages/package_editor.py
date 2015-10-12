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
                   package_editor/extdb_explorer:ExtDbExplorer,
                   package_editor/model_editor:TableModuleEditor"""
    pageOptions={'openMenu':False,'enableZoom':False}
    js_requires ='package_editor/package_editor'
    css_requires ='package_editor/package_editor'
    auth_main = 'admin'

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


    def packageForm(self,form):
        bar = form.top.slotToolbar('2,fbinfo,10,extdbcon,*,dbsetup,10')
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
                        tables='=.record.tables',
                        hidden='==!package || !project || !instance')
        bar.dbsetup.slotButton('DbSetup',fire_dbsetup='#FORM.instanceAction',disabled='^.record.instance_name?=!#v')
        bar.dataRpc('dummy',self.actionOnInstance,
                            instance='=.record.instance_name',
                            package='=.record.package_name',_if='instance',
                            selectedTables='=#FORM.selectedTables',
                            _ask="""You are going to overwrite current resources. Do you want to proceed anyway?""",
                            _ask_if='action=="make_resources_force"',
                        _lockScreen=True,action='^#FORM.instanceAction',
                        _onResult="""
                        var currenModelModule = GET #FORM.currenModelModule;
                        var currenResourceModule = GET #FORM.currenResourceModule;
                        PUT #FORM.currenModelModule = null;
                        PUT #FORM.currenResourceModule = null;
                        SET #FORM.currenModelModule = currenModelModule;
                        SET #FORM.currenResourceModule = currenResourceModule;
                        """)
        bc =form.center.borderContainer()
        form.dataController('bc.setHiderLayer(!package_name,{message:message})',
                            message='!!Please select or create a project<br/>and select or create a package',
                            bc=bc,package_name='^.record.package_name')
        self.tablesModulesEditor(bc.contentPane(region='left',width='380px',splitter=True),storepath='#FORM.record.tables',
                                project='=.record.project_name',package='^.record.package_name')
        self.sourceViewer(bc.tabContainer(region='center',margin='2px'))

    @public_method
    def dbSetupOnInstance(self,instance=None):
        app = GnrApp(instance)
        destdb = app.db
        if destdb.model.check():
            destdb.model.applyModelChanges()

    @public_method
    def actionOnInstance(self,instance=None,action=None,package=None,selectedTables=None,**kwargs):
        app = GnrApp(instance) #it does not work in uwsgi fix it
        if action.startswith('make_resources'):
            ThPackageResourceMaker(app,package=package,menu=True,tables=selectedTables,
                                    force=action=='make_resources_force').makeResources()
        if action in ('dbsetup','import_legacy'):
            destdb = app.db
            if destdb.model.check():
                self.log('applyModelChanges')
                destdb.model.applyModelChanges()
            if action =='import_legacy':
                app.importFromLegacyDb()



    def sourceViewer(self,tc):
        tc.contentPane(title='Model',overflow='hidden').codeEditor(value='^#FORM.currenModelModule')
        resourcePane = tc.contentPane(title='TH Resource',overflow='hidden')
        resourcePane.codeEditor(value='^#FORM.currenResourceModule')

    def getFakeApplication(self,project,package):
        custom_config = Bag()
        pkgcode='%s:%s' %(project,package)
        custom_config.setItem('packages.%s' %pkgcode,None,pkgcode=pkgcode)
        return GnrApp(custom_config=custom_config)

    def getPackagePath(self,project,package):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project)
        return os.path.join(project_path,'packages',package)

