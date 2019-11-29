# encoding: utf-8
from __future__ import division
from builtins import object
from past.utils import old_div
import datetime
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import public_method,metadata

import pytz
class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('annotation',pkey='id',name_long='Annotation',
                            name_plural='Annotations',caption_field='annotation_caption',
                            order_by='$sort_ts')
        self.sysFields(tbl,user_upd=True)
        tbl.column('rec_type',size='2',values='AN:[!!Annotation],AC:[!!Action]')
        #belong to annotation
        tbl.column('author_user_id',size='22',
                    group='_',name_long='User').relation('adm.user.id',
                    relation_name='annotations',
                    mode='foreignkey',
                    onDelete='raise')

        tbl.column('description',name_long='!!Description')
        tbl.column('annotation_type_id',size='22',name_long='!!Annotation type',group='_').relation('annotation_type.id',mode='foreignkey', onDelete='raise')
        tbl.column('annotation_fields',dtype='X',name_long='!!Annotation Fields',subfields='annotation_type_id')
        tbl.column('annotation_date',dtype='D',name_long='!!Date',indexed=True)
        tbl.column('annotation_time',dtype='H',name_long='!!Time',indexed=True)
        tbl.column('annotation_ts',dtype='DHZ',name_long='!!Annotation ts',indexed=True)

        #belong to actions
        tbl.column('action_description',name_long='!!Action Description')
        tbl.column('parent_annotation_id',size='22' ,group='_',name_long='!!Parent annotation').relation('annotation.id',relation_name='orgn_related_actions',mode='foreignkey',onDelete='cascade')
        tbl.column('action_type_id',size='22',name_long='!!Action type',group='_').relation('action_type.id',mode='foreignkey', onDelete='raise')
        tbl.column('action_fields',dtype='X',name_long='!!Action Fields',subfields='action_type_id')
        tbl.column('assigned_user_id',size='22',group='*',name_long='!!Assigned to').relation('adm.user.id',relation_name='orgn_actions',onDelete='raise')
        tbl.column('done_user_id',size='22',group='*',name_long='!!Done by').relation('adm.user.id',relation_name='orgn_actions_done',onDelete='raise')

        tbl.column('assigned_tag',size=':50',name_long='!!User Tag')
        tbl.column('priority',size='1',name_long='!!Priority',values='L:[!!Low],M:[!!Medium],H:[!!High]')
        tbl.column('notice_days',dtype='I',name_long='!!Notice days',name_short='N.Days')
        tbl.column('date_due',dtype='D',name_long='!!Date due',indexed=True)
        tbl.column('time_due',dtype='H',name_long='!!Time due',indexed=True)
        tbl.column('done_ts',dtype='DHZ',name_long='!!Done ts',indexed=True)
        tbl.column('linked_table',name_long='!!Linked table')
        tbl.column('linked_entity',name_long='!!Linked entity')
        tbl.column('linked_fkey',name_long='!!Linked fkey')
        tbl.column('delay_history',dtype='X',group='*',name_long='!!Delay history',_sendback=True)

        tbl.aliasColumn('assigned_username','@assigned_user_id.username',name_long='!!Assigned username')
        tbl.aliasColumn('action_type_description','@action_type_id.description',group='*')
        tbl.aliasColumn('action_type_color','@action_type_id.color',group='*',name_long='Action Color')
        tbl.aliasColumn('action_type_background','@action_type_id.background_color',group='*',name_long='Action BG')

        tbl.formulaColumn('annotation_caption',"""CASE WHEN rec_type='AC' 
                                                 THEN @action_type_id.description || '-' || $assigned_to
                                                 ELSE @annotation_type_id.description END
                                                    """,name_long='!!Annotation')
        tbl.formulaColumn('annotation_background',"COALESCE(@action_type_id.background_color,@annotation_type_id.background_color)",name_long='!!Background',group='*')
        tbl.formulaColumn('annotation_color',"COALESCE(@action_type_id.color,@annotation_type_id.color)",name_long='!!Foreground',group='*')

        tbl.formulaColumn('assigned_to',"""COALESCE($assigned_username,$assigned_tag,'unassigned')""",name_long='Assigment')
        tbl.formulaColumn('connected_description',"'override me'")
        tbl.formulaColumn('_assignment_base',
                                """($rec_type ='AC' AND 
                                ( CASE WHEN ($assigned_user_id IS NOT NULL AND @action_type_id.show_to_all_tag IS NOT TRUE) THEN  $assigned_user_id=:env_user_id
                                                               WHEN $assigned_tag IS NOT NULL THEN $assigned_by_tag IS TRUE
                                  ELSE TRUE END)) AND 
                                (CASE WHEN $notice_days IS NOT NULL 
                                     THEN (CASE WHEN $calculated_date_due IS NOT NULL THEN ($calculated_date_due + $notice_days) <= :env_workdate ELSE TRUE END)  
                                 ELSE TRUE END)""",
                                dtype='B',group='_')
        tbl.formulaColumn("assigned_by_tag","""(',' || :env_userTags || ',' LIKE '%%,'|| COALESCE($assigned_tag,'') || ',%%')""",
                        dtype='B')

        tbl.formulaColumn('sort_ts',"""(CASE WHEN $rec_type='AN' THEN $annotation_ts
                                             ELSE $calculated_due_ts END)""",dtype='DH',group='*')

        tbl.formulaColumn("calculated_due_ts","""(CASE WHEN $time_due IS NOT NULL THEN $calculated_date_due+$time_due
                                                       WHEN $calculated_date_due IS NOT NULL THEN CAST($calculated_date_due AS TIMESTAMP)
                                                       ELSE $annotation_ts END)""",
                        dtype='DH',name_long='!!Calc.Due ts')

        tbl.formulaColumn("calculated_date_due","""COALESCE ($date_due,$pivot_date_due)""",dtype='D',name_long='!!Calc.Date due')

        tbl.formulaColumn("pivot_date_due","""(CASE WHEN @action_type_id.deadline_days IS NOT NULL
                                                        THEN $pivot_date+@action_type_id.deadline_days
                                                    ELSE NULL END)""",dtype='D',name_long='!!Pivot date due')

        tbl.formulaColumn('following_actions',"array_to_string(ARRAY(#factions),',')",select_factions=dict(table='orgn.annotation',columns="$action_type_description || '-' || COALESCE($action_description,'missing description')",
                                                                where='$parent_annotation_id=#THIS.id'),name_long='!!Following actions')
        
        tbl.formulaColumn('__protected_by_author',"""
            CASE WHEN :env_orgn_author_only IS NOT TRUE THEN string_to_array(:env_userTags,',') @> string_to_array(COALESCE(:env_orgn_superuser_tag,''),',')
            ELSE $author_user_id!=:env_user_id END
            """,dtype='B')
        tbl.pyColumn('calc_description',name_long='!!Calc description',required_columns='calculated_date_due,time_due,$action_type_description,$following_actions')

        tbl.pyColumn('countdown',name_long='!!Countdown',required_columns='$calculated_date_due,$time_due,$rec_type,$done_ts')
        tbl.pyColumn('zoomlink',name_long='!!Zoomlink',required_columns='$connected_description,$linked_table,$linked_fkey,$linked_entity')

        tbl.pyColumn('template_cell',dtype='A',group='_',py_method='templateColumn', template_name='action_tpl',template_localized=True)



    def pyColumn_calc_description(self,record=None,field=None):
        if record['rec_type'] == 'AN':
            if not record['done_ts']:
                return record['description']
            else:
                c0 = self.db.currentPage.getRemoteTranslation('!!Previous Action')['translation']
                c1 = self.db.currentPage.getRemoteTranslation('!!Outcome')['translation']
                action_description = record['action_description'] or record['action_type_description']
                description = '%s %s' %(record['description'] or '', record['following_actions'] or '')
                result = "<b>%s:</b><i>%s</i><br/><b>%s:</b>%s" %(c0,action_description,c1,description)
                return result
        else:
            return record['action_description']

    def pyColumn_countdown(self,record=None,field=None):
        date_due = record.get('calculated_date_due')
        if not date_due:
            return
        if record['time_due']:
            due_ts = datetime.datetime.combine(date_due,record['time_due'])
        else:
            due_ts = datetime.datetime(date_due.year,date_due.month,date_due.day)

        td = due_ts-datetime.datetime.now()
        tdh = int(old_div(td.total_seconds(),3600))
        result = None
        if tdh<0:
            tdh = -tdh
            if tdh >48:
                result = self.expired_tpl_short() %dict(days=int(old_div(tdh,24)))
            else:
                result = self.expired_tpl_long() %dict(days=int(old_div(tdh,24)),hours=tdh%24)
        else:
            if tdh >48:
                result = self.due_tpl_short() %dict(days=int(old_div(tdh,24)))
            else:
                result = self.due_tpl_long() %dict(days=int(old_div(tdh,24)),hours=tdh%24)
        return result

    def pyColumn_zoomlink(self,record=None,field=None):
        for colname,colobj in list(self.columns.items()):
            if colname.startswith('le_') and colobj.relatedTable().fullname == record['linked_table']:
                attr = colobj.attributes
                entity = record['linked_entity'] 
                zoomPars = dictExtract(attr,'linked_%s_' %entity)
                zoomMode = zoomPars.get('zoomMode')
                title = None
                if zoomMode == 'page':
                    title = '%s - %s' %(self.db.currentPage.getRemoteTranslation(self.db.table(record['linked_table']).name_long)['translation'],
                                        record['connected_description'])
                result = self.db.currentPage.zoomLink(table=record['linked_table'],pkey=record['linked_fkey'],
                                                    formResource=zoomPars.get('formResource','Form'),
                                                    caption=record['connected_description'],
                                                    zoomMode=zoomMode,
                                                    zoomUrl=zoomPars.get('zoomUrl'),
                                                    title=title)
                return result


    def expired_tpl_short(self):
        return '<div class="orgn_action_expired">Overdue %(days)s days</div>'

    def expired_tpl_long(self):
        return '<div class="orgn_action_over_expired">Overdue %(days)s days and %(hours)s hours</div>'


    def due_tpl_short(self):
        return '<div class="orgn_action">Due in %(days)s days</div>'

    def due_tpl_long(self):
        return '<div class="orgn_near_action">Due in %(days)s days and %(hours)s hours</div>'

    def formulaColumn_pluggedFields(self):
        desc_fields = []
        pivot_dates = []
        assigments_restrictions = ["$_assignment_base"]
        for colname,colobj in list(self.columns.items()):
            if colname.startswith('_assignment'):
                assigments_restrictions.append(colname)
            elif colname.startswith('le_'):
                related_table = colobj.relatedTable()
                if related_table:
                    assigments_restrictions.append(' ( CASE WHEN $%s IS NOT NULL THEN @%s.__allowed_for_partition ELSE TRUE END ) ' %(colname,colname))
                    if related_table.column('orgn_description') is not None:
                        desc_fields.append('@%s.orgn_description' %colname)
                    elif related_table.attributes.get('caption_field'):
                        desc_fields.append('@%s.%s' %(colname,related_table.attributes['caption_field']))
                    if related_table.column('orgn_pivot_date') is not None:
                        pivot_dates.append('@%s.orgn_pivot_date' %colname)
        description_formula = "COALESCE(%s,'Missing caption')" %','.join(desc_fields) if desc_fields else "'NOT PLUGGED'"
        pivot_date_formula =  "COALESCE(%s,CAST($__ins_ts AS date))" %','.join(pivot_dates) if pivot_dates else "CAST($__ins_ts AS date)"
        assigment_formula = ' AND '.join(assigments_restrictions)
        return [dict(name='connected_description',sql_formula=description_formula),
                dict(name='pivot_date',sql_formula=pivot_date_formula,name_long='!!Pivot date',dtype='D'),
                dict(name='plugin_assigment',sql_formula='(%s)' %assigment_formula,dtype='B',name_long='Assigned to me')]


    def setAnnotationTs(self,record_data):
        annotation_date = record_data['annotation_date']
        annotation_time = record_data['annotation_time']
        record_data['annotation_ts'] = None #fix for avoid comparing of bag
        record_data['annotation_ts'] = datetime.datetime(annotation_date.year, annotation_date.month, 
                                                        annotation_date.day, annotation_time.hour, 
                                                        annotation_time.minute, annotation_time.second,
                                                        annotation_time.microsecond, tzinfo=pytz.utc)


    def relatedEntityInfo(self,record):
        for colname,colobj in list(self.columns.items()):
            related_table = colobj.relatedTable()
            if colname.startswith('le_') and record.get(colname):
                return related_table.fullname,(record.get('linked_entity') or self.linkedEntityName(related_table)),record[colname]


    def trigger_onInserting(self,record_data=None):
        now = datetime.datetime.now(pytz.utc)
        if record_data['rec_type'] == 'AC' and not record_data['date_due']:
            pivot_date = self.getPivotDateFromDefaults(record_data)
            ts = record_data['__ins_ts']
            if not pivot_date or datetime.datetime(pivot_date.year,pivot_date.month,pivot_date.day)<ts:
                ts = ts + datetime.timedelta(seconds=1)
                record_data['date_due'] = ts.date()
                record_data['time_due'] = ts.time()
        record_data['annotation_date'] = record_data.get('annotation_date') or now.date()
        record_data['annotation_time'] = record_data.get('annotation_time') or now.time()
        self.setAnnotationTs(record_data)
        record_data['author_user_id'] = self.db.currentEnv.get('user_id')
        record_data['linked_table'],record_data['linked_entity'],record_data['linked_fkey'] = self.relatedEntityInfo(record_data)

    def trigger_onUpdating(self,record_data,old_record=None):
        if old_record['rec_type'] == 'AC' and record_data['rec_type'] == 'AN':
            #closing action
            record_data['done_user_id'] = self.db.currentEnv.get('user_id')
            record_data['done_ts'] = datetime.datetime.now(pytz.utc)
            record_data['annotation_date'] = record_data['done_ts'].date()
            record_data['annotation_time'] = record_data['done_ts'].time()
            confirmed_type_id = self.db.table('orgn.annotation_type').sysRecord('ACT_CONFIRMED')['id']
            rescheduled_type_id = self.db.table('orgn.annotation_type').sysRecord('ACT_RESCHEDULED')['id']
            if record_data['annotation_type_id'] == rescheduled_type_id:
                rescheduling = record_data.pop('rescheduling',None)
                if rescheduling:
                    rescheduled_action = self.record(pkey=record_data['id']).output('dict')
                    rescheduling.update(dictExtract(rescheduled_action,'le_',slice_prefix=False))
                    rescheduling.update(dictExtract(rescheduled_action,'linked_',slice_prefix=False))
                    rescheduling['date_due'] = rescheduling['date_due'] or rescheduled_action['date_due']
                    rescheduling['time_due'] = rescheduling['time_due'] or rescheduled_action['time_due']
                    rescheduling['assigned_tag'] = rescheduling['assigned_tag'] or rescheduled_action['assigned_tag']
                    rescheduling['assigned_user_id'] = rescheduling['assigned_user_id'] or rescheduled_action['assigned_user_id']
                    self.insert(rescheduling)
            elif record_data['annotation_type_id'] == confirmed_type_id and record_data.pop('outcome_id',None):
                next_action = record_data.pop('next_action',None)
                if next_action:
                    followed_action = self.record(pkey=record_data['id']).output('dict')
                    next_action['rec_type'] = 'AC'
                    next_action['priority'] = next_action['priority'] or 'L'
                    next_action.update(dictExtract(followed_action,'le_',slice_prefix=False))
                    next_action.update(dictExtract(followed_action,'linked_',slice_prefix=False))
                    next_action['parent_annotation_id'] = record_data['id']
                    self.insert(next_action)
                #if outcome_id:
        if self.fieldsChanged('annotation_date,annotation_time',record_data,old_record):
            self.setAnnotationTs(record_data)

    def getLinkedEntities(self):
        result = []
        for colname,colobj in list(self.columns.items()):
            if colobj.attributes.get('linked_entity'):
                result.extend(colobj.attributes['linked_entity'].split(','))
        return ','.join(result)

    def getLinkedEntityDict(self):
        result = dict()
        for colname,colobj in self.columns.items():
            if colobj.attributes.get('linked_entity'):
                for entity in colobj.attributes['linked_entity'].split(','):
                    code,caption = entity.split(':')
                    result[code] = dict(table=colobj.relatedTable().fullname,caption=caption)
        return result

    def linkedEntityName(self,tblobj):
        joiner = tblobj.relations.getNode('@annotations').attr['joiner']
        pkg,tbl,fkey = joiner['many_relation'].split('.')
        restrictions = self.db.table('orgn.annotation').column(fkey).attributes.get('linked_entity')
        if restrictions:
            restrictions = [r.split(':')[0] for r in restrictions.split(',')]
            return restrictions[0]
        else:
            return tblobj.name

    def getPivotDateFromDefaults(self,action_defaults):
        fkey_field = [k for k,v in list(action_defaults.items()) if k.startswith('le_') if v]
        if fkey_field:
            fkey_field = fkey_field[0] if fkey_field else None
            related_table = self.column(fkey_field).relatedTable()
            orgn_pivot_date_field = self.getPivotDateField(related_table,fkey_field)
            if related_table.column('orgn_pivot_date') is not None:
                return related_table.dbtable.readColumns(pkey=action_defaults[fkey_field],columns='$%s' %orgn_pivot_date_field)

    def getPivotDateField(self,related_table=None,fkey_field=None):
        return self.column(fkey_field).attributes.get('pivot_date') or 'orgn_pivot_date'

    @public_method
    def getDueDateFromDeadline(self,deadline_days=None,pivot_date=None,**action_defaults):
        pivot_date = pivot_date or self.getPivotDateFromDefaults(action_defaults)
        if pivot_date:
            _date_due_from_pivot = datetime.datetime(pivot_date.year,pivot_date.month,pivot_date.day)
            return (_date_due_from_pivot+datetime.timedelta(days=deadline_days)).date()


    def getAllowedActionUsers(self,record):
        table,entity,fkey = self.relatedEntityInfo(record)
        return self.db.table(table).getPartitionAllowedUsers(fkey)


    @metadata(doUpdate=True)
    def touch_fix_annotation_ts(self,record,old_record=None,**kwargs):
        ins_ts = record['__ins_ts']
        record['annotation_date'] = record.get('annotation_date') or ins_ts.date()
        record['annotation_time'] = record.get('annotation_time') or ins_ts.time()

    def newRecordCaption(self,record,**kwargs):
        if record['rec_type'] == 'AN':
            return '!!New annotation'
        else:
            return '!!New action'
