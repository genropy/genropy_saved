# encoding: utf-8

def main(db):
    print '\t create mail in attachments storage'  
    if not db.table('sys.service').checkDuplicate(service_type='storage',service_name='mail'):
        from gnr.app.gnrdeploy import PathResolver
        p = PathResolver()
        db.table('sys.service').addService(service_type='storage',service_name='mail',
                                                implementation='local',
                                                base_path='/'.join((p.site_name_to_path(db.application.instanceName),'mail'))
                                                )
