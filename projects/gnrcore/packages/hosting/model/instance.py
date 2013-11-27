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
        tbl = pkg.table('instance', rowcaption='code',name_long='Instance',name_plural='Instances')
        self.sysFields(tbl)
        tbl.column('code', size=':10', name_long='!!Instance Code')
        tbl.column('description', name_long='!!Instance Description')
        tbl.column('repository_name', dtype='T', name_long='!!Repository Name') # Optional
        tbl.column('path', dtype='T', name_long='!!Instance Path')
        tbl.column('site_path', dtype='T', name_long='!!Site Path')
        tbl.column('slot_configuration', 'X', name_long='!!Slot configuration', _sendback=True)
        tbl.column('hosted_data', 'X', name_long='!!Hosted data', _sendback=True)
        tbl.column('client_id', size=':22', name_long='!!Client id').relation('hosting.client.id', mode='foreignkey',
                                                                            relation_name='instances')
        tbl.column('active','B',name_long='Active')
        tbl.column('last_update_log',name_long='!!Last update log')

        tbl.pyColumn('current_host',name_long='Host',dtype='A')

    
    def pyColumn_current_host(self,record=None,**kwargs):
        appconfig = self.db.application.config
        code = record['code']
        remote_db = appconfig['aux_instances.%s?remote_db' % code] 
        result = None
        if remote_db:
            ssh_host = appconfig['remote_db.%s?ssh_host' %remote_db]
            if ssh_host:
                result = ssh_host.split('@')[1] if '@' in ssh_host else ssh_host
        return result or 'localhost'

    def create_instance(self, code):
        instanceconfig = Bag(self.pkg.instance_template())
        instanceconfig.setAttr('hosted', instance=code)
        instanceconfig.setAttr('db', dbname=code)
        base_path = os.path.dirname(self.pkg.instance_folder(code))
        im = InstanceMaker(code, base_path=base_path, config=instanceconfig)
        im.do()
        return im.instance_path

    def create_site(self, code):
        siteconfig = Bag(self.pkg.site_template())
        base_path = os.path.dirname(self.pkg.site_folder(code))
        sm = SiteMaker(code, base_path=base_path, config=siteconfig)
        sm.do()
        return sm.site_path

    def build_apache_site(self, instance_code, apache_path='/etc/apache2/sites-available/', process_name=None, user=None
                          ,
                          group=None, tmp_path='/tmp', threads=25,
                          admin_mail=None, port=80, domain=None,
                          processes=1, base_url='/', sudo_password=None):
        params = dict(process_name=process_name or 'gnr_%s' % instance_code,
                      domain='%s.%s' % (instance_code, domain),
                      user=user,
                      group=group,
                      tmp_path=tmp_path or '/tmp',
                      threads=str(threads),
                      processes=str(processes),
                      base_url=base_url,
                      admin_mail=admin_mail or 'genro@%s' % domain,
                      site_path=self.pkg.site_folder(instance_code),
                      port=str(port)
                      )
        params['process_env'] = 'ENV_%s' % params['process_name'].upper()
        apache_file_content = """<VirtualHost *:80>
                ServerName %(domain)s
                ServerAdmin %(admin_mail)s
                DocumentRoot /var/www
                WSGIDaemonProcess %(process_name)s user=%(user)s group=%(group)s python-eggs=%(tmp_path)s threads=%(threads)s 
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
        """ % params
        tmp_file = NamedTemporaryFile()
        tmp_file.write(apache_file_content)
        tmp_file.flush()
        os.fsync(tmp_file)
        pass_pipe = Popen(['/bin/echo', sudo_password], stdout=PIPE)
        cm = Popen(['sudo -S cp %s %s/%s' % (tmp_file.name, apache_path, instance_code)], stdin=pass_pipe.stdout,
                   shell=True)
        cm.wait()
        pass_pipe = Popen(['/bin/echo', sudo_password], stdout=PIPE)
        cm = Popen(['sudo -S /usr/sbin/a2ensite %s ' % instance_code], stdin=pass_pipe.stdout, shell=True)
        cm.wait()
        pass_pipe = Popen(['/bin/echo', sudo_password], stdout=PIPE)
        Popen(['sudo -S /usr/sbin/apache2ctl graceful'], stdin=pass_pipe.stdout, stdout=None, shell=True, )
        tmp_file.close()


    def prepare_hosted_instance(self, record_data):
        hosted_app = self.db.application.getAuxInstance(record_data['code'])
        hosted_user_table = hosted_app.db.table('adm.user')
        hosted_client_table = hosted_app.db.table('hosting.client')
        hosted_instance_table = hosted_app.db.table('hosting.instance')
        hosted_pkg = self.db.package('hosting').attributes.get('hostedPackage')
        client_id = record_data['client_id']
        client_record = self.db.table('hosting.client').record(record_data['client_id']).output('dict')
        #user_record = self.db.table('adm.user').record(pkey=client_record['user_id']).output('dict')
       # hosted_user_table.insertOrUpdate(user_record)
        hosted_client_table.insertOrUpdate(client_record)
        hosted_instance_table.insertOrUpdate(record_data)
        slots = self.db.table('hosting.slot').query(columns='$slot_type,$quantity', where='instance_id = :i_id', i_id=record_data['id']).fetchAsDict('slot_type')
        hosted_app.db.package(hosted_pkg).createSlots(slots)
        #self.db.application.packages(hosted_pkg).copyLinkedCard(hosted_app, client_record)
        #self.prepopulate_instance(hosted_app)
        hosted_app.db.commit()

    def prepopulate_instance(self, hosted_app):
        hosted_db = hosted_app.db
        for pkg in hosted_db.packages.values():
            pkg.updateFromExternalDb(self.db)
                
    def trigger_onInserting(self, *args, **kwargs):
        pass
        #self.common_inserting_trigger(*args, **kwargs)

    def common_inserting_trigger(self, instance_record):
        if not self.db.application.config['hosting?instance']:
            self.common_inserting_trigger_hosting(instance_record)
        else:
            self.common_inserting_trigger_hosted(instance_record)


    def common_inserting_trigger_hosting(self, record_data):
        self.activate_instance(record_data)

    def activate_instance(self,record_data):
        self.create_instance(record_data['code'])
        self.create_site(record_data['code'])
        self.pkg.db_setup(record_data['code'])
        self.prepare_hosted_instance(record_data)
        if record_data['slot_configuration']:
            self.db.table('hosting.slot').set_slots(record_data['slot_configuration'], record_data['id'])
        for pkg in self.db.application.packages.values():
            if hasattr(pkg, 'onInstanceCreated'):
                getattr(pkg, 'onInstanceCreated')(record_data)
        if sys.platform.startswith('linux'):
            pkg_config = self.db.application.config.getAttr('packages.gnrcore:hosting')
            self.build_apache_site(record_data['code'], domain=pkg_config.get('domain'),
                                   sudo_password=pkg_config.get('sudo_password'),
                                   user=pkg_config.get('user'),
                                   group=pkg_config.get('group') or pkg_config.get('user'))


    def common_inserting_trigger_hosted(self, record_data):
        if record_data['slot_configuration']:
            self.db.table('hosting.slot').set_slots(record_data['slot_configuration'], record_data['id'])


    def trigger_onUpdating(self, record_data, old_record):
        for pkg in self.db.application.packages.values():
            if hasattr(pkg, 'onInstanceUpdated'):
                getattr(pkg, 'onInstanceUpdated')(record_data)
                
