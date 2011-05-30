# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('validazione', pkey='id', name_long='!!Validation', name_plural='!!Validations')
        self.sysFields(tbl)
        tbl.column('validate_case_c',name_long='!!validate_case=\"c\"')
        tbl.column('validate_case_u',name_long='!!validate_case=\"u\"')
        tbl.column('validate_case_l',name_long='!!validate_case=\"l\"')
        tbl.column('validate_case_t',name_long='!!validate_case=\"t\"')
        tbl.column('validate_email_1',name_long='!!validate_email + error')
        tbl.column('validate_email_2',name_long='!!validate_email + onAccept')
        tbl.column('validate_len_1',name_long='!!validate_len_1')
        tbl.column('validate_len_2',name_long='!!validate_len_1')
        tbl.column('validate_len_3',name_long='!!validate_len_1')
        tbl.column('validate_notnull',name_long='!!validate_notnull')
        tbl.column('validate_regex',name_long='!!validate_regex')
        tbl.column('validate_call',dtype='N',name_long='!!validate_call')
        #fb.textbox(value='^.validate_len_:10', lbl='validate_len=\":10\"',
        #            validate_len=':10',
        #            validate_len_error="""Wrong lenght: the field accept a string
        #                                  of maximum 10 characters""")
        #fb.textBox(value='^.validate_len_5',lbl='validate_len=\'5\'',validate_len='5')
        #fb.textBox(value='^.validate_len_6:',lbl='validate_len=\'6:\'',validate_len='6:',
        #           validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        #fb.textbox(value='^.validate_notnull',lbl='validate_notnull',validate_notnull=True)
        #fb.textbox(value='^.validate_regex',lbl='validate_regex (not \".\")',validate_regex='!\.',
        #           validate_regex_error='!!Don\'t write any \".\" char in the expression')