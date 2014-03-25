# encoding: utf-8
import re
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('counter', pkey='codekey', name_long='!!Counter')
        self.sysFields(tbl, id=False, ins=True, upd=True)
        tbl.column('codekey', size=':80 ', readOnly='y', name_long='!!Codekey', indexed='y')
        tbl.column('code', size=':12', readOnly='y', name_long='!!Code')
        tbl.column('pkg', size=':12', readOnly='y', name_long='!!Package')
        tbl.column('tbl', size=':30', readOnly='y', name_long='!!Table')
        tbl.column('fld', size=':30', readOnly='y', name_long='!!Counter Field')
        tbl.column('counter', 'L', name_long='!!Counter')
        tbl.column('last_used', 'D', name_long='!!Last used')
        tbl.column('holes', 'X', name_long='!!Holes')
        tbl.column('errors','X', name_long='!!Errors')


    def alignSequences(self,tblobj,field=None,to_align=None):
        if isinstance(to_align,basestring):
            to_align = to_align.split(',')
        pars = getattr(tblobj,'counter_%s' %field)()
        limits = self.getSequenceLimits(**pars)
        if not limits:
            return
        for sq in to_align:
            self._alignCounter(tblobj,sq=sq,field=field,limits=limits,**pars)

    def _alignCounter(self,tblobj,field=None,sq=None,limits=None,date_field=None,format=None,code=None,**kwargs):
        counter_key = sq.replace('*','').replace('.','').replace('/','').replace('-','').replace('_','')
        if not '$K' in format:
            counter_key = '%s%s' %(code,counter_key)
        counter_key = '%s_%s' %(tblobj.fullname,counter_key)
        s_start,s_end = limits
        placeholder = '*'* (s_end-s_start-1)
        delta = len(placeholder)
        columns='substring($%s from %i for %i) AS cnt' %(field,limits[0]+1,delta)
        if date_field:
            columns='%s,$%s' %(columns,date_field)
        l = tblobj.query(columns=columns ,
                        where="overlay($%s placing '%s' from %i for %i) =:sq" %(field,placeholder,limits[0]+1,delta),
                        sq=sq).fetch()
        i = 0
        errors = Bag()
        holes = Bag()
        prev_date = None
        prevcnt = None
        cnt = 0
        l = sorted(l,key=lambda r: r['cnt'])
        for r in l:
            i+=1
            cnt = int(r['cnt'])
            if date_field:
                rdate = r[date_field]
                if prev_date and prev_date>rdate:
                    err = dict(r)
                    err['prev_date'] = prev_date
                    errors.setItem('wrongOrder.%i' %i, **err)
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
        with self.recordToUpdate(codekey=counter_key,insertMissing=True) as record:
            record['codekey'] = counter_key
            record['counter'] = cnt
            record['tbl'] = tblobj.fullname
            record['pkg'] = record['tbl'].split('.')[0]
            record['fld'] = field
            record['last_used'] = prev_date
            record['holes'] = holes
            record['errors'] = errors




    def getSequenceLimits(self,format=None,code=None,**kwargs):
        format = format.replace('$YY','YY')
        format = format.replace('$MM','MM')
        format = format.replace('$DD','DD')
        format = format.replace('$K','K'*len(code))
        s = re.search("(\\$N+)", format)
        if not s:
            return
        return s.span()

    def getFieldSequences(self,tblobj,field=None):
        pars = getattr(tblobj,'counter_%s' %field)()
        limits = self.getSequenceLimits(**pars)
        if not limits:
            return
        s_start,s_end = limits
        placeholder = '*'* (s_end-s_start-1)
        return tblobj.query(columns="overlay($%s placing '%s' from %i for %i) as dc" %(field,placeholder,s_start+1,len(placeholder)),distinct=True).fetch()
            