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
        os.fsync()
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        cm=Popen(['sudo -S cp %s %s/%s'%(tmp_file.name,apache_path,instance_code)],stdin=pass_pipe.stdout,shell=True)
        cm.wait()
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        cm=Popen(['sudo -S /usr/sbin/a2ensite %s '%instance_code],stdin=pass_pipe.stdout,shell=True)
        cm.wait()
        pass_pipe=Popen(['/bin/echo',sudo_password], stdout=PIPE)
        Popen(['sudo -S /usr/sbin/apache2ctl reload'],stdin=pass_pipe.stdout,stdout=None,shell=True,)
        tmp_file.close()

    def trigger_onInserting(self, record_data):
        self.create_instance(record_data['code'])
        self.create_site(record_data['code'])
        if sys.platform.startswith('linux'):
            self.build_apache_site(record_data['code'],domain=self.db.application.config['hosting?domain'] or 'icond.it', sudo_password=self.db.application.config['hosting?sudo_password'] or 'Ch14ra3Nen3')
        self.pkg.db_setup(record_data['code'])
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceCreated'):
                getattr(pkg,'onInstanceCreated')(record_data)
    
    def trigger_onUpdating(self, record_data, old_record):
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceUpdated'):
                getattr(pkg,'onInstanceUpdated')(record_data)
                