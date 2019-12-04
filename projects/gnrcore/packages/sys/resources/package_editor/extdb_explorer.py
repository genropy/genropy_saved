# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from builtins import str
from collections import defaultdict
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql import GnrSqlDb
from gnr.app.gnrapp import GnrApp
from gnr.core.gnrstring import boolean
from time import time
from gnr.app.gnrdeploy import PathResolver
import os

class ExtDbExplorer(BaseComponent):
    py_requires='package_editor/model_editor:TableModuleWriter'

    @struct_method
    def extDbConnectionDialog(self,pane,title='Ext DB Connection',datapath='exdb',
                            project=None,package=None,instance=None,**kwargs):
        dialog = pane.dialog(title=title,datapath=datapath,closable=True,
                            subscribe_openDbConnectionDialog="""
                                this.widget.show();
                                if($1===true){
                                    return;
                                }
                                SET .project = $1.project;
                                SET .package = $1.package;
                                SET .instance = $1.instance;
                            """,subscribe_closeDbConnectionDialog="this.widget.hide();",**kwargs)
        frame = dialog.framePane(frameCode='externaldb',height='500px',width='1000px')
        self.extdb_contentFrame(frame)
        frame.dataRpc('dummy',self.extdb_buildTableModules,
                    connection_params='=.connection_params',
                    package='=.package',
                    instance='=.instance',
                    project='=.project',
                    data='=.data',
                    timeout=5000000,
                    _lockScreen=dict(thermo=True),
                    _fired='^.addToModel',
                    _onCalling="""
                    var columns = new gnr.GnrBag();
                    kwargs['data'].walk(function(n){
                        if((n.attr.checked+'').startsWith('disabled')){
                            return;
                        }
                        if (n.attr.checked && n.attr.tag=='column'){
                            var table_data = new gnr.GnrBag();
                            let kw = {...n.attr};
                            delete kw.default;
                            columns.setItem(n.attr.table_fullname+'.'+n.attr.name,null,kw);
                        }
                    });
                    kwargs['data'] = columns
                    """,
                    _onResult="""
                    console.log('extdb_buildTableModules finished');
                    genro.publish('reloadTableModules');
                    genro.publish('closeDbConnectionDialog');""")
        bar = frame.bottom.slotBar('*,cancel,confirm,5',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton("Cancel",action="genro.publish('closeDbConnectionDialog');",dlg=dialog.js_widget)
        bar.confirm.div(hidden='^.instance?=!#v').button('Add to model',action="""
            FIRE .addToModel;
        """)

    @public_method
    def onUploaded_exdbSqliteUploader(self, file_url=None, file_path=None, file_ext=None, instance_name=None,
                                  action_results=None,filename=None, **kwargs):
        sn = self.site.storageNode(file_path)
        p = PathResolver()
        instance_path = p.instance_name_to_path(instance_name)
        destpath = os.path.join(instance_path,'data','legacy',filename)
        sn.move(destpath)
        self.clientPublish('update_filename',filename=destpath,nodeId='exdb_params')


    def extdb_contentFrame(self,frame):
        top = frame.top.slotToolbar('2,fbconnection,5,connecbutton,*,2',height='22px')
        bc = frame.center.borderContainer()
        fb = top.fbconnection.formbuilder(cols=7,border_spacing='3px',nodeId='exdb_params',
                                        selfsubscribe_update_filename="""SET .filename = $1.filename
                                        genro.publish('floating_message',{message:_T('Sql file added. Press connect'),messageType:'message'});
                                        """,
                                        datapath='.connection_params')
        fb.filteringSelect(value='^.implementation',values='postgres,sqlite,mysql,mssql,fourd',
                            lbl='Implementation',width='7em')
        fb.textbox(value='^.dbname',lbl='Dbname',width='8em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.host',lbl='Host',width='8em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.port',lbl='Port',width='5em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.user',lbl='User',width='7em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.password',lbl='Password',width='5em',hidden='^.implementation?=#v=="sqlite"')
        fb.dropUploader(nodeId='exdbSqliteUploader',
            rpc_instance_name='=main.data.record.instance_name', 
            uploadPath='page:sqliteSource',
            height = '16px', width='30em',
            line_height='15px',font_size='14px',
            hidden='^.implementation?=#v!="sqlite"',
            label= '!![en]Drop sqlite file here or do double click to browse your disk')
    
        top.connecbutton.slotButton('Connect',
                                    action="""FIRE .connect= new gnr.GnrBag({"avoidImported":avoidImported,"avoidNoPkey":avoidNoPkey,"avoidEmpty":avoidEmpty});""",
                                    ask=dict(title='Connect options',
                                            fields=[dict(name='avoidImported',label='Avoid imported',tag='checkbox'),
                                                    dict(name='avoidNoPkey',label='Avoid tables without pkey',tag='checkbox'),
                                                    dict(name='avoidEmpty',label='Avoid empty tables',tag='checkbox')]),
                                avoidImported=True,avoidNoPkey=False,avoidEmpty=False)
        top.dataRpc('.data',
                    self.extdb_getDbStructure,project='=.project',package='=.package',
                    connection_params='=.connection_params',
                    timeout=5000000,
                    connection_options='^.connect',
                    _lockScreen=True)
        center = bc.borderContainer(region='center')
        left = center.framePane(region='left',width='300px',splitter=True)
        #bar = left.top.slotToolbar('*,searchOn,2')
       #bar.fbopt.formbuilder(,border_spacing='0')
        left.center.contentPane(overflow='auto').tree(storepath='.data', persist=False,#searchOn=True,
                    margin='10px',
                    inspect='shift', labelAttribute='name',
                    _class='fieldsTree',
                    hideValues=True,
                    draggable=True,
                    dragClass='draggedItem',
                    onChecked=True,
                    connect_ondblclick="""
                    var ew = dijit.getEnclosingWidget($1.target);
                    if(ew.item){
                        var attr = ew.item.attr;
                        if(attr.tag=='table'){
                            dojo.query('.dijitTreeLabel',ew.tree.domNode).forEach(function(n){genro.dom.removeClass(n,'selectedTreeNode')})
                            genro.dom.addClass(ew.labelNode,'selectedTreeNode')
                            this.setRelativeData('.source.current_table',attr.name);
                            this.setRelativeData('.source.current_columns',ew.item.getValue().deepCopy());
                            this.fireEvent('.source.getPreviewData',attr.fullname);
                        }
                    }
                    """,
                    selected_fieldpath='.selpath',
                    getLabelClass="""var ct = this.sourceNode.getRelativeData('.source.current_table');
                                        if (node.label==ct){
                                            return "selectedTreeNode"
                                        }
                                        """)
        bccenter = center.borderContainer(region='center')
        frame= bccenter.framePane(frameCode='previewGrid',region='top',height='300px',_class='pbl_roundedGroup',margin='2px')
        bar = frame.top.slotBar('2,vtitle,*',height='20px',_class='pbl_roundedGroupLabel')
        bar.vtitle.div('==_current_table?_current_table+" columns":"No table selected"',_current_table='^.source.current_table')
        g = frame.quickGrid(value='^.source.current_columns')
        g.column('name',width='10em',name='Name')
        g.column('dtype',width='5em',name='Dtype')
        g.column('is_pkey',width='5em',name='Pkey',dtype='B')
        g.column('indexed',width='5em',name='Indexed',dtype='B')
        g.column('unique',width='5em',name='Unique',dtype='B')
        g.column('size',width='5em',name='Size')
        frame = bccenter.roundedGroupFrame(title='Data',region='center')
        frame.center.contentPane().quickGrid(value='^.source.previewData')
        frame.dataRpc('.source.previewData',self.extdb_getPreviewData,
                    connection_params='=.connection_params',
                    table='^.source.getPreviewData',
                    _frame=frame,
                    _onCalling=""" 
                    kwargs._frame.setHiderLayer(true,{message:'Loading data'})
                    """,_onResult="""
                    kwargs._frame.setHiderLayer(false);
                    """)



    @public_method
    def extdb_buildTableModules(self,project=None,package=None,instance=None,data=None,connection_params=None,**kwargs):
        p = PathResolver()
        project_path = p.project_name_to_path(project)
        modelpath = os.path.join(project_path,'packages',package,'model')
        instance_path = os.path.join(p.instance_name_to_path(instance),'config','instanceconfig.xml')
        instance_bag = Bag(instance_path)
        dbname = connection_params['dbname'] or connection_params['filename']
        legacydb,ext = os.path.splitext(os.path.basename(dbname))
        parsdict = dict()
        for k,v in list(connection_params.items()):
            if v not in ('',None):
                parsdict[k] = v
        instance_bag.setItem('legacy_db.%s' %legacydb,None,**parsdict)
        instance_bag.toXml(instance_path,typevalue=False,pretty=True)
        for srcpkg,tables in list(data.items()):
            for tablename,columns in self.utils.quickThermo(list(tables.items()),labelcb=lambda r: '%s.%s' %(srcpkg,r[0]),maxidx=len(tables)):
                firstColAttr = columns.getAttr('#0')
                tablename = tablename.lower()
                tablename = tablename.replace(' ','_').replace('.','_')
                table_data = Bag()
                table_data['name'] = tablename
                table_data['legacy_name'] = firstColAttr.get('table_fullname')
                table_data['legacy_db'] = legacydb
                pkey = firstColAttr.get('table_pkey')
                if pkey:
                    pkey = pkey.lower()
                table_data['pkey'] = pkey or None
                columns_bag = Bag()
                table_data['_columns'] = columns_bag
                caption_field = None
                for colattr in columns.digest('#a'):
                    legacy_name = colattr['name']
                    if legacy_name=='_multikey':
                        legacy_name = None
                    colname = colattr['name'].lower()
                    dtype=colattr.get('dtype')
                    if not caption_field and dtype in ('A','T','C') and colname!=pkey:
                        caption_field = colname
                    b = Bag(dict(name=colname,legacy_name=legacy_name,
                                                        name_long=None,dtype=dtype,
                                                        size=str(colattr.get('size')) if colattr.get('size') else None,
                                                        indexed=colattr.get('indexed'),
                                                        unique=colattr.get('unique')))
                    columns_bag.setItem(colname,b)
                    if colattr.get('relate_to'):
                        b.setItem('_relation',Bag(dict(relation=colattr['relate_to'].lower(),onDelete='raise',meta_thmode='dialog')))
                table_data['caption_field'] = caption_field
                self.makeOneTable(os.path.join(modelpath,'%s.py' %tablename),table_data=table_data)


    @public_method
    def extdb_getPreviewData(self,table=None,connection_params=None,**kwargs):
        sourcedb = self.extdb_getSourceDb(connection_params)
        sourcedb.model.build()
        result = Bag()
        tbl = sourcedb.table(table)
        cols = ','.join(['$%s' %c.name for c in list(sourcedb.table(table).columns.values()) if c.name!='_multikey'])
        f = tbl.query(columns=cols,addPkeyColumn=False,limit=200).fetch()
        sourcedb.closeConnection()
        for i,r in enumerate(f):
            result['r_%s' %i] = Bag(r)
        return result

    def extdb_getSourceDb(self,connection_params=None):
        dbname=connection_params['dbname'] or connection_params['filename']
        if connection_params['implementation']!='sqlite':
            connection_params['host'] = connection_params['host'] or 'localhost'
            connection_params['user'] = connection_params['user']
            connection_params['password'] = connection_params['password']
            connection_params['port'] = connection_params['port']
        externaldb = GnrSqlDb(implementation=connection_params['implementation'],
                            dbname=dbname,
                            host=connection_params['host'],user=connection_params['user'],
                            password = connection_params['password'],
                            port=connection_params['port'])
        externaldb.importModelFromDb()
        return externaldb

    @public_method
    def extdb_getDbStructure(self,connection_params=None,connection_options=None,project=None,package=None):
        externaldb = self.extdb_getSourceDb(connection_params)
        avoidImported = connection_options['avoidImported']
        avoidNoPkey = connection_options['avoidNoPkey']
        avoidEmpty = connection_options['avoidEmpty']
        if avoidEmpty:
            externaldb.model.build()
        #externaldb.table('targetcross.anl_budget').query().count()

        existing_tables = []
        if project and package:
            p = PathResolver()
            project_path = p.project_name_to_path(project)
            modelpath = os.path.join(project_path,'packages',package,'model')
            if os.path.isdir(modelpath):
                existing_tables = [os.path.splitext(r)[0] for r in [r for r in os.listdir(modelpath) if r.endswith('.py')]]
        src = externaldb.model.src
        relations_dict = defaultdict(dict)
        for r in externaldb.adapter.relations():
            relations_dict[(r[1],r[2])][r[3][0]] = dict(reltable=(r[5],r[6]),pkey=r[7][0])
        result = Bag()
        for pkg in list(src['packages'].keys()):
            pkgval = Bag()
            result.setItem(pkg, pkgval,name=pkg,checked=False)
            tables = src['packages'][pkg]['tables']
            if not tables:
                continue
            tables.sort('#k')
            for table,tblattr,tblval in tables.digest('#k,#a,#v'):
                fkeys = relations_dict[(pkg,table)]
                tblattr = dict(tblattr)
                imported_table = table.lower() in existing_tables
                if imported_table and avoidImported:
                    continue
                if avoidNoPkey and not tblattr.get('pkey'):
                    continue
                if avoidEmpty:
                    if not externaldb.table('%s.%s' %(pkg,table)).query().count():
                        continue
                tblattr['checked'] = 'disabled:on' if imported_table else False
                tblattr['name'] = table
                tableval = Bag()
                pkgval.setItem(table,tableval,**tblattr)
                for column,colattr,colval in tblval['columns'].digest('#k,#a,#v'):
                    cv = dict(colattr)
                    for t,v in list(tblattr.items()):
                        cv['table_%s' %t] = v
                    #cv['checked'] = False
                    cv['name'] = column
                    fkey = fkeys.get(column)
                    if colval:
                        relnode = colval.getNode('relation')
                        if relnode:
                            cv['relate_to'] = relnode.attr['related_column']
                    if fkey and not cv.get('relate_to'):
                        cv['relate_to'] = '%s.%s' %(fkey['reltable'][1],fkey['pkey'])
                    tableval.setItem(column,None,**cv)
                if tblval['indexes']:
                    for column,unique in tblval['indexes'].digest('#a.columns,#a.unique'):
                        n = tableval.getNode(column)
                        if n:
                            n.attr['is_pkey'] = column == tblattr.get('pkey')
                            n.attr['indexed'] = True
                            n.attr['unique'] = boolean(unique)
        return result

    def extdb_importFromExtDb(self,connection_params=None,instance=None,package=None):
        app = GnrApp(instance)
        destdb = app.db
        if destdb.model.check():
            destdb.model.applyModelChanges()
        if connection_params and (connection_params['dbname'] or connection_params['filename']):
            sourcedb = self.extdb_getSourceDb(connection_params)
            sourcedb.model.build()
            for table in list(destdb.tablesMasterIndex()[package].keys()):
                self.extdb_importTable(sourcedb,destdb,package,table)
                destdb.commit()
            sourcedb.closeConnection()
            destdb.closeConnection()

    def extdb_importTable(self,sourcedb,destdb,package,table):
        desttable = destdb.table('%s.%s' %(package,table))
        if desttable.query().count():
            return
        sourcetable = sourcedb.table(desttable.attributes['legacy_name'])
        columns = []
        for k,c in list(desttable.columns.items()):
            legacy_name = c.attributes.get('legacy_name')
            if legacy_name:
                columns.append(" $%s AS %s " %(legacy_name,k))
        columns = ', '.join(columns)
        f = sourcetable.query(columns=columns,addPkeyColumn=False).fetch()
        progressDetail = dict(status='Importing records',total=len(f),current=0)
        t0 = time()
        for i,r in enumerate(f):
            desttable.insert(r)
            if time()-t0>1:
                t0 = time()
                progressDetail['current'] = i
                status = r""" %(status)s <progress style='width:12em' max='%(total)s' value='%(current)s'></progress>""" %progressDetail
                self.clientPublish('update_import_status',status=status,table=table)
        self.clientPublish('update_import_status',status='<b>Imported</b>',table=table)
