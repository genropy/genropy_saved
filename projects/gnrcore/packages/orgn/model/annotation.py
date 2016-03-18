# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('annotation',pkey='id',name_long='Annotation',
                            name_plural='Annotations',caption_field='annotation_caption',
                            order_by='$__ins_ts')
        self.sysFields(tbl,user_upd=True)
        tbl.column('rec_type',size='2',values='AN:[!!Annotation],AC:[!!Action]')
        #belong to annotation
        tbl.column('author_user_id',size='22',group='_',name_long='User').relation('adm.user.id',relation_name='annotations',onDelete='raise')

        tbl.column('description',name_long='!!Description')
        tbl.column('annotation_type_id',size='22',name_long='!!Annotation type',group='_').relation('annotation_type.id',mode='foreignkey', onDelete='raise')
        tbl.column('annotation_fields',dtype='X',name_long='!!Annotation Fields',subfields='annotation_type_id')
        
        #belong to actions
        tbl.column('parent_annotation_id',size='22' ,group='_',name_long='!!Parent annotation').relation('annotation.id',relation_name='orgn_related_actions',mode='foreignkey',onDelete='cascade')
        tbl.column('action_type_id',size='22',name_long='!!Action type',group='_').relation('action_type.id',mode='foreignkey', onDelete='raise')
        tbl.column('action_fields',dtype='X',name_long='!!Action Fields',subfields='action_type_id')
        tbl.column('assigned_user_id',size='22',group='_',name_long='!!User').relation('adm.user.id',relation_name='orgn_actions',onDelete='raise')
        tbl.column('assigned_tag',size=':50',name_long='!!User Tag')
        tbl.column('priority',size=':2',name_long='!!Priority',values='NW:[!!Now],UR:[!!Urgent],HG:[!!High],LW:[!!Low]')
        tbl.column('days_before',dtype='I',name_long='!!Days before',name_short='D.Before')
        tbl.column('date_due',dtype='D',name_long='!!Date due',indexed=True)
        tbl.column('time_due',dtype='H',name_long='!!Time due',indexed=True)
        tbl.column('done_ts',dtype='DH',name_long='!!Done ts',indexed=True)
        tbl.aliasColumn('assigned_username','@assigned_user_id.username')
        tbl.formulaColumn('annotation_caption',"""CASE WHEN rec_type='AC' 
                                                 THEN @action_type_id.description || '-' || $assigned_to
                                                 ELSE @annotation_type_id.description END
                                                    """,name_long='!!Annotation')
        tbl.formulaColumn('annotation_background',"COALESCE(@action_type_id.background_color,@annotation_type_id.background_color)",name_long='!!Background',group='*')
        tbl.formulaColumn('annotation_color',"COALESCE(@action_type_id.color,@annotation_type_id.color)",name_long='!!Foreground',group='*')

        tbl.formulaColumn('assigned_to',"""COALESCE($assigned_username,$assigned_tag,'unassigned')""",name_long='Assigment')
        tbl.formulaColumn('connected_fkey',"NULL")
        tbl.formulaColumn('connected_description',"'override me'")
        tbl.formulaColumn('_assignment_base',
                                """($rec_type ='AC' AND ( CASE WHEN $assigned_user_id IS NOT NULL THEN  $assigned_user_id=:env_user_id
                                   CASE WHEN $assigned_tag IS NOT NULL THEN $assigned_by_tag
                                   ELSE TRUE END))""",
                                dtype='B',group='_')
        tbl.formulaColumn("assigned_by_tag","""(',' || :env_userTags || ',' LIKE '%%,'|| COALESCE($assigned_tag,'') || ',%%')""",
                        dtype='B')


    def defaultValues(self):
        return dict(author_user_id=self.db.currentEnv.get('user_id'))


    def formulaColumn_pluggedFields(self):
        desc_fields = []
        fkeys = []
        assigments_restrictions = ["$_assignment_base"]
        for colname,colobj in self.columns.items():
            if colname.startswith('_assignment'):
                assigments_restrictions.append(colname)
            related_table = colobj.relatedTable()
            if related_table and related_table.column('orgn_description') is not None:
                fkeys.append('$%s' %colname)
                desc_fields.append('@%s.orgn_description' %colname)

        description_formula = "COALESCE(%s)" %','.join(desc_fields) if desc_fields else "'NOT PLUGGED'"
        fkeys_formula = "COALESCE(%s)" %','.join(fkeys) if fkeys else "'NOT PLUGGED'"
        assigment_formula = ' AND '.join(assigments_restrictions)

        return [dict(name='connected_fkey',sql_formula=fkeys_formula),
                dict(name='connected_description',sql_formula=description_formula),
                dict(name='plugin_assigment',sql_formula='(%s)' %assigment_formula,dtype='B',name_long='Assigned to me')]

    def getRestrictions(self):
        result = []
        for colname,colobj in self.columns.items():
            if colobj.attributes.get('restrictions'):
                result.extend(colobj.attributes['restrictions'].split(','))
        return ','.join(result)

