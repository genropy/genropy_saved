# encoding: utf-8
import re
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from datetime import datetime
BASE = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('counter', pkey='codekey',pkey_columns='pkg,tbl,code,fld,period', name_long='!!Counter')
        self.sysFields(tbl, id=False, ins=True, upd=True)
        tbl.column('codekey', size=':80', readOnly='y', name_long='!!Codekey', indexed='y')
        tbl.column('code', size=':12', readOnly='y', name_long='!!Code')
        tbl.column('pkg', size=':12', readOnly='y', name_long='!!Package')
        tbl.column('tbl', size=':30', readOnly='y', name_long='!!Table')
        tbl.column('fld', size=':30', readOnly='y', name_long='!!Counter Field')
        tbl.column('period',size=':10',name_long='!!Period',indexed='y')
        tbl.column('counter', 'L', name_long='!!Counter')
        tbl.column('last_used', 'D', name_long='!!Last used')
        tbl.column('holes', 'X', name_long='!!Holes')
        tbl.column('errors','X', name_long='!!Errors')
        

    def getFieldSequences(self,tblobj,field=None):
        pars = getattr(tblobj,'counter_%s' %field)()
        N_start,N_end = self._getBoundaries(**pars)['N']
        if N_start is None:
            return
        placeholder = '*'* (N_end-N_start)
        #columns="overlay($%s placing '%s' from %i for %i) as dc" %(field,placeholder,N_start+1,len(placeholder))
        columns = "substr($%(fld)s, 1,%(nstart)i) || '%(placeholder)s' || substr($%(fld)s,%(lst)i) AS dc" %dict(fld=field,nstart=N_start,placeholder=placeholder,lst=N_start+len(placeholder)+1)
        dc = tblobj.query(columns = columns,
                            distinct=True,where=" NOT ($%s IS NULL OR $%s='') " %(field,field)).fetch()
        return sorted([r['dc'] for r in dc if r['dc']])


    def initializeApplicationSequences(self,thermo_wrapper=None):
        packages = thermo_wrapper(self.db.packages.values(),message=lambda p,n,m: 'Sequences for package %s' %p.name) if thermo_wrapper else self.db.packages.values()
        for pkg in packages:
            self.initializePackageSequences(pkg,thermo_wrapper=thermo_wrapper)

    def initializePackageSequences(self,pkgobj,thermo_wrapper=None):
        tables = thermo_wrapper(pkgobj['tables'].values(),message=lambda t,n,m: 'Sequences for table %s' %t.name,line_code='tbl') if thermo_wrapper else pkgobj['tables'].values()
        for tblobj in tables:
            self.initializeTableSequences(tblobj.dbtable,thermo_wrapper=thermo_wrapper)

    def initializeTableSequences(self,tblobj,thermo_wrapper=None):
        counter_fields = thermo_wrapper(tblobj.counterColumns(),message=lambda f,n,m: 'Sequences for field %s' %f,line_code='field') if thermo_wrapper else tblobj.counterColumns()
        for field in counter_fields:
            sequences = self.getFieldSequences(tblobj,field=field)
            self.alignSequences(tblobj,field=field,to_align=sequences,thermo_wrapper=thermo_wrapper)

    def alignSequences(self,tblobj,field=None,to_align=None,fix_duplicate=None,thermo_wrapper=None):
        if isinstance(to_align,basestring):
            to_align = to_align.split(',')
        pars = getattr(tblobj,'counter_%s' %field)()
        boundaries = self._getBoundaries(**pars)
        if boundaries['N'][0] is not None:
            to_align = thermo_wrapper(to_align,line_code='sequences',message='Sequence') if thermo_wrapper else to_align
            for sq in to_align:
                self._alignOneSequence(tblobj,sq=sq,field=field,boundaries=boundaries,fix_duplicate=fix_duplicate,**pars)
#
    @public_method
    def alignCounter(self,pkey=None):
        counter_record = self.record(pkey).output('dict')
        tblobj = self.db.table('%(pkg)s.%(tbl)s' %counter_record)
        field = counter_record['fld']
        counter_pars = getattr(tblobj,'counter_%s' %field)()
        boundaries = self._getBoundaries(**counter_pars)
        sq = counter_pars['format']
        sq = sq.replace('$K',counter_record['code'])
        sq = sq.replace('$N','N').replace('$Y','Y').replace('$M','M').replace('$D','')
        sq = list(sq)
        N_start,N_end = boundaries['N']
        sq[N_start:N_end] = list('*'*(N_end-N_start))
        period = counter_record['period']
        if period:
            period_year = counter_record['period'][0:4]
            period_month = counter_record['period'][4:6]
            period_day = counter_record['period'][6:8]
            if period_year:
                period_year = list(period_year)
                Y_start,Y_end = boundaries['Y']
                if Y_end-Y_start<4:
                    sq[Y_start:Y_end] = period_year[2:]
                else:
                    sq[Y_start:Y_end] = period_year
            if period_month:
                sq[boundaries['M'][0]:boundaries['M'][1]] = list(period_month)
            if period_day:
                sq[boundaries['D'][0]:boundaries['D'][1]] = list(period_day)
        self._alignOneSequence(tblobj,field=field,sq=''.join(sq),boundaries=boundaries,**counter_pars)
        self.db.commit()

    def _alignOneSequence(self,tblobj,field=None,sq=None,boundaries=None,date_field=None,format=None,code=None,fix_duplicate=None,**kwargs):
        #sq example  XY/2010-****  $K/$YYYY-$NNNN
        period = {}
        for k in 'YMD':
            b = boundaries[k]
            period[k] = sq[b[0]:b[1]] if b[0] is not None else ''
        kbound = boundaries['K']
        pars_code = code
        code = sq[kbound[0]:kbound[1]] if kbound[0] is not None else None
        N_start,N_end = boundaries['N']
        placeholder = '*'* (N_end-N_start)
        delta = len(placeholder)
        columns='$%s,substr($%s ,%i, %i) AS cnt' %(field,field,N_start+1,delta)
        if date_field:
            columns='%s,$%s' %(columns,date_field)
        dccol = "substr($%(fld)s, 1,%(nstart)i) || '%(placeholder)s' || substr($%(fld)s,%(lst)i)" %dict(fld=field,nstart=N_start,placeholder=placeholder,lst=N_start+delta+1)
        l = tblobj.query(columns=columns ,
                        where="%s = :sq" %dccol,
                        sq=sq,excludeDraft=False).fetch()
        i = 0
        errors = Bag()
        holes = Bag()
        prev_date = None
        prevcnt = None
        cnt = 0
        l = sorted(l,key=lambda r: r['cnt'])   
        if l and date_field and period['Y'] and len(period['Y']) <4:
            period['Y'] = str(l[0][date_field].year)
        if period:
            period = '%(Y)s%(M)s%(D)s' %period
        
        period =period or None
        for r in l:
            i+=1
            cnt = int(r['cnt'])
            if date_field:
                rdate = r[date_field]
                if not rdate:
                    print 'missing date'
                    errors.setItem('missing_date.%i' %i,None,cnt=cnt)
                    continue
                if prev_date and prev_date>rdate:
                    err = dict(record_id=r['pkey'])
                    err['cnt'] = cnt
                    err['cnt_date'] = rdate
                    err['prev_date'] = prev_date
                    errors.setItem('wrongOrder.%i' %i,None, **err)
                #prev_date = rdate
            if prevcnt and prevcnt==cnt:
                if r[field].endswith('_'):
                    pass
                elif fix_duplicate:
                    with tblobj.recordToUpdate(pkey=r['pkey']) as record_to_fix:
                        record_to_fix[field] = '%s_' %r[field]
                else:
                    err = dict(cnt=cnt)
                    errors.setItem('duplicates.%i' %i,None,**err)
                i-=1
            elif cnt>i:
                h = dict(record_id=r['pkey'],date_from=None,date_to=None)
                h['cnt_from'] = i
                h['cnt_to'] = cnt-1
                if date_field:
                    h['date_from'] = prev_date
                    h['date_to'] = rdate
                holes.setItem(str(i),None, **h)
                i = cnt
            prevcnt = cnt
            if date_field:
                prev_date = rdate
        errors=errors or None
        holes=holes or None
        record = dict(pkg=tblobj.pkg.name,tbl=tblobj.name,fld=field,
                        period=period,code=code or pars_code,counter=cnt,
                        last_used=prev_date,holes=holes,errors=errors)
        codekey = self.newPkeyValue(record)
        with self.recordToUpdate(codekey=codekey,insertMissing=True) as counter_record:
            counter_record.update(record)

    def _getBoundaries(self,format=None,code=None,**kwargs):
        format = format.replace('$K','$%s' %('K'*len(code)))
        result = dict()
        for k in 'YMDKN':
            f = format
            for n in 'YMDKN'.replace(k,''):
                f = f.replace('$%s' %n,n)
            s = re.search("(\\$%s+)" %k,f)
            s = s.span() if s else None
            result[k] = (s[0],s[1]-1) if s else (None,None)
        return result

    def getCounterPkey(self,tblobj=None,field=None,record=None):
        return self.pkeyValue(self.newCounterRecord(tblobj=tblobj,field=field,record=record))

    def newCounterRecord(self,tblobj=None,field=None,record=None):
        counter_pars = getattr(tblobj,'counter_%s' %field)(record=record)
        counter_record = Bag(code=counter_pars['code'],pkg=tblobj.pkg.name,tbl=tblobj.name,fld=field)
        date_field = counter_pars.get('date_field')
        format = counter_pars.get('format','')
        if date_field:
            if not record[date_field]:
                raise self.exception('business_logic', msg='!!Missing %s. Mandatory for counter %s' %(date_field,field))
            ymd = self.getYmd(record[date_field])
            period = []
            if '$Y' in format:
                period.append(ymd[0])
            if '$M' in format:
                period.append(ymd[1])
            if '$D' in format:
                period.append(ymd[2])
            if period:
                counter_record['period'] = ''.join(period)
        return counter_record

    def assignCounter(self,tblobj=None,field=None,record=None):
        if record.get(field):
            return
        counter_pars = getattr(tblobj,'counter_%s' %field)(record=record)
        if not counter_pars or (tblobj.isDraft(record) and not counter_pars.get('assignIfDraft')):
            return
        #if not 'unique' in tblobj.column(field).attributes:
        #    print 'MISSING UNIQUE ATTRIBUTE IN FIELD %s IN TABLE %s' %(field,tblobj.fullname)
        record[field] = self.getSequence(tblobj=tblobj,field=field,record=record,update=True)
        if counter_pars.get('onAssigned'):
            counter_pars['onAssigned'](record=record,field=field)
        

    def guessNextSequence(self,tblobj=None,field=None,record=None):
        counter,counterInfo = self.getCounter(tblobj=tblobj,field=field,record=record,update=False)
        sequence = self.formatSequence(tblobj=tblobj,field=field,record=record,counter=counter)
        return sequence,counterInfo

    def getSequence(self,tblobj=None,field=None,record=None,update=False):
        counter,counterInfo = self.getCounter(tblobj=tblobj,field=field,record=record,update=update)
        return self.formatSequence(tblobj=tblobj,field=field,record=record,counter=counter)

    def convertCustomBase(self,counter,base):
        result = []
        b = len(base)
        while counter !=0:
            r = counter % b
            counter = counter  / b
            result.append(base[r])
        result.reverse()
        return ''.join(result)

    def formatSequence(self,tblobj=None,field=None,record=None, counter=None):
        counter_pars = getattr(tblobj,'counter_%s' %field)(record=record)
        base = counter_pars.get('base')
        if base:
            if base and isinstance(base,int):
                base = BASE[0:base]
            counter = self.convertCustomBase(counter,base)
        else:
            counter = str(counter)
        output = counter_pars['format']
        code = counter_pars['code']
        x = '$N%s' % output.split('$N')[1]
        output = output.replace(x, counter.zfill(len(x) - 1))
        output = output.replace('$K', code)        
        date_field = counter_pars.get('date_field')
        date = record[date_field] if date_field else None
        if date_field and not date:
            raise self.exception('business_logic',msg='!!Missing %s. Mandatory for counter %s' %(date_field,field))
        if date:
            ymd = self.getYmd(date)
            output = output.replace('$YYYY', ymd[0])
            output = output.replace('$YY', ymd[0][2:])
            output = output.replace('$MM', ymd[1])
            output = output.replace('$DD', ymd[2])
        return output

    def getCounter(self,tblobj=None,field=None,record=None,update=False):
        counter_pars = getattr(tblobj,'counter_%s' %field)(record=record)
        if counter_pars.get('rootstore'):
            with self.db.tempEnv(storename=self.db.rootstore):
                return self._getCounter(tblobj=tblobj,field=field,record=record,update=update,counter_pars=counter_pars)
        return self._getCounter(tblobj=tblobj,field=field,record=record,update=update,counter_pars=counter_pars)

    def _getCounter(self,tblobj,field=None,record=None,update=None,counter_pars=None):
        counterInfo = dict()
        codekey = self.getCounterPkey(tblobj=tblobj,field=field,record=record)
        date_field = counter_pars.get('date_field')
        recycle = counter_pars.get('recycle') if date_field else False
        date = None
        if date_field:
            date = record[date_field]
            if not date:
                raise self.exception('business_logic', msg='!!Missing date %s for counter %s' %(date_field,field))
            if isinstance(date,datetime):
                date = date.date()
        counter_record = self.record(codekey,ignoreMissing=True,for_update=update).output('record')
        counter_record = counter_record or self.newCounterRecord(tblobj=tblobj,field=field,record=record)
        last_used = counter_record['last_used']
        counter = None
        holes = counter_record['holes']
        if holes and recycle:
            holes.sort('#a.cnt_from')
            for hole_key,cnt_from,cnt_to,date_from,date_to in holes.digest('#k,#a.cnt_from,#a.cnt_to,#a.date_from,#a.date_to'):
                if (date_from is None or date >= date_from) and (date_to is None or date<=date_to):
                    counter = cnt_from
                    cnt_from += 1
                    if cnt_from>cnt_to:
                        holes.pop(hole_key)
                    else:
                        holes.setAttr(hole_key,dict(cnt_from=cnt_from,date_from=date_from))
                    counterInfo.update(recycled=True,cnt=counter)
                    break
        if counter is None:
            counter = (counter_record['counter'] or 0) + 1
            counter_record['last_used'] = date
            counter_record['counter'] = counter
            if date and  last_used and date< last_used:
                msgTpl = counter_pars.get('message_dateError','!!Incompatible date assigning %(fieldname)s counter')
                fieldname = tblobj.column(field).name_long or field
                fieldname = fieldname.replace('!!','')
                if not counter_pars.get('date_tolerant'):
                    raise self.exception('business_logic',msg=msgTpl %dict(fieldname=fieldname,last_used=last_used))
        if update:
            if counter_record['codekey']:
                oldrec = dict(counter_record)
                self.update(counter_record,oldrec)
            else:
                self.insert(counter_record)
            counterInfo['codekey'] = counter_record['codekey']
        return counter,counterInfo


    def releaseCounter(self,tblobj=None,field=None,record=None):
        codekey = self.getCounterPkey(tblobj=tblobj,field=field,record=record)
        counter_pars = getattr(tblobj,'counter_%s' %field)(record=record)
        date_field = counter_pars.get('date_field')
        N_start,N_end = self._getBoundaries(**counter_pars)['N']
        date = record[date_field] if date_field else None
        if date_field and not date:
            raise self.exception('business_logic',msg='!!Missing %s. Mandatory for counter %s' %(date_field,field))
        with self.recordToUpdate(codekey,mode='record',ignoreMissing=True) as counter_record:
            if not counter_record:
                return
            sequence = record[field]
            record[field] = None
            releasing_counter = int(sequence[N_start:N_end])
            if releasing_counter>counter_record['counter']:
                pass
                #raise self.exception('business_logic','Wrong counter releasing')
            else:
                holes = counter_record['holes'] or Bag()
                holes.sort('#a.cnt_from')
                counter_record['holes'] = holes
                i = 0
                cnt_from = releasing_counter
                cnt_to = releasing_counter
                for hole_key,h_cnt_from,h_cnt_to in holes.digest('#k,#a.cnt_from,#a.cnt_to'):
                    if cnt_from == h_cnt_from - 1:
                        cnt_to = h_cnt_to
                        holes.popNode(hole_key)
                        break
                    elif cnt_to == h_cnt_to + 1:
                        cnt_from = h_cnt_from
                        if i<len(holes) - 1:
                            next_hole = holes.nodes[i+1]
                            if next_hole.attr['cnt_from'] == cnt_to+1:
                                cnt_to = next_hole.attr['cnt_to']
                                holes.popNode(next_hole.label)
                        break
                    i += 1
                date_from, date_to = self.getCounterDates(tblobj, record=record, field=field, date_field=date_field,
                                                          cnt_from=cnt_from,
                                                          cnt_to=cnt_to, cnt_last=counter_record['counter'])
                if date_to is None:
                    holes.popNode(str(cnt_from))
                    counter_record['counter'] = cnt_from -1
                    counter_record['last_used'] = date_from
                else:
                    holes.setItem(str(cnt_from), None, cnt_from=cnt_from,
                              cnt_to=cnt_to, date_from=date_from, date_to=date_to)

                holes.sort('#a.cnt_from')
        if counter_pars.get('onReleased'):
            counter_pars['onReleased'](record=record,field=field)


    def getCounterDates(self, tblobj, record=None,field=None, date_field=None,cnt_from=None, cnt_to=None, cnt_last=None):
        wlist = []
        wkw = {}
        d1,d2 = None,None
        if cnt_from>1:
            wkw['prev_counter'] = self.formatSequence(tblobj=tblobj, field=field, record=record, counter=cnt_from-1)
            wlist.append('$%(field)s =:prev_counter')

        if cnt_to<cnt_last:
            wkw['next_counter'] = self.formatSequence(tblobj=tblobj, field=field, record=record, counter=cnt_to+1)
            wlist.append('$%(field)s =:next_counter')

        if wkw:
            f = tblobj.query(where=' OR '.join(wlist) %{'field':field},
                           columns='$%s' % date_field,
                             order_by='$%s' %field, **wkw).fetch()
            d1 = f[0][date_field] if f and cnt_from > 1 else None
            d2 = f[-1][date_field] if f and cnt_to < cnt_last else None
        return d1,d2

    def getYmd(self, date, phyear=False):
        """Return a tuple (year, month, date) of strings from a date.
        
        :param date: the datetime
        :param phyear: the fiscal year (not yet implemented)"""
        if not date:
            return ('0000', '00', '00')
        if phyear:
            #to be completed
            pass
        else:
            return (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))


    def getDuplicates(self,table=None,field=None,code=None):
        result = Bag()
        f = self.db.table(table).query(columns='$%s AS fldval, count($%s) AS cnt' %(field,field),
                            where = "$%s LIKE :c AND $%s IS NOT NULL" %(field,field),
                            c='%%%s%%' %code,group_by='$%s' %field,
                          having="count($%s)>1" %field,addPkeyColumn=False,excludeDraft=False).fetch()
        for fldval,cnt in f:
            result[fldval.replace('.','_')] = Bag(dict(fldval=fldval,cnt=cnt))
        return result

    def use_dbstores(self,forced_dbstore=None, env_forced_dbstore=None,**kwargs):
        return True



