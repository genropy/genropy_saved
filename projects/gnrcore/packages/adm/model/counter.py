# encoding: utf-8
import re
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('counter', pkey='codekey',pkey_columns='pkg,tbl,code,period', name_long='!!Counter')
        self.sysFields(tbl, id=False, ins=True, upd=True)
        tbl.column('codekey', size=':80 ', readOnly='y', name_long='!!Codekey', indexed='y')
        tbl.column('code', size=':12', readOnly='y', name_long='!!Code')
        tbl.column('pkg', size=':12', readOnly='y', name_long='!!Package')
        tbl.column('tbl', size=':30', readOnly='y', name_long='!!Table')
        tbl.column('fld', size=':30', readOnly='y', name_long='!!Counter Field')
        tbl.column('period',size=':10',name_long='!!Period',indexed='y')
        tbl.column('counter', 'L', name_long='!!Counter')
        tbl.column('last_used', 'D', name_long='!!Last used')
        tbl.column('holes', 'X', name_long='!!Holes')
        tbl.column('errors','X', name_long='!!Errors')


    def alignSequences(self,tblobj,field=None,to_align=None):
        if isinstance(to_align,basestring):
            to_align = to_align.split(',')
        pars = getattr(tblobj,'counter_%s' %field)()
        boundaries = self._getBoundaries(**pars)
        if boundaries['N'][0] is not None:
            for sq in to_align:
                self._alignOneSequence(tblobj,sq=sq,field=field,boundaries=boundaries,**pars)
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
                    sq[Y_start,Y_end] = period_year[2:]
                else:
                    sq[Y_start,Y_end] = period_year
            if period_month:
                sq[boundaries['M']] = list(period_month)
            if period_day:
                sq[boundaries['D']] = list(period_day)
        self._alignOneSequence(tblobj,field=field,sq=''.join(sq),boundaries=boundaries,**counter_pars)

    def _alignOneSequence(self,tblobj,field=None,sq=None,boundaries=None,date_field=None,format=None,code=None,**kwargs):
        #sq example  XY/2010-****  $K/$YYYY-$NNNN
        period = {}
        for k in 'YMD':
            b = boundaries[k]
            period[k] = sq[b[0]:b[1]] if b[0] else ''
        kbound = boundaries['K']
        code = sq[kbound[0]:kbound[1]] if kbound[0] is not None else None
        N_start,N_end = boundaries['N']
        placeholder = '*'* (N_end-N_start)
        delta = len(placeholder)
        columns='substring($%s from %i for %i) AS cnt' %(field,N_start+1,delta)
        if date_field:
            columns='%s,$%s' %(columns,date_field)
        l = tblobj.query(columns=columns ,
                        where="overlay($%s placing '%s' from %i for %i) =:sq" %(field,placeholder,N_start+1,delta),
                        sq=sq).fetch()
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
                if prev_date and prev_date>rdate:
                    err = dict(r)
                    err['prev_date'] = prev_date
                    errors.setItem('wrongOrder.%i' %i,None, **err)
                prev_date = rdate
            if prevcnt and prevcnt==cnt:
                errors.setItem('duplicates.%i' %i,None,**dict(r))
            elif cnt>i:
                h = dict()
                h['cnt_from'] = i
                h['cnt_to'] = cnt-1
                if date_field:
                    h['date_from'] = prev_date
                    h['date_to'] = rdate
                i = cnt
                holes.setItem(str(i),None, **h)
            prevcnt = cnt
        errors=errors or None
        holes=holes or None
        if errors is not None:
            print errors
        record = dict(pkg=tblobj.pkg.name,tbl=tblobj.name,fld=field,period=period,code=code,counter=cnt,last_used=prev_date,holes=holes,errors=errors)
        codekey = self.newPkeyValue(record)
        with self.recordToUpdate(codekey=codekey,insertMissing=True) as r:
            r.update(record)


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

    def getFieldSequences(self,tblobj,field=None):
        pars = getattr(tblobj,'counter_%s' %field)()
        N_start,N_end = self._getBoundaries(**pars)['N']
        if N_start is None:
            return
        placeholder = '*'* (N_end-N_start)
        return tblobj.query(columns="overlay($%s placing '%s' from %i for %i) as dc" %(field,placeholder,N_start+1,len(placeholder)),distinct=True).fetch()
         

    def formatCode(self, code, output, ymd, counter):
        """Create the output for the code and return it
        
        :param code: the counter code
        :param output: the formatting output for the key
        :param ymd: a tuple including year, month and day as strings
        :param counter: the long integer counter"""
        x = '$N%s' % output.split('$N')[1]
        
        output = output.replace(x, str(counter).zfill(len(x) - 1))
        output = output.replace('$YYYY', ymd[0])
        output = output.replace('$YY', ymd[0][2:])
        output = output.replace('$MM', ymd[1])
        output = output.replace('$DD', ymd[2])
        output = output.replace('$K', code)
        return output

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