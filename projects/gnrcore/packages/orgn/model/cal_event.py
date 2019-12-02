# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('cal_event', pkey='id', name_long='!![en]Event', 
                    name_plural='Events',
                    caption_field='description')
        self.sysFields(tbl)
        tbl.column('description', size=':50', 
                    name_long='!![en]Description',
                    icalendar='DESCRIPTION')
        tbl.column('dtstart', 'DHZ', 
                    name_long='!![en]Begin',
                    icalendar='DTSTART')
        tbl.column('dtend', 'DHZ', 
                    name_long='!![en]End',
                    icalendar='DTEND')
        tbl.column('geocoder', name_long='!![en]Geocode', 
                    name_short='!![en]Geo',icalendar='GEO')
        tbl.column('geodesc', name_long='!![en]Location', 
                    name_short='!![en]Location') 
        
        