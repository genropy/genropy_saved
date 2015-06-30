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

class ExtDbExplorer(BaseComponent):
    @struct_method
    def dbext_dbConnectionPalette(self,pane,label='Ext DB Connection',paletteCode='dbConnectionPalette',datapath=None):
        palette = pane.palettePane(paletteCode=paletteCode,title=label,
                        height='700px',width='900px',dockButton_label=label)
        bc = palette.borderContainer(datapath=datapath)
        top = bc.contentPane(region='top').slotToolbar('2,fbconnection,*,connecbutton')
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
        top.dataRpc('.connection_result',
                    self.extdb_getDbStructure,
                    connection_params='=.connection_params',
                    _fired='^.connect',
                    _lockScreen=True)
        center = bc.borderContainer(region='center')
        left = center.contentPane(region='left',width='300px',padding='10px',overflow='auto',splitter=True)
        left.tree(storepath='.connection_result', persist=False,
                    inspect='shift', labelAttribute='name',
                    _class='fieldsTree',
                    hideValues=True,
                    margin='6px',
                    onDrag=self.extdb_onDrag(),
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

    def extdb_onDrag(self):
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
    def extdb_getDbStructure(self,connection_params=None):
        externaldb = self.extdb_getSourceDb(connection_params)
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
