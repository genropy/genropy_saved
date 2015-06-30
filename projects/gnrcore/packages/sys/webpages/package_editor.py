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
    py_requires='public:Public,gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler,extdb_explorer:ExtDbExplorer'

    def windowTitle(self):
        return '!!Package editor'

    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Package editor',datapath='main',design='sidebar')
        self.packageForm(bc.frameForm(frameCode='packageMaker',region='center',
                                        datapath='.packageform',store='memory',
                                        store_startKey='*newrecord*'))

    @public_method
    def getProjectPath(self,value=None,**kwargs):
        p = PathResolver()
        try:
            path = p.project_name_to_path(value)
            instances_path = os.path.join(path,'instances')
            packages_path = os.path.join(path,'packages')
            instances = [l for l in os.listdir(instances_path) if os.path.isfile(os.path.join(instances_path,l,'instanceconfig.xml'))]
            packages = [l for l in os.listdir(packages_path) if os.path.isdir(os.path.join(packages_path,l))]
            data = Bag()
            data['instances'] = ','.join(instances) if instances else None
            data['packages'] =','.join(packages) if packages else None
            return Bag(dict(errorcode=None,data=data))
        except Exception:
            return 'Not existing project'

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
        bar = form.top.slotToolbar('2,fbinfo,10,extdbcon,10,connectionTpl,*,applyChanges,semaphore,5')
        bar.connectionTpl.div('^main.connectionTpl')
        bar.dataController("""
                var implementation = connection_params.getItem('implementation');
                var filename = connection_params.getItem('filename');
                var dbname = connection_params.getItem('dbname');
                var r = ''
                var filepath = connection_params.getItem('filename');
                if(implementation=='sqlite' && filepath){
                    var f = filepath.split(/\//);
                    r = '<b>sqlite:</b>'+f[f.length-1];
                }else if(implementation && connection_params.getItem('dbname')){
                    r = dataTemplate('<b>$implementation:</b>$dbname',connection_params)
                }
                SET main.connectionTpl = r;
                """,connection_params='^main.connection_params',_onStart=True,color='#444')
        bar.extdbcon.dbConnectionPalette(datapath='main')
        bar.applyChanges.slotButton('Apply',action="""if(this.form.isValid()){
                FIRE #FORM.makePackage;
            }else{
                genro.dlg.alert('Invalid data','Error');
            }""")
        bar.dataRpc('dummy',self.applyPackageChanges,project='=#FORM.record.project_name',package='=#FORM.record.package_name',
                    instance='=#FORM.record.selected_instance',connection_params='=main.connection_params',
                    tables='=#FORM.record.tables',
                    _onCalling="""
                        var tables_to_send = new gnr.GnrBag();
                        kwargs.tables.forEach(function(n){
                            if(n.attr._loadedValue || n._value.getNodeByAttr('_loadedValue')){
                                tables_to_send.setItem(n.label,n._value.deepCopy(),n.attr);
                            }
                        });
                        kwargs.tables=tables_to_send;
                    """,
                    _fired='^#FORM.makePackage',_onResult='genro.dlg.alert("Package Done","Message");',
                    _xlockScreen=True,timeout=0)
        fb = bar.fbinfo.formbuilder(cols=5,border_spacing='3px',datapath='.record')
        fb.textbox(value='^.project_name',validate_onAccept='SET .package_name=null;',validate_onReject='SET .package_name = null;',
                    validate_notnull=True,
                    validate_remote=self.getProjectPath,lbl='Project')
        p = PathResolver()
        fb.data('projectFolders',','.join(p.gnr_config['gnr.environment_xml.projects'].keys()))
        fb.dataRpc('dummy',self.makeNewProject,subscribe_makeNewProject=True,
                    _onResult='PUT .project_name=null; SET .project_name=result')
        fb.button('New Project',action="""
            genro.publish('makeNewProject',{project_name:project_name,project_folder_code:project_folder_code,
                                            language:language,base_instance_name:base_instance_name,
                                            included_packages:included_packages});
            """,project_name='=.project_name',
                    ask=dict(title='New Project',fields=[
                        dict(name='project_name',lbl='Project name'),
                        dict(name='project_folder_code',lbl='Folder',wdg='filteringSelect',values='^projectFolders'),
                        dict(name='language',lbl='Language',wdg='filteringSelect',values='EN:English,IT:Italian'),
                        dict(name='base_instance_name',lbl='Instance name'),
                        dict(name='included_packages',lbl='Packages',wdg='simpleTextArea'),
                        ]),included_packages='gnrcore:sys,gnrcore:adm',language='EN',project_folder_code='',
                    base_instance_name='=.project_name')
        fb.filteringSelect(value='^.package_name',validate_notnull=True,lbl='Package',
                    validate_onAccept='FIRE #FORM.resetPackageData; FIRE #FORM.loadPackage = value;',validate_onReject="""FIRE #FORM.resetPackageData;""",
                    values='^.packages',
                    width='7em')
        fb.dataController("""
                    SET #FORM.record.tables = null;
                    """,_fired='^#FORM.resetPackageData')
        fb.dataRpc('#FORM.record.tables',self.table_editor_loadPackageTables,package='^#FORM.loadPackage',
                project='=#FORM.record.project_name',
                _if='project&&package',_else='return gnr.GnrBag();')
        fb.button('New Package',action="""
            genro.publish('makeNewPackage',{package_name:package_name,project_name:project_name,
                                            is_main_package:is_main_package,name_long:name_long});
            """,package_name='=.package_name',project_name='=.project_name',
                    ask=dict(title='New Package',fields=[
                        dict(name='package_name',lbl='Package name'),
                        dict(name='name_long',lbl='Name long'),
                        dict(name='is_main_package',label='Is main package',wdg='checkbox'),
                        ]))
        fb.filteringSelect(value='^.selected_instance',lbl='Instance',values='^.instances')
        fb.dataRpc('dummy',self.makeNewPackage,subscribe_makeNewPackage=True,
                    _onResult='PUT .package_name=null; SET .package_name=result')
        self.packageGrids(form.center.borderContainer())

    def tables_struct(self,struct):
        r = struct.view().rows()
        r.cell('legacy_name',width='10em',name='Legacy Name',hidden='^main.connectionTpl?=!#v')
        r.cell('name',width='10em',name='Name')
        r.cell('pkey',width='10em',name='Pkey')
        r.cell('name_long',width='20em',name='Name long')
        r.cell('name_plural',width='20em',name='Name plural')
        r.cell('caption_field',width='20em',name='Caption field')
        r.cell('status',width='20em',name='Import status')

    def packageGrids(self,bc):
        tablesframe = bc.contentPane(region='top',height='200px',splitter=True).bagGrid(frameCode='tables',title='Tables',
                                                storepath='#FORM.record.tables',
                                                datapath='#FORM.tablesFrame',
                                                struct=self.tables_struct,
                                                grid_multiSelect=False,
                                                grid_subscribe_update_import_status="""
                                                    var b = this.widget.storebag();
                                                    var r = b.getItem($1.table);
                                                    if(!r){
                                                        return;
                                                    }
                                                    r.setItem('status',$1.status);
                                                    """,
                                                pbl_classes=True,margin='2px',
                                                addrow=True,delrow=True)
        tablesgrid = tablesframe.grid
        tablesgrid.dragAndDrop('source_columns')
        tablesgrid.dataController("""
            var tblpars,tableNode,tblVal,columnNode,colVal,colpars,columns,pkeycol,status,col_legacy_name;
            data.forEach(function(col){
                    tblpars = objectExtract(col,'table_*');
                    var tblname = tblpars['name'].toLowerCase();
                    tableNode = tables.getNode(tblname);

                    if(!tableNode){
                        pkeycol = tblpars.pkey.toLowerCase()
                        status = ''; //dataTemplate(tpl,{tblname:tblname});
                        tblVal = new gnr.GnrBag({name:tblname,legacy_name:tblpars['fullname'],
                                                pkey:pkeycol,
                                                _columns:new gnr.GnrBag(),
                                                status:status});
                        tableNode = tables.setItem(tblname,tblVal);
                    }
                    columns = tableNode.getValue().getItem('_columns');
                    var colname = col.name.toLowerCase()
                    columnNode =  columns.getNode(colname);
                    if(!columnNode){
                        var relate_to = col.relate_to?col.relate_to.toLowerCase():null
                        col_legacy_name = col.name;
                        if(col_legacy_name=='_multikey'){
                            col_legacy_name = null;
                        }
                        columnNode = columns.setItem(colname,new gnr.GnrBag({name:colname,legacy_name:col_legacy_name,
                                                                name_long:stringCapitalize(col.name),dtype:col.dtype,size:col.size,
                                                                indexed:col.indexed,unique:col.unique}));
                        if(relate_to){
                            columnNode._value.setItem('_relation',new gnr.GnrBag({relation:relate_to,relation_name:null,
                                                                                  onDelete:'raise',one_name:null,
                                                                                  many_name:null,deferred:false}));
                        }
                    }
                })
            """,data='^.dropped_source_columns',dropInfo='=.droppedInfo_source_columns',
                tables='=#FORM.record.tables',
                tpl="""<a style="cursor:pointer; text-align:center;" href="javascript:genro.publish('import_table',{table:'$tblname'})">import</a>""")
        bc.contentPane(region='center',overflow='hidden')

    def getFakeApplication(self,project,package):
        custom_config = Bag()
        pkgcode='%s:%s' %(project,package)
        custom_config.setItem('packages.%s' %pkgcode,None,pkgcode=pkgcode)
        return GnrApp(custom_config=custom_config)

    def getPackagePath(self,project,package):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project)
        return os.path.join(project_path,'packages',package)

