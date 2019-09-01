# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from __future__ import division
from builtins import str
from builtins import range
from past.utils import old_div
from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrnumber import decimalRound
from dateutil import rrule,relativedelta
from datetime import datetime,time,date
import string

import random

caption = 'Create random records'
tags = '_DEV_'
description = '!!Create random records'

class Main(BaseResourceAction):
    batch_prefix = 'crr'
    batch_title = 'Create random records'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        how_many = self.batch_parameters['batch']['how_many']
        self.preProcessValues(how_many)
        for i in range(how_many):
            record = dict()
            for field,field_pars in list(self.batch_parameters['fields'].items()):
                condition_field= field_pars['_if']
                null_perc = field_pars['null_perc']
                if not condition_field or self.checkCondition(record,condition_field):
                    if not null_perc or random.randint(1,100)>null_perc:
                        if not field in record:
                            self.setRecordField(record,field,field_pars, i)
            self.tblobj.insert(record)
        self.db.commit()

    def checkCondition(self, r, condition_field):
        if condition_field.startswith('!'):
            return not r.get(condition_field[1:])
        else:
            return r.get(condition_field)

    def setRecordField(self, r, field, field_pars, i):

        if 'equal_to' in field_pars:
            r[field] = r[field_pars['equal_to']]
            return

        if field_pars['values']: #pre-calculated pkeys or dates
            r[field] = field_pars['values'][i]
            if 'copied_values' in field_pars:
                copied_values= field['copied_values'][r['field']]
                for k,v in copied_values:
                    r[k]=v
            return

        if field_pars['allowed_records']:
            based_on_key=r[field_pars['based_on']]
            if based_on_key in field_pars['allowed_records']:
                allowed_records = field_pars['allowed_records'][based_on_key]
                rnd_record=random.choice(allowed_records)

                r[field]=rnd_record[field_pars['from_column']]
                if 'copy_columns' in field_pars:
                    for k in list(field_pars.get('copy_columns').keys()):
                        r[k]=rnd_record.get(k)
            return

        if not self.tblobj.columns[field].relatedTable():
            dtype=field_pars['dtype']
        
            if dtype=='B':
                r[field] = random.randint(1, 100) <= field_pars['true_value']
                return

            if dtype in ('T','A'):
                if field_pars['default_value']:
                    value =field_pars['default_value']
                    if '#P' in value:
                        value=value.replace('#P', self.batch_parameters['batch']['batch_prefix'])
                    if '#N' in value:
                        value=value.replace('#N', str(i+1))
                    
                if field_pars['random_value']:
                    value=self.randomTextValue(n_words=field_pars['n_words'],
                                                  w_length=field_pars['w_length'])
                if field_pars['size']:
                    if ':' in field_pars['size']:
                        s=field_pars['size'].split(':')
                        l_max = int(s[1])
                    else:
                        l_max = int(field_pars['size'])
                    
                    if len(value)>l_max:
                        value=value[:l_max]
                r[field]= value

                return

            if 'range' in field_pars:
                r[field] = self.getValueFromRange(r, field_pars, dtype)
                return

            min_value = field_pars['min_value'] if not 'greater_than' in field_pars else r[field_pars['greater_than']]
            max_value = field_pars['max_value'] if not 'less_than' in field_pars else r[field_pars['less_than']]
            rnd_value=self.randomValue(self.convertToNumber(min_value, dtype),
                                       self.convertToNumber(max_value, dtype),
                                        dtype)
            r[field] = self.convertFromNumber(rnd_value, dtype)
        
       

    def convertToNumber(self, v, dtype):
        if dtype == 'H':
            return  v.hour*60 + v.minute
        elif dtype == 'D':
            return v.toordinal()
        elif dtype =='DH':
            return old_div(int(v.strftime('%s')),60)
        elif dtype == 'N':
            return float(v)
        return v

    def convertFromNumber(self, v, dtype):
        if dtype=='H':
            return time(old_div(v,60),v%60)
        if dtype == 'D':
            return date.fromordinal(v)
        if dtype == 'DH':
            return datetime.fromtimestamp(v*60.0)
        if dtype == 'N':
            return decimalRound(v,2)
        return v

    def randomValue(self, v_min,v_max, dtype):
        if dtype in ('I','L','H','D','DH'):
            return random.randint(int(min(v_min,v_max)), int(max(v_min,v_max)))
        else:
            return random.uniform(min(v_min,v_max), max(v_min,v_max))

    def randomTextValue(self, n_words=None, w_length=None):
        n_words = n_words or '2:5'
        w_length= w_length or '4:12'
        min_wlen, max_wlen =w_length.split(':')
        min_wlen=int(min_wlen.strip())
        max_wlen=int(max_wlen.strip())
        if ':' in n_words:
            words_min,words_max=n_words.split(':')
            words_min=int(words_min.strip())
            words_max=int(words_max.strip())
            n_words=random.randint(words_min,words_max)
        else:
            n_words=int(n_words.strip())

        words_list=[]
        for x in range(n_words):
            wd=''.join( random.choice(string.ascii_lowercase) for _ in range(random.randint(min_wlen, max_wlen)))
            words_list.append(wd)
        words_list[0]=words_list[0].capitalize()
        return ' '.join(words_list)


    def getValueFromRange(self, record, field_pars, dtype):
        if field_pars['greater_than']:
            sign=1
            v_base = record[field_pars['greater_than']]
        else:
            sign=-1
            v_base = record[field_pars['less_than']]
        v_base = self.convertToNumber(v_base,dtype)

        range_str = field_pars['range']
        if ':' in range_str:
            r_min,r_max = range_str.split(':')
        else:
            r_min,r_max = '0',range_str
        
        if '%' in r_min:
            v_min= v_base * (float(r_min.replace('%',''))/100)
        else:
            v_min=float(r_min)

        if '%' in r_max:
            v_max= v_base * (float(r_min.replace('%',''))/100)
        else:
            v_max=float(r_max)

        rnd_value = v_base+ sign * self.randomValue(v_min,v_max,dtype)
        return self.convertFromNumber(rnd_value, dtype)

        

    def getDatesList(self,how_many,dtype,min_value, max_value):
        v_min = self.convertToNumber(min_value, dtype)
        v_max = self.convertToNumber(max_value, dtype)
        dates = [self.convertFromNumber(self.randomValue(v_min,v_max,dtype),dtype) for x in range(how_many)]
        return dates



    def preProcessValues(self, how_many):
        for field,field_pars in list(self.batch_parameters['fields'].items()):
            if 'equal_to' in field_pars:
                continue

            dtype=field_pars['dtype']
            if dtype in ('D','DH'):
                if 'greater_than' in field_pars or 'less_than' in field_pars:
                    continue
                field_pars['values'] = self.getDatesList(how_many,dtype,field_pars['min_value'],field_pars['max_value'])
                if field_pars['sorted']:
                    field_pars['values'].sort()
                continue
                
            related_tbl= self.tblobj.columns[field].relatedTable()
            if not related_tbl:
                continue

            related_tbl=related_tbl.dbtable

            if 'based_on' in field_pars:
                based_on_field = field_pars['based_on']
                based_on_pkeys = self.batch_parameters['fields'][based_on_field]['distinct_pkeys']
                from_table= field_pars.get('from_table')
                from_tbl_obj = self.db.table(field_pars['from_table']) if from_table else related_tbl
                from_column = field_pars.get('from_column') or from_tbl_obj.pkey
                field_pars['from_column']=from_column
                where= '$%s IN :based_on_pkeys' % based_on_field
                if 'condition' in field_pars:
                    where = '%s AND %s' % (where, field_pars['condition'])
                columns='$%s, $%s' % (from_column,based_on_field)
                if 'copy_columns' in field_pars:
                    copy_columns=['%s AS %s' % (v,k) for k,v in list(field_pars['copy_columns'].items())]
                    columns = '%s, %s' % (columns, ', '.join(copy_columns))
                columns='*'
                query=from_tbl_obj.query(columns=columns, where=where, based_on_pkeys=based_on_pkeys)
                field_pars['allowed_records'] = query.fetchGrouped(key=based_on_field)
                field_pars['distinct_pkeys'] = set(query.fetchPkeys())
                continue
            

            if not field_pars['pkeys']:
                where_pars = dictExtract(field_pars, 'condition_')
                where = field_pars['condition']
                pkeys = related_tbl.query(columns='$%s' % related_tbl.pkey, where=where, **where_pars).fetchPkeys()
            else:
                pkeys = field_pars['pkeys'].split(',')
            if pkeys:
                field_pars['values'] = [random.choice(pkeys) for x in range(how_many)]
                field_pars['distinct_pkeys'] = set(field_pars['values'])
                if 'copy_columns' in field_pars:
                    columns_list=['%s AS %s' % (v,k) for k,v in list(field_pars['copy_columns'].items())]
                    field_pars['copied_values'] = related_tbl.query(columns='.'.join(columns_list),
                                            where='$%s IN :pkeys' % related_tbl.pkey,
                                            pkeys=field_pars['distinct_pkeys']).fetchAsDict(key=related_tbl.pkey)

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        fb = pane.div(border_bottom='1px solid silver',padding='3px').formbuilder(datapath='.batch', cols=2, border_spacing='2px')
        fb.numberTextBox('^.how_many', lbl='How many', width='5em', validate_notnull=True, default_value=10)
        fb.textbox('^.batch_prefix', lbl='Batch prefix', width='5em', validate_notnull=True)
        box_campi = pane.div(max_height='600px',overflow='auto')
        fb = box_campi.div(margin_right='15px').formbuilder(margin='5px',cols=3,
                            border_spacing='3px',
                            dbtable=table,
                            datapath='.fields',
                            fld_width='100%',
                            colswidth='auto',
                            width='650px')
        randomValuesDict = dict()
        if hasattr(tblobj, 'randomValues'):
            randomValuesDict = getattr(tblobj, 'randomValues')()
        for col_name, col in list(tblobj.columns.items()):
            attr = col.attributes
            dtype=attr.get('dtype')
            if not col_name in randomValuesDict and (attr.get('_sysfield') or dtype == 'X'):
                continue
            col_rules = randomValuesDict.get(col_name, dict())
            if col_rules is not False:
                if attr.get('size'):
                    col_rules['size']=attr.get('size')
                fb.data('.%s' %col_name, Bag(col_rules))
                fb.data('.%s.dtype' %col_name, dtype)
                if col_rules.pop('ask',None) == False or col_rules.get('equal_to') or col_rules.get('based_on'):
                    continue
                self.table_script_prepareColPars(fb,col_rules,col_name, dtype)
                fb.numberTextBox(value='^.%s.null_perc' % col_name, lbl='NULL %', width='4em',lbl_width='6em', default_value=col_rules.pop('null_perc',0))

            
    def table_script_prepareColPars(self, fb, col_rules, col_name, col_dtype):
        
        kw = fb.prepareFieldAttributes(col_name)
        dictExtract(kw, prefix='validate_',pop=True)

        if col_dtype =='B':
            fb.horizontalSlider(value='^.%s.true_value'%col_name ,lbl=kw['lbl'],
                                minimum=0, maximum=100,
                                intermediateChanges=True,
                                discreteValues=11,
                                width='10em',
                                default_value=col_rules.pop('true_value',50))

            fb.div('^.%s.true_value'%col_name, lbl='True %', _class='fakeTextBox')
            return

        if col_dtype in ('I','L','N','R','DH','D','H'):
            lbl=kw.pop('lbl')
            kw.pop('value',None) #remove valuepath set by prepareFieldAttributes
            kw.pop('innerHTML',None) #remove innerHTML set by prepareFieldAttributes
            if col_dtype =='DH':
                kw['tag']='dateTextBox'
            kw['width']='8em'
            if kw['tag']=='dateTextBox':
                kw['period_to']='.%s.max_value'%col_name
            
            if 'range' in col_rules:
                operator = 'Greater than' if 'greater_than' in col_rules else 'Less than'
                fb.div(col_rules.get('greater_than') or col_rules.get('less_than') , lbl='%s %s' % (lbl, operator), _class='fakeTextBox')
                fb.div(col_rules['range'], lbl='Range',_class='fakeTextBox')
                return
                
            if 'greater_than' in col_rules:
                fb.div(col_rules['greater_than'], lbl='%s min' % lbl, _class='fakeTextBox')
            else:
                fb.child(value='^.%s.min_value'%col_name,
                              lbl='%s min' % lbl,
                              default_value=col_rules.pop('min_value',None), 
                              validate_notnull=True, **kw)
            kw.pop('period_to',None)
            if 'less_than' in col_rules:
                fb.div(col_rules['less_than'], lbl='%s max' % lbl, _class='fakeTextBox')
            else:
                fb.child(value='^.%s.max_value'%col_name,
                              lbl='%s max' % lbl,
                              default_value=col_rules.pop('max_value',None),
                              validate_notnull=True,
                              **kw)
            return
        if col_dtype in ('T','A') and col_rules.get('random_value'):
            lbl=kw.pop('lbl')
            fb.textbox('^.%s.n_words' % col_name, lbl='%s N.Words' % lbl, default_value=col_rules.pop('n_words',None))
            fb.textbox('^.%s.w_length' % col_name, lbl='%s Word Length' % lbl, default_value=col_rules.pop('w_length',None))
            return
        else:
            kw['colspan']=2
            kw.update(col_rules)
            if kw['tag'].lower()=='dbselect': #foreign keys case
                kw['tag'] = 'checkboxtext'
                kw['table']=kw.pop('dbtable')
                kw['popup']=True
                kw['value']='%s.pkeys' % kw['value']
                col_rules['table']=kw['table']
                fb.data('.%s' %col_name, Bag(col_rules))
            else:
                
                    
                kw['value'] = '%s.value' % kw['value']
            fb.child(**kw)
        