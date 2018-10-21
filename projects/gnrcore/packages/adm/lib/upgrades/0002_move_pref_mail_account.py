# encoding: utf-8

def main(db):
    pref_mail_account = db.application.getPreference('mail',pkg='adm')
    if pref_mail_account and pref_mail_account['smtp_host']:
        with db.table('sys.service').recordToUpdate(service_type='mail',service_name='mail',insertMissing=True) as rec:
            rec['parameters'] = pref_mail_account
            rec['implementation'] = 'mailservice'

