# encoding: utf-8
import pytz
import datetime
from gnr.core.gnrlang import GnrException
from gnr.app.gnrdbo import GnrDboTable


class TimeSheetTable(GnrDboTable):
    def use_dbstores(self, **kwargs):
        return self.db.table(tblname=self.fullname[0:-5]).use_dbstores()

    def config_db(self,pkg):
        tblname = self._tblname
        tbl = pkg.table(tblname,pkey='id')
        mastertbl = f"{pkg.parentNode.label}.{tblname.replace('_tmsh','')}"
        pkgname,mastertblname = mastertbl.split('.')
        tblname = f'{mastertblname}_tmsh'
        assert tbl.parentNode.label == tblname,'table name must be %s' %tblname
        model = self.db.model
        mastertbl =  model.src[f'packages.{pkgname}.tables.{mastertblname}']
        mastertbl.attributes['tmsh_table'] = '{pkgname}.{tblname}'\
                                            .format(pkgname=pkgname,tblname=tblname)
        mastertbl_name_long = mastertbl.attributes.get('name_long')      
        tblattr =  tbl.attributes 
        tblattr.setdefault('caption_field','description')
        tblattr.setdefault('rowcaption','$description')
        tblattr.setdefault('name_long',f'{mastertbl_name_long} Time allocation')
        tblattr.setdefault('name_plural',f'{mastertbl_name_long} Time allocations')
        self.sysFields(tbl,id=True, ins=False, upd=False)
        tbl.column('id',size='22',group='_',name_long='Id')
        maintable_pkey = mastertbl.attributes.get("pkey")
        maintable_pkey_attr = mastertbl.getAttr(f'columns.{maintable_pkey}')
        tbl.column('resource_id',size=maintable_pkey_attr.get('size'),
                        dtype=maintable_pkey_attr.get('dtype'),
                        group='*',name_long=mastertblname
                    ).relation(f'{pkgname}.{mastertblname}.{maintable_pkey}', 
                    mode='foreignkey', onDelete_sql='cascade',onDelete='cascade', relation_name='tmsh_items',
                    one_group='_',many_group='_',deferred=True)
        
        tbl.column('ts_start', dtype='DHZ', name_long='!![en]Start TS')
        tbl.column('ts_end', dtype='DHZ', name_long='!![en]End TS')
        self.onTableConfig(tbl)
        tbl.formulaColumn('ts_match',"""(CASE WHEN $ts_start IS NULL AND $ts_end IS NULL THEN TRUE
                                             WHEN $ts_start IS NULL 
                                                THEN $ts_end>=:env_dtend
                                             WHEN $ts_end IS NOT NULL
                                                THEN $ts_start<=:env_dtstart
                                             ELSE
                                                $ts_start>=:env_dtstart AND $ts_end<=:env_dtend
                                             END)
                                        """,
                                        dtype='B')
    def onTableConfig(self,tbl):
        "overridable"
        pass

    def formulaColumn_pluggedFields(self):
        desc_fields = []
        for colname,colobj in list(self.columns.items()):
            if colname.startswith('le_'):
                related_table = colobj.relatedTable()
                desc_fields.append(f"@{colname}.{related_table.attributes['caption_field']}")
        description_formula = f"COALESCE({','.join(desc_fields)})" if desc_fields else "'NOT PLUGGED'"
        return [dict(name='allocation_description',sql_formula=description_formula)]


    def getTsBoundaries(self,date_start=None,time_start=None,date_end=None,time_end=None,
                    delta_minutes=None,delta_hours=None,delta_days=None):
        now = datetime.datetime.now(pytz.utc)
        if not date_start:
            date_start = now.date()
        if not time_start:
            time_start = now.time()
        ts_start = datetime.datetime(date_start.year,date_start.month,date_start.day,
                                     time_start.hour,time_start.minute,tzinfo=pytz.utc)

        if delta_minutes or delta_hours or delta_days:
            ts_end = ts_start + datetime.timedelta(days=delta_days,hours=delta_hours,minutes=delta_minutes)

        else:
            if not date_end:
                date_end = date_start
            if not time_end:
                raise self.exception('business_logic',msg='Missing endtime')
            ts_end = datetime.datetime(date_end.year,date_end.month,date_end.day,
                                     time_end.hour,time_end.minute,tzinfo=pytz.utc)
        return ts_start, ts_end



    def _allocationFkeys(self):
        return [k for k in self.columns.keys() if k.startswith('le_')]

    def isAllocated(self,record):
        for field in self._allocationFkeys():
            if record[field]:
                return field
        return False


    def trigger_onInserted(self,record=None):
        if self.isAllocated(record):
            raise self.exception('business_logic',msg='You cannot insert an allocated timeslot')
            
    def trigger_onDeleted(self,record=None):
        if self.isAllocated(record):
            self.deAllocateResource(record)
            
    
    def trigger_onUpdated(self,record=None,old_record=None):

        if self.fieldsChanged(self._allocationFkeys(),record,old_record):
            if not self.isAllocated(old_record):
                self.makeHole(resource_id=record['resource_id'],ts_start=old_record['ts_start'],ts_end=record['ts_start'])
                self.makeHole(resource_id=record['resource_id'],ts_start=record['ts_end'],ts_end=old_record['ts_end'])
            else:
                self.delete(record)
                
        elif self.fieldsChanged('ts_start,ts_end',record, old_record):
            self.deAllocateResource(old_record)
            self.allocateResource(record)
    
        
    def deAllocateResource(self,record):
        ts_start,ts_end = record['ts_start'],record['ts_end']
        f = self.query(where='$resource_id=:rid AND ($ts_end=:slot_start OR $ts_start=:slot_end)',
                                slot_start=ts_start,slot_end=ts_end,rid=record['resource_id'],
                                order_by='COALESCE($ts_start,$ts_end)').fetch()
        prevrec,nextrec =f[0],f[1]
        if not self.isAllocated(prevrec):
            ts_start = prevrec['ts_start']
            self.raw_delete(prevrec)
        if not self.isAllocated(nextrec):
            ts_end = nextrec['ts_end']
            self.raw_delete(nextrec)
        self.makeHole(resource_id=record['resource_id'],ts_start=ts_start,ts_end=ts_end)        

    def makeHole(self,resource_id=None,ts_start=None,ts_end=None):
        if (ts_start is None and ts_end is None ) or (ts_start != ts_end):
            hole = self.newrecord(resource_id=resource_id,ts_start=ts_start,ts_end=ts_end)
            self.insert(hole)