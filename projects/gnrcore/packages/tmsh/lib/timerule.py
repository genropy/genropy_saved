# encoding: utf-8
# import timerule_manager
try:
    from gnrpkg.tmsh.timerule_manager import TimeruleManager
except Exception:
    pass
from gnr.core.gnrdecorator import public_method

#interval = 5



class TimeRuleTable(object):
    def config_db(self, pkg):
        tblname = self._tblname
        tbl = pkg.table(tblname,pkey='id')
        mastertbl = "{}.{}".format(pkg.parentNode.label,tblname.replace('_tmru',''))
        pkgname,mastertblname = mastertbl.split('.')
        tblname = '{}_tmru'.format(mastertblname)
        assert tbl.parentNode.label == tblname,'table name must be %s' %tblname
        model = self.db.model
        mastertbl =  model.src['packages.{pkgname}.tables.{mastertblname}'.format(pkgname=pkgname,mastertblname=mastertblname)]
        mastertbl.attributes['tmru_table'] = '{pkgname}.{tblname}'\
                                            .format(pkgname=pkgname,tblname=tblname)
        mastertbl_name_long = mastertbl.attributes.get('name_long')      
        tblattr =  tbl.attributes 
        tblattr.setdefault('caption_field','timerule_description')
        tblattr.setdefault('rowcaption','$timerule_description')
        tblattr.setdefault('name_long','{mastertbl_name_long} Time allocation'.format(mastertbl_name_long=mastertbl_name_long))
        tblattr.setdefault('name_plural','{mastertbl_name_long} Time allocations'.format(mastertbl_name_long=mastertbl_name_long))
        structure_field = mastertbl.getAttr('structure_field')
        self.sysFields(tbl,counter='resource_id' if not structure_field else 'resource_id,structure_resource_id')
        tbl.column('id',size='22',group='_',name_long='Id')
        maintable_pkey = mastertbl.attributes.get("pkey")
        maintable_pkey_attr = mastertbl.getAttr('columns.{maintable_pkey}'.format(maintable_pkey=maintable_pkey))
        tbl.column('resource_id',size=maintable_pkey_attr.get('size'),
                        dtype=maintable_pkey_attr.get('dtype'),
                        group='*',name_long=mastertblname
                    ).relation('{pkgname}.{mastertblname}.{maintable_pkey}'.format(pkgname=pkgname,mastertblname=mastertblname,
                                                                            maintable_pkey=maintable_pkey), 
                    mode='foreignkey', onDelete_sql='cascade',onDelete='cascade', relation_name='tmsh_timerules',
                    one_group='_',many_group='_',deferred=True)            
        tbl.column('rule_order', 'L', name_long='!![en]Order')
        tbl.column('is_exception','B', name_long='!![en]Exception')
        tbl.column('on_su', 'B', name_long='!![en]Sunday')
        tbl.column('on_mo', 'B', name_long='!![en]Monday')
        tbl.column('on_tu', 'B', name_long='!![en]Tuesday')
        tbl.column('on_we', 'B', name_long='!![en]Wednesday')
        tbl.column('on_th', 'B', name_long='!![en]Thursday')
        tbl.column('on_fr', 'B', name_long='!![en]Friday')
        tbl.column('on_sa', 'B', name_long='!![en]Saturday')
        tbl.column('am_start_time', 'H', name_long='!![en]Start AM')
        tbl.column('am_end_time', 'H', name_long='!![en]End AM')
        tbl.column('pm_start_time', 'H', name_long='!![en]Start PM')
        tbl.column('pm_end_time', 'H', name_long='!![en]End PM')
        tbl.column('notes', name_long='!![en]Notes')
        tbl.column('deny', 'B', name_long='!![en]Deny rule')
        tbl.column('valid_from', dtype='D', name_long='!![en]Valid from')
        tbl.column('valid_to', dtype='D', name_long='!![en]Valid to')
        tbl.column('month_frequency', size=':2', name_long='!![en]Month frequency')
        tbl.formulaColumn('frequency_name', """CASE 
                                           WHEN #THIS.month_frequency ='1' THEN 'First'
                                           WHEN #THIS.month_frequency ='2' THEN 'Second'
                                           WHEN #THIS.month_frequency ='3' THEN 'Third'
                                           WHEN #THIS.month_frequency ='4' THEN 'Fourth'
                                           WHEN #THIS.month_frequency ='l' THEN 'Last'
                                           WHEN #THIS.month_frequency ='w2' THEN 'Every 2 weeks'
                                           WHEN #THIS.month_frequency ='w3' THEN 'Every 3 weeks'
                                           WHEN #THIS.month_frequency ='w4' THEN 'Every 4 weeks'
                                           ELSE 'Any'
                                           END""")
        tbl.formulaColumn('is_valid', """CASE 
                                          WHEN #THIS.valid_from IS NULL OR #THIS.valid_to IS NULL OR ((#THIS.valid_from <=:env_workdate) AND (#THIS.valid_to>:env_workdate)) THEN true 
                                          ELSE false END""", dbtype='B',name_long='!![en]Valid')
        tbl.formulaColumn('rule_type',"CASE WHEN #THIS.deny IS true THEN 'deny' ELSE 'normal' END", name_long='!![en]Priority code')
        tbl.formulaColumn('timerule_description','$id') #todo
        
    def trigger_onInserting(self, record_data):
        if record_data['is_exception']:
            record_data['valid_to'] = record_data['valid_from']
            weekday = ['mo','tu','we','th','fr','sa','su'][record_data['valid_from'].weekday()]
            record_data['on_%s' %weekday] = True

   #def generateSlots(self, doctor_id = None, start_date=None, end_date = None, showDenied=True,unifyLocation=None, interval=5):
   #    trManager = TimeruleManager(self.db, doctor_id=doctor_id, start_date=start_date, end_date = end_date, interval=interval)
   #    return trManager.generateSlots(showDenied=showDenied, unifyLocation=unifyLocation)
   #
   #def checkDay(self,doctor_id=None,day=None,newEvent=None):
   #    tm = TimeruleManager(db=self.db,start_date=day,end_date=day,doctor_id=doctor_id,newEvent=newEvent)
   #    tm.generateSlots(hideEvents=False, hideActivities=False)
   #    errors = {}
   #    if tm.wrongEvents:
   #        errors['wrongEvents'] = tm.wrongEvents.get(day)
   #    return errors

   #def checkNewEvent(self,newEvent=None,**kwargs):
   #    doctor_id = newEvent['doctor_id']
   #    event_id = newEvent.get('event_id')
   #    day = newEvent['evt_date']
   #    err = self.checkDay(doctor_id=doctor_id,day=day,newEvent=newEvent)
   #    return self._processTimeruleError(err,event_id=event_id)

   #def _processTimeruleError(self,err,activity_id=None,event_id=None):
   #    k = 'wrongActivities' if activity_id else 'wrongEvents'
   #    t = 'activity' if activity_id else 'event'
   #    pkey = activity_id or event_id
   #    pkeyname = 'id' if activity_id else 'event_id'
   #    if err and err.get(k):
   #        err = [x for x in err[k] if x[t].get(pkeyname) ==pkey]
   #        if not err:
   #            return
   #        else:
   #            err = err[0]['error_desc'].split(',')
   #            codes = []
   #            desc = []
   #            for e in err:
   #                c,d = e.split(':')
   #                codes.append(c)
   #                desc.append(d)
   #            return dict(codes=','.join(codes),desc=','.join(desc))
