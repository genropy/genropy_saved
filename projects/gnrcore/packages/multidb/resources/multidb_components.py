# -*- coding: utf-8 -*-
#
from gnr.web.gnrbaseclasses import BaseComponent

from gnr.core.gnrdecorator import public_method
from gnrpkg.multidb.utility import getSyncTables
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

ALL_RECORDS_KWARGS = dict(excludeLogicalDeleted=False,
                     excludeDraft=False,
                     subtable='*',
                     bagFields=True)

class MultidbCheckUtils(BaseComponent):
    py_requires='th/th_dynamic:DynamicTableHandler'
    @struct_method
    def mdb_checkSyncDataTab(self,parent,selectedPagePath=None,**kwargs):
        selectedPagePath = selectedPagePath or '#FORM.selectedPage'
        bc =parent.borderContainer(pageName="checkSyncData",**kwargs)
        bc.contentPane(region='center').bagGrid(frameCode='checkSyncData',struct=self.mdb_checkSyncData_struct,
                                                storepath='#FORM.checkSyncDataStore',pbl_classes=True,
                                                title='Controllo',margin='2px',
                                                grid_selected_tbl='#FORM.mdb_checkTbl',
                                                datapath='#FORM.checkSyncDataFrame',addrow=False,delrow=False,
                                                datamode='attr')
        bc.dataRpc('#FORM.checkSyncDataStore',self.mdb_checkSyncTables,
                    _lockScreen=dict(thermo=True),_fired='^#FORM.mdb_doCheck',
                    _selectedPage='^%s' %selectedPagePath,_delay=100,
                    currdbstore='^#FORM.record.dbstore',_if='_selectedPage=="checkSyncData"')
    
        self.mdb_thMatchData(bc.borderContainer(region='bottom',height='300px',splitter=True))
        
    def mdb_thMatchData(self,bc):
        masterframe = bc.roundedGroupFrame(title='Primario',region='left',width='50%')
        self.mixinComponent('th/th_dynamic:DynamicTableHandler')
        masterframe.dynamicTableHandler(table='^#FORM.mdb_checkTbl',datapath='#FORM.dbroot',
                                 th_wdg='plain',
                                 #th_view_store_applymethod='checksync_mainstore',
                                th_viewResource='View', 
                                th_configurable=True,
                                #th_view_store_apply_showalways='^main.show_always',
                                nodeId='rootStore')
        bar = masterframe.top.bar.replaceSlots('#','#,touchrec')
        bar.touchrec.slotButton('!!Align',fire='#FORM.mdb_alignCurrent')
        bar.dataRpc(None,self.mdb_reTouchAllSync,_fired='^#FORM.mdb_alignCurrent',tbl='=#FORM.mdb_checkTbl',
                    _onResult='FIRE #FORM.mdb_doCheck',dbstore='=#FORM.record.dbstore',_lockScreen=True)

        slaveframe = bc.roundedGroupFrame(title='!!Slave',region='center')
        slaveframe.dynamicTableHandler(table='^#FORM.mdb_checkTbl',datapath='#FORM.mdb_dbext',
                                th_wdg='plain',
                                th_viewResource='View',
                                #th_view_store_applymethod='checksync_extstore',
                                th_view_store_currentDbstore='=#FORM.record.dbstore',
                                th_view_store_forced_dbstore=True,
                                #th_view_store_apply_showalways='^main.show_always',
                                th_delrow=True,
                                th_view_store_dbenv_avoid_trigger_multidb='*',
                                th_view_store_dbenv_avoid__multidbSync=True,
                                th_view_grid_dropTarget_row='dbrecords',
                                th_view_grid_onDrop_dbrecords="""
                                    if(data && data.table==this.attr.table && data.pkeys.length==1){
                                        var drow = this.widget.rowByIndex(dropInfo.row);
                                        genro.publish('mdb_changeSelectedPkey',
                                                        {new_pkey:data.pkeys[0],old_pkey:drow._pkey})
                                    }
                                """,
                                th_configurable=True,
                                th_dbstore='=#FORM.record.dbstore',
                                nodeId='syncStore')
        bar = slaveframe.top.bar.replaceSlots('#','#,moveInMaster')
        bar.moveInMaster.slotButton('Add to master',fire='#FORM.mdb_addToMaster')
        bar.dataRpc(None,self.mdb_addToMaster,_fired='^#FORM.mdb_addToMaster',tbl='=#FORM.mdb_checkTbl',
                    selectedPkeys='=#FORM.mdb_dbext.th.view.grid.currentSelectedPkeys',contabilita='=#FORM.record.dbstore',
                    _onResult='FIRE #FORM.mdb_doCheck')
        bar.dataRpc(None,self.mdb_changeSelectedPkey,subscribe_mdb_changeSelectedPkey=True,tbl='=#FORM.mdb_checkTbl',
                    contabilita='=#FORM.record.dbstore',_onResult='FIRE #FORM.mdb_doCheck')


    #def th_filterset_situazione(self):
    #    return [dict(code='tutti',caption='Tutti'),
    #            dict(code='voto_si',caption=u'Sì',cb='voto_si'),
    #            dict(code='voto_no',caption=u'No',cb='voto_no',isDefault=True),
    #            dict(code='voto_ast',caption=u'Astenuti',cb='voto_astenuto'),
    #            dict(code='voto_ass',caption=u'Assenti',cb='!(voto_si || voto_no || voto_astenuto)')
    #            ]

    
    def mdb_checkSyncData_struct(self,struct):
        r=struct.view().rows()
        r.cell('pkg',width='10em',name='Package')
        r.cell('tbl',width='20em',name='Table')
        r.cell('count_master',width='6em',name='Cnt.Master',dtype='L')
        r.cell('count_slave',width='6em',name='Cnt.Slave',dtype='L')
        r.cell('missing_slave_count',width='6em',name='Cnt.Missing',dtype='L')
        r.cell('missing_master_count',width='15em',name='Cnt.MissMaster',dtype='L')
        r.cell('diff_master_count',width='5em',name='Cnt.Diff',dtype='L')

        #r.cell('diff_master',width='30em',name='Diff.Master')

    @public_method
    def mdb_reTouchAllSync(self,tbl=None,dbstore=None,**kwargs):
        tblobj = self.db.table(tbl)
        tblsub = self.db.table('multidb.subscription')
        f = tblobj.query(**ALL_RECORDS_KWARGS).fetch()
        for r in f:
            tblsub.syncStore(event='U',storename=dbstore,tblobj=tblobj,pkey=r['pkey'],
                            master_record=r,master_old_record=dict(r),mergeUpdate=False)
        self.db.commit()

    @public_method
    def mdb_addToMaster(self,tbl=None,selectedPkeys=None,contabilita=None,**kwargs):
        tblobj = self.db.table(tbl)
        with self.db.tempEnv(storename=contabilita):
            slave_f = tblobj.query(addPkeyColumn=False).fetch()
        master_f = tblobj.query(addPkeyColumn=False).fetchAsDict(tblobj.pkey)
        for r in slave_f:
            if r[tblobj.pkey] not in master_f:
                tblobj.insert(dict(r))
        self.db.commit()

    @public_method
    def mdb_changeSelectedPkey(self,tbl=None,old_pkey=None,new_pkey=None,contabilita=None,**kwargs):
        with self.db.tempEnv(storename=contabilita):
            self.db.table(tbl).changePrimaryKeyValue(pkey=old_pkey,newpkey=new_pkey)
            self.db.commit()

    @public_method
    def mdb_checkSyncTables(self,currdbstore=None):
        result = Bag()
        allsync = getSyncTables(self.db,multidbMode='complete').digest('#a.tablename')
        for tbl in self.utils.quickThermo(allsync,maxidx=len(allsync),labelcb=lambda t: t,title='Check sync'):
            if tbl=='erpy_coge.abi_cab':
                continue
            tblobj = self.db.table(tbl)
            resrow = {'pkg':tbl.split('.')[0],'tbl':tbl}
            master_f = tblobj.query(**ALL_RECORDS_KWARGS).fetchAsDict(tblobj.pkey)
            resrow['count_master'] = len(master_f)
            with self.db.tempEnv(storename=currdbstore):
                slave_f = tblobj.query(order_by='$%s' %tblobj.pkey,**ALL_RECORDS_KWARGS).fetch()
            resrow['count_slave'] = len(slave_f)
            missing_master = []
            diff_master = []
            for slave_row in slave_f:
                slave_pkey = slave_row[tblobj.pkey]
                master_row = master_f.pop(slave_pkey,None)
                if not master_row:
                    missing_master.append(slave_pkey)
                else:
                    differences = []
                    for k,v in slave_row.items():
                        if k in ('__ins_ts','__mod_ts','__ins_user','__mod_user'):
                            continue
                        if v !=master_row.get(k):
                            differences.append('<b>%s:</b>%s ≠ <span style="color:red">%s</span>' %(k,v,master_row.get(k)))
                    if differences:
                        diff_master.append(slave_pkey)
            
            resrow['missing_master_count'] = len(missing_master)
            resrow['missing_master_pkeys'] = missing_master
            resrow['diff_master_count'] = len(diff_master)
            resrow['diff_master_pkeys'] = diff_master
            resrow['missing_slave_count'] = len(master_f)
            resrow['missing_slave_pkeys'] = master_f.keys()

            resrow['_pkey'] = tbl
            if not (resrow['missing_master_count'] or resrow['diff_master_count'] or resrow['missing_slave_count']):
                continue

            result.setItem(tbl.replace('.','_'),None,**resrow)
        return result