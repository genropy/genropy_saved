# encoding: utf-8
"""

id	Optional. Useful for getEventSourceById.
color	Sets every Event Object's color for this source.
backgroundColor	Sets every Event Object's backgroundColor for this source.
borderColor	Sets every Event Object's borderColor for this source.
textColor	Sets every Event Object's textColor for this source.
className	Sets every Event Object's className for this source.
editable	Sets every Event Object's editable for this source.
startEditable	Sets every Event Object's startEditable for this source.
durationEditable	Sets every Event Object's durationEditable for this source.
resourceEditable	Sets every Event Object's resourceEditable for this source.
display	Sets the eventDisplay setting for every event in this source.
overlap	Sets the eventOverlap setting for every event in this source. Does not accept a function.
constraint	Sets the eventConstraint setting for every event in this source.
allow	Sets the eventAllow setting for every event in this source.
defaultAllDay	Sets the defaultAllDay option, but only for this source.



success	Sets the eventSourceSuccess callback, but only for this source.

failure	Sets the eventSourceFailure callback, but only for this source.

eventDataTransform	Sets the eventDataTransform callback, but only for this source.
"""
class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('fcevent', pkey='id', name_long='', name_plural='',caption_field='')
        self.sysFields(tbl)
        tbl.column('color', name_long='color')
        tbl.column('background_color', name_long='backgroundColor')
        tbl.column('text_color', name_long='textColor')
        tbl.column('editable', name_long='editable')
        tbl.column('start_editable', name_long='startEditable')
        tbl.column('duration_editable', name_long='durationEditable')
        tbl.column('display', 'B',name_long='display')
        tbl.column('overlap', 'B',name_long='overlap')
        tbl.column('constraint', 'B',name_long='constraint')
        tbl.column('allow', 'B',name_long='allow')
        tbl.column('default_all_day', 'B',name_long='defaultAllDay')


        tbl.column('start', 'DH', name_long='start')
        tbl.column('end', 'DH', name_long='end')
        tbl.column('start_str', 'DH', name_long='startStr')
        tbl.column('end_str', 'DH', name_long='startStr')

        tbl.column('note', 'DH', name_long='Note')
        tbl.column('classnames',name_long='classNames')
        