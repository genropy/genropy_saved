# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrnumber import decimalRound
from dateutil import rrule,relativedelta
from datetime import datetime

import random

caption = '!!Create random records'
tags = '_DEV_'
description = '!!Create random records'

class Main(BaseResourceAction):
    batch_prefix = 'crr'
    batch_title = '!!Create random records'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        how_many = self.batch_parameters['batch']['how_many']
        self.completeRelFieldsPars(how_many)
        for i in range(how_many):
            r = dict()
            min_date=None
            self.fillRandomRecord(r, i)
            self.tblobj.insert(r)
        self.db.commit()

    def fillRandomRecord(self, r, i):
        for field,field_pars in self.batch_parameters['fields'].items():
            condition_field= field_pars['_if']
            if condition_field and not r[condition_field]:
                continue
            col_obj = self.tblobj.columns[field]
            if 'table' in field_pars:
                r[field] = random.choice(field_pars['pkeys'])
                cluster = field_pars['cluster']
                if cluster:
                    for cl_field, cl_bag in cluster.items():
                        cl_records=cl_bag['recordsDict'][r[cl_bag['group_key']]]
                        if cl_records:
                            cl_rec = random.choice(cl_records)
                            r[cl_field] = cl_rec['pkey']
                    
            elif 'copy_from' in field_pars:
                r[field] = r[field_pars['copy_from']]
            else:
                handler = getattr(self, 'getValue_%s' % field_pars['dtype'], self.getValue_T)
                r[field] = handler(field_pars, i)

    def completeRelFieldsPars(self, how_many):
        for field,field_pars in self.batch_parameters['fields'].items():
            if field_pars['dtype'] in ('D','DH'):
                dtstart=field_pars['min_value'] or self.db.workdate
                until = field_pars['max_value'] or self.db.workdate+relativedelta.relativedelta(days=7)
                dates = list(rrule.rrule(rrule.DAILY, interval=1, dtstart=dtstart, until=until))
                field_pars['values'] = [random.choice(dates) for x in range(how_many)]
                field_pars['values'].sort()
            if not 'table' in field_pars:
                continue
            if not field_pars['pkeys']:
                related_tbl = self.db.table(field_pars['table'])
                where_pars = dictExtract(field_pars, 'condition_')
                where = field_pars['condition']
                field_pars['pkeys'] = related_tbl.query(columns='$%s' % related_tbl.pkey, where=where, **where_pars).fetchPkeys()
            else:
                field_pars['pkeys'] = field_pars['pkeys'].split(',')
            cluster = field_pars['cluster']
            if cluster:
                for c in cluster:
                    col_obj = self.tblobj.columns[c['field']]
                    cluster_tblobj = col_obj.relatedTable().dbtable
                    group_key=c['relation_path'].replace('$','').replace('@','').split('.')[0]
                    q = cluster_tblobj.query(columns='$%s,$%s' % (group_key,cluster_tblobj.pkey),
                                             where='%s IN :parent_pkeys' % c['relation_path'],
                                             parent_pkeys=field_pars['pkeys'])
                    field_pars['cluster.%s'% c['field']] = Bag(dict(group_key=group_key, recordsDict=q.fetchGrouped(key=group_key)))
                    

    def getValue_L(self, field_pars, i):
        return random.randint(field_pars['min_value'] or 0, field_pars['max_value'] or 100)

    def getValue_B(self, field_pars, i):
        r= random.randint(1, 100)
        return r <= (field_pars['true_value'] or 50)

    def getValue_N(self, field_pars, i): 
        v=random.uniform(field_pars['min_value'] or 0, field_pars['max_value'] or 100)
        return decimalRound(v,2)

    def getValue_D(self, field_pars, i): 
        return field_pars['values'][i]

    def getValue_DH(self, field_pars, i): 
        date= field_pars['values'][i]
        return datetime.combine(date, datetime.now())

    def getValue_T(self, field_pars, i):
        value= field_pars['value']
        if value:
            if '#' in value:
                value = value.replace('#', str(i+1))
        return value

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        fb = pane.div(border_bottom='1px solid silver',padding='3px').formbuilder(datapath='.batch', cols=2, border_spacing='2px')
        fb.numberTextBox('^.how_many', lbl='How many', width='5em', validate_notnull=True, default_value=1)
        fb.textbox('^.batch_prefix', lbl='Batch prefix', width='5em')
        box_campi = pane.div(max_height='600px',overflow='auto')
        fb = box_campi.div(margin_right='15px').formbuilder(margin='5px',cols=2,
                            border_spacing='3px',
                            dbtable=table,
                            datapath='.fields',
                            fld_width='100%',
                            colswidth='auto',
                            width='650px')
        randomValues = dict()
        if hasattr(tblobj, 'randomValues'):
            randomValues = getattr(tblobj, 'randomValues')()
        for k,v in tblobj.columns.items():
            attr = v.attributes
            dtype=attr.get('dtype')
            rv = randomValues.get(k,dict())
            
            if rv==False or attr.get('_sysfield') or dtype == 'X':
                continue
            
            fb.data('.%s.dtype' %k, dtype)
            if rv.pop('ask',None) == False:
                fb.data('.%s' %k, Bag(rv))
                continue

            kw = fb.prepareFieldAttributes(k)
            dictExtract(kw, prefix='validate_',pop=True)
            
            if dtype =='B':
                fb.horizontalSlider(value='^.%s.true_value'%k ,lbl=kw['lbl'],
                                    minimum=0, maximum=100,
                                    intermediateChanges=True,
                                    discreteValues=11,
                                    width='10em',
                                    default_value=rv.pop('true_value',50))
                fb.div('^.%s.true_value'%k, lbl='True %')
            elif dtype in ('L','N','DH','D','H'):
                lbl=kw.pop('lbl')
                kw.pop('value')
                if dtype =='DH':
                    kw['tag']='dateTextBox'
                kw['width']='8em'
                if kw['tag']=='dateTextBox':
                    kw['period_to']='.%s.max_value'%k
                fb.child(value='^.%s.min_value'%k,
                                  lbl='%s min' % lbl,
                                  default_value=rv.pop('min_value',None), **kw)
                kw.pop('period_to',None)
                fb.child(value='^.%s.max_value'%k,
                                  lbl='%s max' % lbl,
                                  default_value=rv.pop('max_value',None), **kw)     
            else:
                kw['colspan']=2
                kw.update(rv)
                if kw['tag'].lower()=='dbselect':
                    kw['tag'] = 'checkboxtext'
                    kw['table']=kw.pop('dbtable')
                    kw['popup']=True
                    kw['value']='%s.pkeys' % kw['value']
                    rv['table']=kw['table']
                    fb.data('.%s' %k, Bag(rv))
                else:
                    kw['value'] = '%s.value' % kw['value']
                fb.child(**kw)
