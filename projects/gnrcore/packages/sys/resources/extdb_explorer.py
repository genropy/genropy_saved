# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

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
    py_requires='table_module_editor:TableModuleWriter'

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
                    _fired='^.addToModel',
                    _onCalling="""
                    var columns = new gnr.GnrBag();
                    kwargs['data'].walk(function(n){
                        if((n.attr.checked+'').startsWith('disabled')){
                            return;
                        }
                        if (n.attr.checked && n.attr.tag=='column'){
                            var table_data = new gnr.GnrBag();
                            columns.setItem(n.attr.table_fullname+'.'+name,null,n.attr)
                        }
                    });
                    kwargs['data'] = columns
                    """,
                    _onResult="""
                    genro.publish('tableModuleWritten');
                    genro.publish('closeDbConnectionDialog');""")
        bar = frame.bottom.slotBar('*,cancel,confirm,5',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton("Cancel",action="genro.publish('closeDbConnectionDialog');",dlg=dialog.js_widget)
        bar.confirm.div(hidden='^.instance?=!#v').button('Add to model',action="""
            FIRE .addToModel;
        """)


    def extdb_contentFrame(self,frame):
        top = frame.top.slotToolbar('2,fbconnection,5,connecbutton,*,2',height='22px')
        bc = frame.center.borderContainer()
        fb = top.fbconnection.formbuilder(cols=7,border_spacing='3px',datapath='.connection_params')
        fb.filteringSelect(value='^.implementation',values='postgres,sqlite,mysql,mssql',
                            lbl='Implementation',width='7em')
        fb.textbox(value='^.dbname',lbl='Dbname',width='8em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.host',lbl='Host',width='8em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.port',lbl='Port',width='5em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.user',lbl='User',width='7em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.password',lbl='Password',width='5em',hidden='^.implementation?=#v=="sqlite"')
        fb.textbox(value='^.filename',lbl='Filename',width='50em',hidden='^.implementation?=#v!="sqlite"')
        top.connecbutton.slotButton('Connect',fire='.connect')
        top.dataRpc('.data',
                    self.extdb_getDbStructure,project='=.project',package='=.package',
                    connection_params='=.connection_params',
                    _fired='^.connect',
                    _lockScreen=True)
        center = bc.borderContainer(region='center')
        left = center.contentPane(region='left',width='300px',padding='10px',overflow='auto',splitter=True)
        left.tree(storepath='.data', persist=False,
                    inspect='shift', labelAttribute='name',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
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
        instance_path = os.path.join(p.instance_name_to_path(instance),'instanceconfig.xml')
        instance_bag = Bag(instance_path)
        dbname = connection_params['dbname'] or connection_params['filename']
        legacydb,ext = os.path.splitext(os.path.basename(dbname))
        parsdict = dict()
        for k,v in connection_params.items():
            if v not in ('',None):
                parsdict[k] = v
        instance_bag.setItem('legacy_db.%s' %legacydb,None,**parsdict)
        instance_bag.toXml(instance_path,typevalue=False,pretty=True)
        for srcpkg,tables in data.items():
            for tablename,columns in tables.items():
                firstColAttr = columns.getAttr('#0')
                tablename = tablename.lower()
                table_data = Bag()
                table_data['name'] = tablename
                table_data['legacy_name'] = firstColAttr.get('table_fullname')
                table_data['legacy_db'] = legacydb
                table_data['pkey'] = firstColAttr.get('table_pkey').lower()
                columns_bag = Bag()
                table_data['_columns'] = columns_bag
                for colattr in columns.digest('#a'):
                    legacy_name = colattr['name']
                    if legacy_name=='_multikey':
                        legacy_name = None
                    colname = colattr['name'].lower()
                    b = Bag(dict(name=colname,legacy_name=legacy_name,
                                                        name_long=None,dtype=colattr.get('dtype'),
                                                        size=colattr.get('size'),indexed=colattr.get('indexed'),
                                                        unique=colattr.get('unique')))
                    columns_bag.setItem(colname,b)
                    if colattr.get('relate_to'):
                        b.setItem('_relation',Bag(dict(relation=colattr['relate_to'].lower(),onDelete='raise')))
                self.makeOneTable(os.path.join(modelpath,'%s.py' %tablename),table_data=table_data)


    @public_method
    def extdb_getPreviewData(self,table=None,connection_params=None,**kwargs):
        sourcedb = self.extdb_getSourceDb(connection_params)
        sourcedb.model.build()
        result = Bag()
        tbl = sourcedb.table(table)
        cols = ','.join(['$%s' %c.name for c in sourcedb.table(table).columns.values() if c.name!='_multikey'])
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
                            password = connection_params['password'])
        externaldb.importModelFromDb()
        return externaldb

    @public_method
    def extdb_getDbStructure(self,connection_params=None,project=None,package=None):
        externaldb = self.extdb_getSourceDb(connection_params)
        existing_tables = []
        if project and package:
            p = PathResolver()
            project_path = p.project_name_to_path(project)
            modelpath = os.path.join(project_path,'packages',package,'model')
            if os.path.isdir(modelpath):
                existing_tables = map(lambda r: os.path.splitext(r)[0], filter(lambda r: r.endswith('.py'), os.listdir(modelpath)))
        src = externaldb.model.src
        result = Bag()
        for pkg in src['packages'].keys():
            pkgval = Bag()
            result.setItem(pkg, pkgval,name=pkg,checked=False)
            tables = src['packages'][pkg]['tables']
            if not tables:
                continue
            for table,tblattr,tblval in tables.digest('#k,#a,#v'):
                tblattr = dict(tblattr)
                tblattr['checked'] = 'disabled:on' if table.lower() in existing_tables else False
                tblattr['name'] = table
                tableval = Bag()
                pkgval.setItem(table,tableval,**tblattr)
                for column,colattr,colval in tblval['columns'].digest('#k,#a,#v'):
                    cv = dict(colattr)
                    for t,v in tblattr.items():
                        cv['table_%s' %t] = v
                    #cv['checked'] = False
                    cv['name'] = column
                    if colval:
                        relnode = colval.getNode('relation')
                        cv['relate_to'] = relnode.attr['related_column']
                    tableval.setItem(column,None,**cv)
                if tblval['indexes']:
                    for column,unique in tblval['indexes'].digest('#a.columns,#a.unique'):
                        n = tableval.getNode(column)
                        if n:
                            n.attr['is_pkey'] = column == tblattr['pkey']
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
            for table in destdb.tablesMasterIndex()[package].keys():
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
        for k,c in desttable.columns.items():
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
