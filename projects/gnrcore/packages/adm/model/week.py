#!/usr/bin/env python
# encoding: utf-8
import datetime
from dateutil import rrule
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('week', pkey='start_date', name_long='!![en]Week', 
                    name_plural='!![en]Week',caption_field='week')
        tbl.column('start_date', dtype='D', name_long='!![en]Start Date')
        tbl.formulaColumn('week', "to_char($start_date, 'YYYY-IW')", 
                    dtype='T', name_long='Week',static=True)
        tbl.formulaColumn('end_date',"$start_date + interval '6 days' ",
                            dtype='D',name_long='!![en]End Date')

    @public_method    
    def populate(self,start_date=None,end_date=None):
        records = []
        self.sql_deleteSelection(where='$start_date BETWEEN :ds AND :de',ds=start_date,de=end_date)
        start_date = start_date - datetime.timedelta(days = start_date.weekday())
        for dt in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date):
            records.append({'start_date':dt})
        self.insertMany(records)
        self.db.commit()