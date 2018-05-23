#!/usr/bin/env python
# encoding: utf-8
from dateutil import rrule
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('day', pkey='date', name_long='!!Days', name_plural='!!Days',caption_field='date')
        tbl.column('date', dtype='D', name_long='!!Date')
        tbl.column('weekday', dtype='L', name_long='!!Weekday')
        tbl.column('is_holyday', dtype='B', name_long='!!Is holyday')

    @public_method    
    def populate(self,date_start=None,date_end=None):
        records = []
        self.sql_deleteSelection(where='$date BETWEEN :ds AND :de',ds=date_start,de=date_end)
        for dt in rrule.rrule(rrule.DAILY, dtstart=date_start, until=date_end):
            records.append({'date':dt,'weekday':dt.weekday()})
        self.insertMany(records)
        self.db.commit()