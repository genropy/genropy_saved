#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdeploy import InstanceMaker, SiteMaker
from gnr.core.gnrbag import Bag
import os
from subprocess import Popen, PIPE
from  tempfile import NamedTemporaryFile
import sys

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('instance', rowcaption='')
        self.sysFields(tbl)
        tbl.column('code',size=':10',name_long='!!Instance Code')
        tbl.column('description',name_long='!!Instance Description')
        tbl.column('repository_name', dtype='T', name_long='!!Repository Name') # Optional
        tbl.column('path',dtype='T',name_long='!!Instance Path')
        tbl.column('site_path',dtype='T',name_long='!!Site Path')
        tbl.column('slot_configuration','X',name_long='!!Slot configuration',_sendback=True)  
        tbl.column('hosted_data','X',name_long='!!Hosted data',_sendback=True)  
        tbl.column('client_id',size=':22',name_long='!!Client id').relation('client.id',mode='foreignkey')

    def create_instance(self, code):
        instanceconfig=Bag(self.pkg.instance_template())
        instanceconfig.setAttr('hosted',instance=code)
        instanceconfig.setAttr('db',dbname=code)
        base_path=os.path.dirname(self.pkg.instance_folder(code))
        im=InstanceMaker(code, base_path=base_path, config=instanceconfig)
        im.do()
        return im.instance_path
        
    def create_site(self, code):
        siteconfig=Bag(self.pkg.site_template())
        base_path=os.path.dirname(self.pkg.site_folder(code))
        sm=SiteMaker(code, base_path=base_path, config=siteconfig)
        sm.do()
        return sm.site_path

    def build_apache_site(self, instance_code, apache_path='/etc/apache2/sites-available/',process_name=None,user='genro',
                    group='genro', tmp_path='/tmp', threads=25,
                    admin_mail=None, port=80, domain=None,
                    processes=1, base_url='/', sudo_password=None):
        params=dict(process_name=process_name or 'gnr_%s'%instance_code,
                    domain='%s.%s'%(instance_code,domain),
                    user=user,
                    group=group,
                    tmp_path=tmp_path or '/tmp',
                    threads=str(threads),
                    processes=str(processes),
                    base_url=base_url,
                    admin_mail=admin_mail or 'genro@%s'%domain,
                    site_path=self.pkg.site_folder(instance_code),
                    port=str(port)
                    )
        params['process_env']='ENV_%s'%params['process_name'].upper()
        apache_file_content="""<VirtualHost *:80>
                ServerName %(domain)s
                ServerAdmin %(admin_mail)s
                DocumentRoot /var/www
                WSGIDaemonProcess %(process_name)s user=%(user)s group=%(group)s python-eggs=%(tmp_path)s threads=%(threads)s processes=%(processes)s
                SetEnv %(process_env)s %(process_name)s
                WSGIProcessGroup %%{ENV:%(process_env)s}
                # modify the following line to point your site
                WSGIScriptAlias %(base_url)s %(site_path)s/root.py
                <Directory %(site_path)s>
                    Options Indexes FollowSymLinks
                    AllowOverride All
                    Order allow,deny
                    Allow from all
                </Directory>
        </VirtualHost>
        """%params
        tmp_file = NamedTemporaryFile()
        tmp_file.write(apache_file_content)
        tmp_file.flush()
        os.fsync(tmp_file)
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        cm=Popen(['sudo -S cp %s %s/%s'%(tmp_file.name,apache_path,instance_code)],stdin=pass_pipe.stdout,shell=True)
        cm.wait()
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        cm=Popen(['sudo -S /usr/sbin/a2ensite %s '%instance_code],stdin=pass_pipe.stdout,shell=True)
        cm.wait()
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        Popen(['sudo -S /usr/sbin/apache2ctl reload'],stdin=pass_pipe.stdout,stdout=None,shell=True,)
        tmp_file.close()


    def prepare_hosted_instance(self, record_data):
        hosted_app=self.db.application.getAuxInstance(record_data['code'])
        hosted_anag_table=hosted_app.db.table('sw_base.anagrafica')
        hosted_user_table=hosted_app.db.table('adm.user')
        hosted_client_table=hosted_app.db.table('hosting.client')
        hosted_instance_table=hosted_app.db.table('hosting.instance')
        client_id = record_data['client_id']
        anagrafica_id,user_id=self.db.table('hosting.client').readColumns(record_data['client_id'],'$anagrafica_id,$user_id')
        user_record = self.db.table('adm.user').record(pkey=user_id).output('dict')
        anagrafica_record = self.db.table('sw_base.anagrafica').record(pkey=anagrafica_id).output('dict')
        client_record = self.db.table('hosting.client').record(pkey=client_id).output('dict')
        hosted_anag_table.insertOrUpdate(anagrafica_record)
        hosted_user_table.insertOrUpdate(user_record)
        hosted_client_table.insertOrUpdate(client_record)
        hosted_instance_table.insertOrUpdate(record_data)
        self.prepopulate_instance(hosted_app)
        hosted_app.db.commit()

    def prepopulate_instance(self, hosted_app):
        hosted_db = hosted_app.db
        for pkg in hosted_db.packages.values():
            for tbl in pkg.tables.values():
                if not tbl.attributes.get('hosting_prepopulate'):
                    continue
                tbl_name="%s.%s"%(pkg.name,tbl.name)
                hosting_table = self.db.table(tbl_name)
                hosted_table = hosted_db.table(tbl_name)
                records = hosting_table.query().fetch()
                for record in records:
                    hosted_table.insert(record)

    def trigger_onInserting(self, *args,**kwargs):
         self.common_inserting_trigger(*args,**kwargs)

    def common_inserting_trigger(self, instance_record):
        if not self.db.application.config['hosting?instance']:
            self.common_inserting_trigger_hosting(instance_record)
        else:
            self.common_inserting_trigger_hosted(instance_record)

    def common_inserting_trigger_hosting(self, record_data):
        self.create_instance(record_data['code'])
        self.create_site(record_data['code'])
        if sys.platform.startswith('linux'):
            self.build_apache_site(record_data['code'],domain=self.db.application.config['hosting?domain'] or 'icond.it', sudo_password=self.db.application.config['hosting?sudo_password'] or 'Ch14ra3Nen3')
        self.pkg.db_setup(record_data['code'])
        self.prepare_hosted_instance(record_data)
        if record_data['slot_configuration']:
            self.db.table('hosting.slot').set_slots(record_data['slot_configuration'],record_data['id'])
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceCreated'):
                getattr(pkg,'onInstanceCreated')(record_data)
    
    def common_inserting_trigger_hosted(self, record_data):
        if record_data['slot_configuration']:
            self.db.table('hosting.slot').set_slots(record_data['slot_configuration'],record_data['id'])
        
    
    def trigger_onUpdating(self, record_data, old_record):
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceUpdated'):
                getattr(pkg,'onInstanceUpdated')(record_data)
                