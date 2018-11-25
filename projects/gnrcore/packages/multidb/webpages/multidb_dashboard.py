#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#  Created by Francesco Porcari
#
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrbag import Bag
from gnrpkg.multidb.utility import getSyncTables
import os


class GnrCustomWebPage(object):
    py_requires = 'public:Public,th/th:TableHandler,th/th_dynamic:DynamicTableHandler'
    auth_main='admin'
    pageOptions={'openMenu':False,'enableZoom':False}


    def main(self, root,**kwargs):
        frame = root.rootContentPane(datapath='main',design='sidebar',title='!!Multidb dashboard')   
        frame = frame.center.framePane()      
        bc = frame.center.borderContainer()

        bc.css("._common_d11 .onlymain .dojoxGrid-cell",
                "background: rgba(223, 255, 147, 0.2) !important;")
        bc.css("._common_d11 .onlystore .dojoxGrid-cell",
                "background: rgba(255, 227, 60, 0.3) !important;")
        bc.css("._common_d11 .missing .dojoxGrid-cell",
                "background: rgba(74, 242, 161, 0.3) !important;")
        bc.css("._common_d11 .diff",
                "color:red !important;")
        bc.css("._common_d11 .nosub .dojoxGrid-cell",
                "background: rgba(255, 166, 74, 0.3) !important;")
        bc.css(".difftable","border-collapse:collapse;")
        bc.css(".difftable th","background:gray;color:white;border:1px solid silver;padding:5px;")
        bc.css(".difftable td","border:1px solid silver; padding:5px;")

        bar = frame.top.slotBar('2,fbselects,*')
        fb = bar.fbselects.formbuilder(cols=4,border_spacing='2px')
        fb.filteringSelect(value='^.dbstore',lbl='!!Db Store',values=','.join(sorted(self.db.stores_handler.dbstores.keys())))
        fb.remoteSelect(value='^.sync_table',lbl='!!Table',selected_multidb='.multidb_mode',
                        method=self.getSyncTables,
                        auxColumns='multidb',hasDownArrow=True)
        fb.dataRpc('main.subscribed_pkeys',self.setSyncInfoInStore,insync_table='^.sync_table',insync_store='^.dbstore',
                    _if='insync_table&&insync_store',_fired='^.get_sync_info',
                    _onResult="FIRE main.load_th")
        fb.button('!!Total sync',
                    hidden='^.multidb_mode?=#v!="complete"',
                    fire='.sync_again')
        fb.checkbox(value='^.show_always',label='Show always')
        fb.dataRpc('dummy',self.syncAgain,insync_table='=.sync_table',
                    insync_store='=.dbstore',
                    _fired='^.sync_again',
                    _if='insync_table&&insync_store')

        left = bc.roundedGroupFrame(title='Main store',region='left',width='50%')
        leftbc = left.center.borderContainer()
        self.troublesTree(leftbc.framePane(region='bottom',height='200px',closable='close',
                                            border_top='1px solid silver',splitter=True))
        center = bc.roundedGroupFrame(title='Current dbstore',region='center',margin='2px')
        centerbc = center.center.borderContainer()
        frame.dataController("""if(_reason=='child' && _node.label!='_protectionStatus'){
                var mainstruct_copy = mainstruct.deepCopy();
                mainstruct_copy.popNode('#0.#0._protectionStatus');
                SET main.dbext.th.view.grid.struct = mainstruct_copy;
            }""",
            mainstruct='^main.dbroot.th.view.grid.struct',_delay=1)

        frame.dataController("""SET main.dbext.th.view.grid.sorted = sorted;""",
            sorted='^main.dbroot.th.view.grid.sorted',_delay=1,_userChanges=True)

        leftbc.contentPane(region='center').dynamicTableHandler(table='=main.sync_table',datapath='.dbroot',
                                 th_wdg='plain',
                                 th_view_store_applymethod='checksync_mainstore',
                                th_viewResource='View', 
                                th_configurable=True,
                                th_condition='==multidb_mode=="complete"?null:"$pkey IN :subscribed_pkeys"',
                                th_view_store_multidb_mode ='=main.multidb_mode',
                                th_view_store_apply_showalways='^main.show_always',
                                th_condition_subscribed_pkeys='=main.subscribed_pkeys',
                                nodeId='rootStore',_fired='^main.load_th')

        centerbc.contentPane(region='center').dynamicTableHandler(table='=main.sync_table',datapath='.dbext',
                                th_wdg='plain',
                                th_viewResource='View',
                                 th_view_store_applymethod='checksync_extstore',
                                th_view_store_currentDbstore='=main.dbstore',
                                th_view_store_forced_dbstore=True,
                                
                                th_view_store_apply_showalways='^main.show_always',

                                th_view_grid_selected__differences='main.selectedrow.differences',
                                th_view_grid_selected__linked_records='main.selectedrow.linked_records',
                                th_delrow=True,
                                th_dbstore='=main.dbstore',
                                nodeId='syncStore',
                                #th_configurable=False,
                                _fired='^main.load_th')
        bottom = centerbc.contentPane(region='bottom',height='200px',closable='close',border_top='1px solid silver')
        bottom.div('^main.selectedrow.differences',margin='5px',
                    border='2px solid silver',rounded=6,padding='10px')
        bottom.div('^main.selectedrow.linked_records',margin='5px',
                    border='2px solid silver',rounded=6,padding='10px')


    def troublesTree(self,frame):
        bar = frame.top.slotToolbar('2,packagesButtons,*,checksync,5',height='22px')
        bar.checksync.slotButton('Check',action='FIRE .checkDbstore')
        bar.packagesButtons.multiButton(value='^.selectedPackage',values='^.currpackages')
        rpc = frame.dataRpc('.multidbLog',self.getMultidbLog,
                            currentstore='^main.dbstore',
                            docheck='^.checkDbstore',
                            _onCalling="""if(docheck){
                                genro.lockScreen(true,'checkstore');
                            }""",
                            _if='currentstore',_else='null')
        rpc.addCallback("""
            genro.lockScreen(false,'checkstore')
            SET .currpackages = result.keys().join(',');
            return result;
            """)
        bar.dataFormula('.packageErrors',"multidbLog.getItem(selectedPackage).deepCopy();",
                         multidbLog='=.multidbLog',selectedPackage='^.selectedPackage')
        frame.tree(storepath='.packageErrors')

    @public_method
    def getMultidbLog(self,currentstore=None,docheck=None):
        f = self.site.getStaticPath('site:data','multidb_logs')
        if docheck:
            self.db.package('multidb').checkFullSyncTables(errorlog_folder=f,
                                            dbstores=currentstore)
        p = os.path.join(f,'%s.xml' %currentstore)
        if os.path.exists(p):
            return Bag(p)
        return Bag()

    @public_method
    def checksync_mainstore(self,selection=None,showalways=None,**kwargs):
        self._checksync(selection,'main',showalways=showalways)

    @public_method
    def checksync_extstore(self,selection=None,showalways=None,**kwargs):
        self._checksync(selection,'ext',showalways=showalways)


    def _checksync(self,selection,storemode,showalways=None):
        currentSync = self.pageStore().getItem('currentSync')
        dbtable = selection.dbtable
        def cb(row):
            sync_value = currentSync.get(row['pkey'])
            if not sync_value:
                sync_value = 'missing'
            if sync_value == 'equal':
                return dict() if showalways else None
            if storemode=='main':
                return dict()
            differences = None
            if '|' in sync_value:
                sync_value,differences = sync_value.split('|')
            return dict(_customClasses=sync_value,_differences=differences,
                            _linked_records=self.checkRelations(dbtable,row['pkey']))
        selection.apply(cb)
        selection.sort('pkey')

    @public_method
    def getSyncTables(self,_querystring=None,_id=None,**kwargs):
        result = Bag()
        if _id:
            tableobj = self.db.table(_id)
            tblattr = tableobj.attributes
            caption = tableobj.fullname
            result.setItem(_id.replace('.','_'),None,caption=caption,
                        multidb='complete' if tblattr['multidb']=='*' else 'partial',
                        tablename=caption,
                        _pkey=caption)
            return result,dict(columns='tablename,multidb',headers='Table,Multidb')
        if _querystring:
            _querystring = _querystring.replace('*','')
        result = getSyncTables(self.db,_querystring)
        return result,dict(columns='tablename,multidb',headers='Table,Multidb')

    @public_method
    def setSyncInfoInStore(self,insync_table=None,insync_store=None):
        tbl = self.db.table(insync_table)
        pkey = tbl.pkey
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False)
        if tbl.attributes.get('hierarchical'):
            queryargs.setdefault('order_by','$hierarchical_pkey')

        with self.db.tempEnv(storename=insync_store):
            store_f = tbl.query(**queryargs).fetch()

        where = None
        syncpkeys = []
        columns = '*'
        main_f = dict()
        if tbl.attributes['multidb'] is True:
            where = '$%s in :syncpkeys' %pkey
            columns = '*,$__multidb_subscribed'
            syncpkeys = [r[pkey] for r in store_f]
        with self.db.tempEnv(target_store=insync_store):
            main_f = tbl.query(where=where,columns=columns,
                            syncpkeys=syncpkeys, 
                            **queryargs).fetchAsDict()
        result = dict()
        for r in store_f:
            r = dict(r)
            r.pop('__ins_ts',None)
            r.pop('__mod_ts',None)
            r.pop('__version',None)
            r.pop('__del_ts',None)
            r.pop('__moved_related',None)

            mr = main_f.pop(r[pkey],None)
            if mr:
                mr = dict(mr)
                mr.pop('__ins_ts',None)
                mr.pop('__mod_ts',None)
                mr.pop('__version',None)
                mr.pop('__del_ts',None)
                mr.pop('__moved_related',None)
                if '__multidb_subscribed' in mr:
                    __multidb_subscribed = mr.pop('__multidb_subscribed') or mr.get('__multidb_default_subscribed')
                else:
                    __multidb_subscribed = '*'
                if mr==r:
                    result[r[pkey]] = 'equal'
                else:
                    difflist = ["<tr><th>Table</th><th>Main val</th><th>Ext val</th></tr>"]
                    for k,v in r.items():
                        if v!=mr[k]:
                            difflist.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' %(k,mr[k],v))
                    result[r[pkey]] = 'diff|<table class="difftable"><tbody>%s</tbody></table>' %''.join(difflist)
                if not __multidb_subscribed:
                    result[r[pkey]] = 'nosub %s' %result[r[pkey]]
            else:
                result[r[pkey]] = 'onlystore'
        for k in main_f.keys():
            result[k] = 'onlymain'
        with self.pageStore() as store:
            store.setItem('currentSync',result)
        return syncpkeys

    @public_method
    def syncAgain(self,insync_table=None,insync_store=None):
        tbl = self.db.table(insync_table)
        with self.db.tempEnv(_multidbSync=True):
            tbl.copyToDbstore(dbstore=insync_store,empty_before=True)
            self.db.commit()


    def checkRelations(self,tblobj,pkey):
        result = tblobj.currentRelations(pkey)
        if not result:
            return None
        return '<br/>'.join(['%s:%s' %(tbl,count) for tbl,count in result.digest('#v.linktbl,#v.count')])

