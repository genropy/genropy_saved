# -*- coding: UTF-8 -*-

"""
timerule_manager.py
"""

from gnr.core.gnrbag import Bag
from datetime import datetime,date,time
from dateutil import rrule, relativedelta
from gnr.core.gnrlist import sortByItem
from gnr.core.gnrlang import uniquify, GnrException

class TimeruleInvalidEventException(GnrException):
    code = 'TR01'
    description = '!!Invalid event'
    caption = "!!The event %(rowcaption)s is invalid: %(msg)s"

class TimeruleInvalidRuleException(GnrException):
    code = 'TR02'
    description = '!!Invalid rule'
    caption = "!!The rule is invalid: %(msg)s"


class TimeruleManager(object):
    weekdays = ['mo','tu','we','th','fr','sa','su']
    
    def __init__(self, db, resource_table=None,resource_id=None,
                    start_date=None, end_date = None, 
                    interval='',newEvent=None):
        self.db = db
        self.tblobj = self.db.table(resource_table)
        self.resource_id = resource_id
        self.dates = None
        if isinstance(start_date,list):
            dates = sorted(start_date)
            start_date = dates[0]
            end_date = dates[-1]
            self.dates = dates
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval or 5
        self.scale_slot = 60/self.interval

        doctor_tbl = self.db.table('base.doctor')
        self.rules = self.getDoctorRules()
        self.weeklyRulesDict = self.prepareWeeklyRules(end_date)
        fmain_location = doctor_tbl.query(columns='$main_location_id',where='$id=:doctor_id',doctor_id=self.doctor_id).fetch()
        self.main_location_id = fmain_location[0]['main_location_id'] if fmain_location else '*noMainLocation*'
        self.eventsDictByDay = self.getEvents(newEvent=newEvent)
        self.clashes = {}
        self.wrongEvents = {}
        self.resultbag = Bag()
        self.currMonth = None

        
    def prepareWeeks(self, day):
        month=day.month
        self.currMonth = month
        self.monthWeekDays = dict([ (x,[])for x in range(7)])
        curr=1
        while True:
            try:
                currdate = date(day.year, month, curr)
                self.monthWeekDays[currdate.weekday()].append(curr)
                curr = curr+1
            except:
                return
                
    def prepareWeeklyRules(self, end_date=None):
        result = dict()
        for r in self.rules:
            r = dict(r)
            freq = r['month_frequency']
            if freq and freq.startswith('w'):
                n_weekly = int(freq[1:])
                wd = [getattr(rrule,k.upper()) for k in self.weekdays if (r.get('on_%s'%k))]
                result[r['id']] = set([day.date() for day in rrule.rrule(rrule.WEEKLY, interval=n_weekly, byweekday=wd, dtstart=r['valid_from'], until=end_date)])
        return result

    def generateSlots(self, unifyLocation= None, showDenied= None, hideEvents=None, hideActivities=None,checkEvents=None):
        dates = self.dates or self._dayIterator()
        for i,day in enumerate(dates):
            dayEvents = self.eventsDictByDay.get(day,None)
            if day.month != self.currMonth:
                self.prepareWeeks(day)
            dayProductionRules = self.dayRules(day, rule_type = 'normal')
            dayRulesWithSlots = self.dayRulesWithSlots(day, dayProductionRules)
            baseSet = set()
            baseSet = baseSet.union(*[ rs for r,rs in dayRulesWithSlots])
            result={}
            self.slotDict = dict()
            for s in baseSet:
                assigned=None
                slot_identifier= s.hour*self.scale_slot+s.minute/self.interval
                for r,rs in dayRulesWithSlots:
                    if s in rs:
                        assigned = self.slotDict.get(slot_identifier)
                        if not assigned or r['is_exception']:
                            if  r['doctor_id'] or (r['location_id'] == self.main_location_id) :
                                slot = dict(slot_start=s, room_id=r['room_id'],referrer_id=r['referrer_id'], slot_identifier= slot_identifier,notes=r['notes'])
                                if assigned:
                                    result[assigned[0]['location_id']].remove(assigned[1])
                                result.setdefault(r['location_id'],[]).append(slot)
                                self.slotDict[slot_identifier] = (r,slot)
                        else:
                            saved_assigned = assigned
                            assigned = assigned[0]
                            if r['location_id']!= assigned['location_id']:
                                self.clashes.setdefault( (r['location_id'],s),[assigned]).append(r)
                            elif r['referrer_id']!= assigned['referrer_id']:
                                self.clashes.setdefault( (r['referrer_id'],s),[assigned]).append(r)
                            else:
                                raise TimeruleInvalidRuleException(msg='Rule n%i should be revised. Slot already assigned in the same location' %r['_row_count'])
            if dayEvents:
                self.extraLocationEvents(day,dayEvents=dayEvents,slots=result)
            for location_id,slots in result.items():
                slots.sort(key=lambda x: x['slot_start'])
                dayDenyRules = self.dayRules(day, rule_type='deny')
                slots = self.applyDenyRules(dayDenyRules, slots, showDenied = showDenied)
                if dayEvents:
                    self.applyEvents(dayEvents=dayEvents, slots=slots, day=day, location_id=location_id, hideEvents=hideEvents)
                location_name = self.locationsDict[location_id].get('location_name') if location_id else ''
                unified_slots = self.unifySlots(slots,locationInfo=dict(location_id=location_id,location_name=location_name))
                if unifyLocation:
                    dayBagNode= self.resultbag.getNode('r_%i'%i)
                    if not dayBagNode:
                        self.resultbag.setItem('r_%i'%i,None,day = day,  weekday = self.weekdays[day.weekday()],slots=unified_slots)
                    else:
                        dayBagNode.attr['slots'].extend(unified_slots)
                else:   
                    location_id = location_id or 'nolocation'
                    location_bag = self.resultbag.getItem(location_id)    
                    if location_bag is None:
                        location_bag = Bag()
                        self.resultbag.setItem(location_id,location_bag,location_name=location_name) 
                    location_bag.setItem('r_%i' %i, None,
                                  slots=unified_slots,
                                  day = day,  weekday = self.weekdays[day.weekday()],
                                  location_id=location_id,location_name=location_name)

            if dayEvents:
                for ap in dayEvents:
                    self.wrongEvents.setdefault(day,[]).append(dict(event=ap,errors=[],error_desc='OS:Not allowed day'))
        return self.resultbag

    def extraLocationEvents(self,day,dayEvents=None,slots=None):
        for ev in dayEvents:
            location_id = ev['location_id']
            if location_id not in slots.keys():
                sg = self.slotMaker(day,ev['evt_start_time'],ev['evt_end_time'])
                for s in sg:
                    slot_identifier= s.hour*self.scale_slot+s.minute/self.interval
                    assigned = self.slotDict.get(slot_identifier)
                    if assigned:
                        assigned[1]['event'] = True
                    slot = dict(slot_start=s, slot_identifier= slot_identifier,out_of_rules='location')
                    slots.setdefault(location_id,[]).append(slot)
                    self.slotDict[slot_identifier] = (dict(location_id=location_id),slot)
                self.wrongEvents.setdefault(day,[]).append(dict(event=ev,errors=[],error_desc='OS:Out of rules'))



    def getDoctorRules(self):
        return self.db.table('base.time_rule').query(columns='*,$level,$priority_code,$rule_type',
                                                   where="""( $doctor_id=:doctor_id OR  ( $doctor_id IS NULL  AND ($location_id IS NULL OR $location_id IN :locations )))  
                                                            AND ($valid_from IS NULL OR $valid_from<=:end_date)
                                                            AND ($valid_to IS NULL OR $valid_to>=:start_date)
                                                             """,
                                                   order_by = '$priority_code DESC',
                                                   zerolevel=0,
                                                   locations=self.locationsDict.keys(),
                                                   doctor_id=self.doctor_id,
                                                   start_date=self.start_date,
                                                   end_date=self.end_date).fetch()


    def getEvents(self,newEvent=None):
        evt_id=None
        where="""$doctor_id=:doctor_id AND ($evt_date BETWEEN :start_date AND :end_date) """
        if newEvent and newEvent.get('event_id'):
            evt_id =newEvent['event_id']
            where+=" AND $id!=:evt_id"
        sel= self.db.table('base.event').query(columns= """$id AS event_id,$doctor_id,$room_id,$location_id,$service_id,
                                                                        $evt_date,$evt_start_time,$evt_end_time,
                                                                        $patient_name,$patient_contact_link,
                                                                        @referrer_id.name_full AS referrer_name,
                                                                        $location_name,
                                                                        $evt_description,$service_name,
                                                                        $color,$background,$is_activity,$type_name,
                                                                        $notes,$estimate_notes,
                                                                        $cancelled""",
                                                                     where=where,
                                                                     doctor_id=self.doctor_id,
                                                                     start_date=self.start_date, 
                                                                     end_date=self.end_date,
                                                                     evt_id=evt_id,
                                                                    order_by='$evt_date').selection(_aggregateRows=True)
        appDict = {}
        for app in sel:
            appDict.setdefault(app['evt_date'], []).append(app)
        if newEvent:
            appDict.setdefault(newEvent['evt_date'],[]).append(newEvent)
        return appDict
                

    def applyEvents(self,dayEvents=None, slots=None, day=None, hideEvents=None):
        def cb(r):
            z = filter (lambda s: s['slot_start'] == r, slots)
            if not z:
                s = self.slotMaker(day,r.time()).next()
                slot_identifier= s.hour*self.scale_slot+s.minute/self.interval
                z = dict(slot_start=s, slot_identifier= slot_identifier,event=ap,out_of_rules=True)
                assigned = self.slotDict.get(slot_identifier)
                if assigned:
                    assigned[1]['event'] = True
                slots.append(z)
                slots.sort(key=lambda x: x['slot_start'])
                return 'OS:not existing slot'
            z = z[0]
            if 'deny' in z:
                return 'DS:not existing slot (deny rule)'
            if  'event' in z:
                return 'AP:event overlap'
            z['event'] = ap
            return None
        dEv=[]
        for ap in dayEvents:
            result = map (cb, self.slotMaker(day, ap['evt_start_time'], ap['evt_end_time']))
            errors=[ k for k in result if k]
            if errors:
                self.wrongEvents.setdefault(day,[]).append(dict(event=ap,error_desc=','.join(uniquify(errors))))
        dayEvents[:] = dEv


    def unifySlots(self, slots,locationInfo):
        unified_slots = []
        prev_identifier=None
        prev_room=None
        prev_referrer_id =None
        prev_deny=None
        prev_rel_id=None
        for slot in slots:
            new_rel_id = None
            evt= slot.get('event')
            if evt is True:
                continue
            if evt:
                new_rel_id = evt.get('event_id')

            if (slot['slot_identifier']-1 != prev_identifier) or (slot.get('room_id') != prev_room) \
                                or (slot.get('deny')!= prev_deny) or prev_rel_id!=new_rel_id \
                                or (slot.get('referrer_id') != prev_referrer_id):
                s_time = (slot['slot_start'].hour,slot['slot_start'].minute)
                slot_cell = {'s_time':s_time,
                            'duration':self.interval,'notes':slot.get('notes','')}
                if slot.get('out_of_rules'):
                    slot_cell['out_of_rules'] = slot.get('out_of_rules')
                slot_cell.update(locationInfo)
                if slot.get('deny'):
                    slot_cell.update({'denied':True, 'deny_reason':slot.get('deny')})
                if evt:
                    slot_cell.update({'event_id':new_rel_id, '_evt_rec':dict(evt),
                                      'evt_description':evt.get('evt_description'),
                                      'color':evt.get('color'),
                                      'background_color':evt.get('background'),
                                      'is_activity':evt.get('is_activity'),
                                      'serv_type':evt.get('evt_serv_type'),
                                      'type_name':evt.get('type_name')})

                unified_slots.append(slot_cell)
            else:
                unified_slots[-1]['duration'] += self.interval
                last_s_time = unified_slots[-1]['s_time']
                d = last_s_time[1] + unified_slots[-1]['duration']
                e_time = (last_s_time[0]+d/60 , d%60)
                unified_slots[-1]['e_time'] = e_time
            prev_identifier=slot['slot_identifier']
            prev_room=slot.get('room_id')
            prev_deny=slot.get('deny')
            prev_rel_id = new_rel_id
            prev_referrer_id = slot.get('referrer_id')

        return unified_slots
        
    def applyDenyRules(self, dayDenyRules, slots=None, showDenied=None):
        def cb(s):
            s = s['slot_start']
            s_end=s + relativedelta.relativedelta(minutes=self.interval)
            s = s.time()
            s_end = s_end.time()
            allowed=False
            if dr['am_start_time'] and dr['am_end_time']:
                allowed=(s >= dr['am_end_time']) or (s_end<=dr['am_start_time'])
            if dr['pm_start_time'] and dr['pm_end_time']:
                allowed=allowed and((s >= dr['pm_end_time']) or (s_end<=dr['pm_start_time']))
            return allowed

        def markCb(s):
            if not cb(s):
                s['deny'] = dr['notes'] or 'Not available'
            return s

        for dr in dayDenyRules:
            if showDenied:
                slots = map(markCb, slots)
            else:
                slots = filter(cb, slots)
        return slots

    def dayRulesWithSlots(self, day, dayRules):
        result = []
        for r in dayRules:
            s=[]
            if r['am_start_time'] and r['am_end_time']:
                s=[k for k in self.slotMaker(day, r['am_start_time'], r['am_end_time'])]
            if r['pm_start_time'] and r['pm_end_time']:
                s.extend([k for k in self.slotMaker(day, r['pm_start_time'], r['pm_end_time'])])
            result.append([r,set(s)])
        return result

    def slotMaker(self,day, t1, t2=None):
        if not t2:
            t2 = (datetime.combine(day,t1)+relativedelta.relativedelta(minutes=self.interval)).time()
        t2 = datetime.combine(day,t2)-relativedelta.relativedelta(minutes=self.interval)
        for s in rrule.rrule(rrule.MINUTELY, interval=self.interval, dtstart=datetime.combine(day,t1), until=t2):
            yield s

    def dayRules(self, day, location_id=None, rule_type=None):
        main_location_id = self.main_location_id
        k = 'on_%s' % self.weekdays[day.weekday()]

        def cb(r):
            dayOfMonth=day.day
            weekArray=self.monthWeekDays[day.weekday()]
            freq=r['month_frequency']
            valid_from = r['valid_from']
            valid_to = r['valid_to']
            validByDate= ((not valid_from or valid_from<=day) and (not valid_to or day<=valid_to))
            denyOrInherited = (rule_type=='deny'  or ( r['doctor_id'] or main_location_id==r['location_id']))
            denyOrNotLocationOrCurrLocation = (not location_id or (r['location_id']==location_id) or rule_type=='deny')
            correctRuleType = r['rule_type'] == rule_type
            rightFrequency =(freq is None) or (freq == 'a') or (freq.startswith('w') and day in self.weeklyRulesDict[r['id']]) \
                            or (freq=='l' and weekArray[-1]==dayOfMonth) or (freq.isdigit() and weekArray[int(freq)-1]==dayOfMonth)
            return r[k] and correctRuleType and denyOrNotLocationOrCurrLocation and denyOrInherited and validByDate and rightFrequency


        drules= filter(cb,self.rules)
        sortByItem(drules,'priority_code:d','location_id','valid_from:d')
        return drules

    def _dayIterator(self):
        itr = rrule.rrule(rrule.DAILY, dtstart=self.start_date, until=self.end_date)
        for d in itr:
            yield d.date()
