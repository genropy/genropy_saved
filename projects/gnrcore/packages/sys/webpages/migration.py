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
from gnr.core.gnrstring import boolean
from gnr.sql.gnrsql import GnrSqlDb
from gnr.app.gnrdeploy import ProjectMaker, InstanceMaker, SiteMaker,PackageMaker, PathResolver

MORE_ATTRIBUTES = 'cell_,format,validate_notnull,validate_case'

class GnrCustomWebPage(object):
    py_requires='public:Public,gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler'


    def windowTitle(self):
        return '!!Package maker'

    def isDeveloper(self):
        return True


    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Package maker',datapath='main',design='sidebar')
        self.dbSourceTree(bc.contentPane(region='left',width='300px',background='silver',splitter=True,overflow='auto',drawer='close'))
        self.packageForm(bc.frameForm(frameCode='packageMaker',region='center',
                                        datapath='.packagemaker',store='memory',
                                        store_startKey='*newrecord*'))

        

    def dbSourceTree(self,pane):
        fb = pane.div(margin_right='10px').formbuilder(cols=1,border_spacing='3px',
                        datapath='.connection_params',width='100%',colswidth='auto')
        fb.filteringSelect(value='^.implementation',values='postgres,sqlite,mysql,mssql',
                            lbl='Implementation',default='postgres')
        fb.textbox(value='^.dbname',lbl='Dbname',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.host',lbl='Host',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.port',lbl='Port',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.user',lbl='User',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.password',lbl='Password',hidden='^.implementation?=#v=="sqlite"')
        
        fb.simpleTextArea(value='^.filename',lbl='Filepath',
                    hidden='^.implementation?=#v!="sqlite"',width='100%')
        fb.button('Connect',fire='main.connect')
        pane.dataRpc('.connection_result',
                    self.getDbStructure,
                    connection_params='=.connection_params',
                    _fired='^.connect',
                    _xlockScreen=True)

        pane.tree(storepath='.connection_result', persist=False,
                    inspect='shift', labelAttribute='name',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
                    onDrag=self.dbSourceTree_onDrag(),
                    draggable=True,
                    dragClass='draggedItem',
                    onChecked=True,
                    selected_fieldpath='.selpath',
                    getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                    getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")

    def dbSourceTree_onDrag(self):
        return """var modifiers=dragInfo.modifiers;
                  var children=treeItem.getValue()
                  var result;
                  if(!children){
                     result = [treeItem.attr]
                  }else{
                    result=[];
                    children.walk(function(n){if (n.attr.checked && n.attr.tag=='column'){result.push(n.attr);}});
                  }
                  dragValues['source_columns']= result; 
                  
               """


    @public_method
    def getProjectPath(self,value=None,**kwargs):
        p = PathResolver()
        try:
            p.project_name_to_path(value)
            return True
        except Exception:
            return 'Not existing project'

    @public_method
    def getProjectPackage(self,value=None,project_name=None,**kwargs):
        if not project_name:
            return 'Missing project'
        p = PathResolver()
        try:
            project_path = p.project_name_to_path(project_name)
            if os.path.exists(os.path.join(project_path,'packages',value)):
                return True
            return 'Not existing package'
        except Exception:
            return 'Not existing project'

    @public_method
    def applyPackageChanges(self,data=None,**kwargs):
        print x

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
    def makeOneTable(self,project=None,package=None,table=None,table_data=None):
        path_resolver = PathResolver()
        project_path = path_resolver.project_name_to_path(project)
        filpath = os.path.join(project_path,'packages',package,'model','%s.py' %table)
        table_data['name_long'] = table_data['name_long'] or table
        table_data['name_plural'] = table_data['name_plural'] or table
        table_data['caption_field'] = table_data['caption_field'] or table_data['pkey']
        columns = table_data['_columns']
        header = """# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('%(name)s', pkey='%(pkey)s', name_long='!!%(name_long)s', 
                            name_plural='!!%(name_plural)s',caption_field='%(caption_field)s',
                            legacy_name='%(legacy_name)s')
""" %table_data
        with open(filpath,'w') as f:
            f.write(header)
            for col in columns.digest('#v'):
                relation = col.pop('_relation')
                self._writeColumn(f,col)
                if relation:
                    self._writeRelation(f,relation)
                f.write('\n')

    def _writeColumn(self,f,col):
        attributes = Bag()

        name = col.pop('name')
        dtype = col.pop('dtype')
        size = col.pop('size')
        name_long = col.pop('name_long')
        name_short = col.pop('name_short')

        more_attributes = col.pop('_more_attributes')

        if dtype and dtype not in ('A','T','C'):
            attributes['dtype'] = dtype
        if size:
            attributes['size'] = size
        attributes.setItem('name_long', name_long or name,localized=True)
        if name_short:
            attributes.setItem('name_short', name_short,localized=True)
        attributes.update(col)
        
        
       #if more_attributes:
       #    for key,dtype,value in more_attributes.digest('#v.attribute_key,#v.attribute_dtype,#v.attribute_value'):
       #        if v not in (None,''):
       #            pass
       #            attributes[key] = 
       #        
       #f.write("        tbl.column('%s', %s)" % (name, ', '.join(atlst)))

    def _writeRelation(self,f,relation):
        pkg,table,id = relation['relation'].split('.')
        if pkg == 'main':
            relation['relation'] = '%s.%s' %(table,id)
        atlst = []
        relation_name = relation.pop('relation_name')
        one_one = relation.pop('one_one')
        deferred = relation.pop('deferred')

        if relation_name:
            atlst.append("relation_name='%s'" %relation_name)
        if one_one:
            atlst.append("one_one='*'" if not relation_name else "one_one=True")
        if relation['onDelete']:
            atlst.append("onDelete='%s'" %relation.pop('onDelete'))
        if relation['mode']:
            atlst.append("mode='%s'" %relation.pop('mode'))
        if deferred:
            atlst.append('deferred=True')
        for k, v in relation.items():
            if v is not None:
                atlst.append("%s='%s'" % (k, v))
        f.write(""".relation('%s',%s)"""  %(relation['relation'],', '.join(atlst)))

    def packageForm(self,form):
        bar = form.top.slotToolbar('2,fbinfo,*,applyChanges,semaphore,5')
        bar.applyChanges.slotButton('Apply',action="""if(this.form.isValid()){
                FIRE #FORM.makePackage;
            }else{
                genro.dlg.alert('Invalid data','Error');
            }""")
        bar.dataRpc('dummy',self.applyPackageChanges,data='=#FORM.record',_fired='^#FORM.makePackage')

        fb = bar.fbinfo.formbuilder(cols=4,border_spacing='3px',datapath='.record')
        fb.textbox(value='^.project_name',validate_notnull=True,validate_remote=self.getProjectPath,lbl='Project')
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
        fb.textbox(value='^.package_name',validate_notnull=True,lbl='Package',
                    validate_remote=self.getProjectPackage,
                    validate_project_name='=.project_name',
                    width='7em')

        fb.button('New Package',action="""
            genro.publish('makeNewPackage',{package_name:package_name,project_name:project_name,
                                            is_main_package:is_main_package,name_long:name_long});
            """,package_name='=.package_name',project_name='=.project_name',
                    ask=dict(title='New Package',fields=[
                        dict(name='package_name',lbl='Package name'),
                        dict(name='name_long',lbl='Name long'),
                        dict(name='is_main_package',label='Is main package',wdg='checkbox'),
                        ]))
        fb.dataRpc('dummy',self.makeNewPackage,subscribe_makeNewPackage=True,
                    _onResult='PUT .package_name=null; SET .package_name=result')

        self.packageGrids(form.center.borderContainer())

    def tables_struct(self,struct):
        r = struct.view().rows()
        r.cell('legacy_name',width='10em',name='Legacy Name')
        r.cell('name',width='10em',name='Name',edit=True)
        r.cell('pkey',width='10em',name='Pkey')
        r.cell('name_long',width='20em',name='Name long',edit=True)
        r.cell('name_plural',width='20em',name='Name plural',edit=True)
        r.cell('caption_field',width='20em',name='Caption field',edit=True)

    def columns_struct(self,struct):
        r = struct.view().rows()
        r.cell('legacy_name',width='10em',name='Legacy Name')
        r.cell('name',width='10em',name='Name',edit=True)
        r.cell('dtype',width='5em',name='Dtype',edit=dict(tag='filteringSelect',values='T:Text,I:Int,N:Decimal,B:Bool,D:Date,DH:Timestamp,X:Bag'))
        r.cell('size',width='5em',name='Size',edit=True)
        r.cell('group',width='5em',name='Group',edit=True)
        r.cell('name_long',width='20em',name='Name long',edit=True)
        r.cell('name_short',width='10em',name='Name short',edit=True)
        r.cell('indexed',width='5em',name='Indexed',edit=True,dtype='B')
        r.cell('unique',width='5em',name='Unique',edit=True,dtype='B')
        r.cell('_more_attributes',width='20em',name='More attributes',edit=True,editOnOpening=""" 
                                        var more_attributes = rowData.getItem(field);
                                        genro.publish('edit_more_attributes',{more_attributes:more_attributes,rowIndex:rowIndex})
                                        return false;
                                    """)

        r.cell('_relation',width='20em',name='Relation',edit=True,
                     editOnOpening="""var relation = rowData.getItem(field);
                                    if(relation){
                                        relation = relation.deepCopy();
                                    }
                                    genro.publish('edit_relation',{relation:relation,rowIndex:rowIndex})
                                    return false;
                                    """)
    def relationEditorDialog(self,bc):
        dlg = bc.dialog(title='Relation',
                        subscribe_edit_relation="""this.widget.show()
                                                   this.setRelativeData('.data',$1.relation);
                                                   this.setRelativeData('.rowIndex',$1.rowIndex)
                                                """,datapath='#FORM.relationEditor')
        frame = dlg.framePane(height='200px',width='400px')
        pane = frame.center.contentPane()
        fb = pane.formbuilder(cols=1,datapath='.data')
        fb.textbox(value='^.relation',lbl='Relation')
        fb.textbox(value='^.relation_name',lbl='Relation name')
        fb.textbox(value='^.mode',lbl='Mode')
        fb.textbox(value='^.onDelete',lbl='onDelete')
        fb.textbox(value='^.onDelete_sql',lbl='onDelete(sql)')
        fb.textbox(value='^.onUpdate',lbl='onUpdate')
        fb.textbox(value='^.onUpdate_sql',lbl='onUpdate(sql)')
        fb.textbox(value='^.one_name',lbl='One name')
        fb.textbox(value='^.many_name',lbl='Many name')
        fb.checkbox(value='^.deferred',label='Deferred')
        fb.checkbox(value='^.one_one',label='One one')

        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""griddata.setItem('#'+rowIndex+'._relation',data.deepCopy());
                                                    dlg.hide()""",
                                        dlg=dlg.js_widget,
                                        griddata='=#FORM.current_columns',
                                        rowIndex='=.rowIndex',
                                        data='=.data')


    def moreAttributesDialog(self,bc):
        dlg = bc.dialog(title='More attributes',
                        subscribe_edit_more_attributes="""this.widget.show()
                                                   this.setRelativeData('.data',$1.more_attributes);
                                                   this.setRelativeData('.rowIndex',$1.rowIndex)
                                                """,datapath='#FORM.moreAttributes')
        def struct(struct):
            r = struct.view().rows()
            r.cell('attribute_key',name='Key',edit=dict(tag='ComboBox',values=MORE_ATTRIBUTES),width='10em')
            r.cell('attribute_dtype',name='Dtype',edit=dict(tag='filteringSelect',
                                                            values='T:Text,B:Bool,I:Int,N:Decimal'),width='10em')
            r.cell('attribute_value',name='Value',edit=True,width='10em')

        frame = dlg.bagGrid(height='200px',width='400px',storepath='#FORM.moreAttributes.data',struct=struct)
        
        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""griddata.setItem('#'+rowIndex+'._more_attributes',data.deepCopy());
                                                    dlg.hide()""",
                                        dlg=dlg.js_widget,
                                        griddata='=#FORM.current_columns',
                                        rowIndex='=.rowIndex',
                                        data='=.data')

    def packageGrids(self,bc):
        self.relationEditorDialog(bc)
        self.moreAttributesDialog(bc)
        tablesframe = bc.contentPane(region='top',height='50%',splitter=True).bagGrid(frameCode='tables',title='Tables',
                                                storepath='#FORM.record.tables',
                                                datapath='#FORM.tablesFrame',
                                                struct=self.tables_struct,
                                                grid_autoSelect=True,
                                                grid_multiSelect=False,
                                                grid_selected_name='#FORM.current_table',
                                                pbl_classes=True,margin='2px',
                                                addrow=True,delrow=True)
        bar = tablesframe.bottom.slotToolbar('*,makeSelectedTable,5')
        bar.makeSelectedTable.slotButton('Make selected',action='FIRE #FORM.makeSelectedTable',
                                        disabled='^#FORM.current_table?=!#v')
        bar.dataRpc('dummy',self.makeOneTable,table='=#FORM.current_table',
                    project='=#FORM.record.project_name',package='=#FORM.record.package_name',
                    _onCalling="""kwargs['table_data'] = this.getRelativeData('#FORM.record.tables').getItem(table).deepCopy();
                                console.log(kwargs);
                                """,
                    _if='project&&package&&table',
                    _fired='^#FORM.makeSelectedTable')
        tablesgrid = tablesframe.grid
        tablesgrid.dragAndDrop('source_columns')
        tablesgrid.dataController("""
            var tblpars,tableNode,tblVal,columnNode,colVal,colpars,columns,pkeycol;
            data.forEach(function(col){
                    tblpars = objectExtract(col,'table_*');
                    var tblname = tblpars['name'].toLowerCase();
                    tableNode = tables.getNode(tblname);

                    if(!tableNode){
                        pkeycol = tblpars.pkey.toLowerCase()
                        tblVal = new gnr.GnrBag({name:tblname,legacy_name:tblpars['name'],
                                                pkey:pkeycol,
                                                _columns:new gnr.GnrBag()});
                        tableNode = tables.setItem(tblname,tblVal);
                    }
                    columns = tableNode.getValue().getItem('_columns');
                    var colname = col.name.toLowerCase()
                    columnNode =  columns.getNode(colname);
                    if(!columnNode){
                        var relate_to = col.relate_to?col.relate_to.toLowerCase():null
                        columnNode = columns.setItem(colname,new gnr.GnrBag({name:colname,legacy_name:col.name,
                                                                name_long:col.name,dtype:col.dtype,size:col.size,
                                                                indexed:col.indexed,unique:col.unique}));
                        if(relate_to){
                            columnNode._value.setItem('_relation',new gnr.GnrBag({relation:relate_to,relation_name:null,
                                                                                  mode:'foreignkey',onDelete:'raise',one_name:null,
                                                                                  many_name:null,deferred:false}));
                        }
                    }
                })
            """,data='^.dropped_source_columns',dropInfo='=.droppedInfo_source_columns',
                tables='=#FORM.record.tables')

        columnsframe = bc.contentPane(region='center').bagGrid(frameCode='columns',title='Columns',
                                                        datapath='#FORM.columnsFrame',
                                                    storepath='#FORM.current_columns',
                                                    struct=self.columns_struct,
                                                    pbl_classes=True,margin='2px',
                                                    addrow=True,delrow=True)
        bc.dataController("columnsframe.setHiderLayer(!current_table,{message:'Select table'})",
                            columnsframe=columnsframe,current_table='^#FORM.current_table')

        bc.dataController(
            """ var oldvalue = _triggerpars.kw.oldvalue;
                var columns;
                if(oldvalue && current_table!=oldvalue && current_columns){
                    tables.setItem(oldvalue+'._columns',current_columns.deepCopy(),null,{doTrigger:false});
                }
                if(current_table){
                    columns = tables.getItem(current_table+'._columns');
                    if(columns){
                        columns = columns.deepCopy();
                    }
                }
                SET #FORM.current_columns = columns;
                """,
                current_table='^#FORM.current_table',
                current_columns='=#FORM.current_columns',
                tables='=#FORM.record.tables')
        bc.dataController("""
            if(_node.label=='current_columns'){
                return;
            }
            if(_reason=='child'){
                tables.setItem(current_table+'._columns',current_columns.deepCopy(),null,{doTrigger:false});
            }
            """,current_columns='^#FORM.current_columns',current_table='=#FORM.current_table',
            tables='=#FORM.record.tables')

    @public_method
    def getDbStructure(self,connection_params=None):
        print x
        config = self.site.gnrapp.config
        dbname=connection_params['dbname'] or connection_params['filename']
        if connection_params['implementation']!='sqlite':
            connection_params['host'] = connection_params['host'] or config['db?host'] or 'localhost'
            connection_params['user'] = connection_params['user'] or config['db?user']
            connection_params['password'] = connection_params['password'] or config['db?password']
            connection_params['port'] = connection_params['port'] or config['db?port']

        externaldb = GnrSqlDb(implementation=connection_params['implementation'],
                            dbname=dbname,
                            host=connection_params['host'],user=connection_params['user'],
                            password = connection_params['password'])
        externaldb.importModelFromDb()
        src = externaldb.model.src
        result = Bag()
        for pkg in src['packages'].keys():
            pkgval = Bag()
            result.setItem(pkg, pkgval,name=pkg,checked=False)
            for table,tblattr,tblval in src['packages'][pkg]['tables'].digest('#k,#a,#v'):
                tblattr = dict(tblattr)
                tblattr['checked'] = False
                tblattr['name'] = table
                tableval = Bag()
                pkgval.setItem(table,tableval,**tblattr)
                for column,colattr,colval in tblval['columns'].digest('#k,#a,#v'):
                    cv = dict(colattr)
                    for t,v in tblattr.items():
                        cv['table_%s' %t] = v
                    cv['checked'] = False
                    cv['name'] = column
                    if colval:
                        relnode = colval.getNode('relation')
                        cv['relate_to'] = relnode.attr['related_column']
                    tableval.setItem(column,None,**cv)
                for column,unique in tblval['indexes'].digest('#a.columns,#a.unique'):
                    n = tableval.getNode(column)
                    if n:
                        n.attr['indexed'] = True
                        n.attr['unique'] = boolean(unique)

        return result



