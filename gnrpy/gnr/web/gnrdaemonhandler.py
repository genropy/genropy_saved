#!/usr/bin/env python2.7
# encoding: utf-8
# 
from datetime import datetime
from multiprocessing import Process
from gnr.web.gnrwsgisite_proxy.gnrsiteregister import GnrSiteRegisterServer
from gnr.core.gnrbag import Bag
from gnr.core.gnrsys import expandpath
from gnr.app.gnrconfig import gnrConfigPath
import atexit
import os
import urllib
import time

import Pyro4
if hasattr(Pyro4.config, 'METADATA'):
    Pyro4.config.METADATA = False
if hasattr(Pyro4.config, 'REQUIRE_EXPOSE'):
    Pyro4.config.REQUIRE_EXPOSE = False
OLD_HMAC_MODE = hasattr(Pyro4.config,'HMAC_KEY')
PYRO_HOST = 'localhost'
PYRO_PORT = 40004
PYRO_HMAC_KEY = 'supersecretkey'

def createSiteRegister(sitename=None,daemon_uri=None,host=None, socket=None, hmac_key=None,storage_path=None,debug=None,autorestore=False):
    print 'creating'
    server = GnrSiteRegisterServer(sitename=sitename,daemon_uri=daemon_uri,storage_path=storage_path,debug=debug)
    print 'starting'
    server.start(host=host,socket=socket,hmac_key=hmac_key,port='*',autorestore=autorestore)

def createHeartBeat(site_url=None,interval=None,**kwargs):
    server = GnrHeartBeat(site_url=site_url,interval=interval,**kwargs)
    time.sleep(interval)
    server.start()

def getFullOptions(options=None):
    gnr_path = gnrConfigPath()
    enviroment_path = os.path.join(gnr_path,'environment.xml')
    env_options = Bag(expandpath(enviroment_path)).getAttr('gnrdaemon')
    if env_options.get('sockets'):
        if env_options['sockets'].lower() in ('t','true','y') :
            env_options['sockets']=os.path.join(gnr_path,'sockets')
        if not os.path.isdir(env_options['sockets']):
            os.makedirs(env_options['sockets'])
        env_options['socket']=env_options.get('socket') or os.path.join(env_options['sockets'],'gnrdaemon.sock')
    assert env_options,"Missing gnrdaemon configuration."
    for k,v in options.items():
        if v:
            env_options[k] = v
    return env_options

class GnrHeartBeat(object):
    def __init__(self,site_url=None,interval=None,**kwargs):
        self.interval = interval
        self.site_url = site_url
        self.url = "%s/sys/heartbeat"%self.site_url

    def start(self):
        while True:
            try:
                response = urllib.urlopen(self.url)
                response_code = response.getcode() 
                if response_code!=200:
                    self.retry('WRONG CODE %i' %response_code)   
                else:                
                    time.sleep(self.interval)
            except IOError:
                self.retry('IOError')

    def retry(self,reason):                
        print '%s -> will retry in %i seconds' %(reason,3*self.interval)
        time.sleep(3*self.interval)



class GnrDaemonProxy(object):
    def __init__(self,host=None,port=None, socket=None,hmac_key=None,compression=True,use_environment=False,serializer='pickle'):
        options=dict(host=host, socket=socket, port=port,hmac_key=hmac_key,compression=compression)
        if use_environment:
            options = getFullOptions(options=options)
        self.hmac_key = str(options.get('hmac_key') or PYRO_HMAC_KEY)
        if OLD_HMAC_MODE:
            Pyro4.config.HMAC_KEY = self.hmac_key
        Pyro4.config.SERIALIZER = options.get('serializer','pickle')
        Pyro4.config.COMPRESSION = options.get('compression',True)

        if options.get('socket'):
            self.uri='PYRO:GnrDaemon@./u:%s' % options.get('socket')
        else:
            self.uri = 'PYRO:GnrDaemon@%s:%s' %(options.get('host') or PYRO_HOST,options.get('port') or PYRO_PORT)
    
    def proxy(self):
        proxy = Pyro4.Proxy(self.uri)
        proxy._pyroHmacKey = self.hmac_key
        return proxy

class GnrDaemon(object):
    def __init__(self):
        self.running = False
        self.siteregisters= dict()
        self.siteregisters_process = dict()
        self.sshtunnel_index = dict()

    def start(self,use_environment=False,**kwargs):
        if use_environment:
            options =  getFullOptions(options=kwargs)
        self.do_start(**options)


    def do_start(self, host=None, port=None, socket=None, hmac_key=None,
                      debug=False,compression=False,timeout=None,
                      multiplex=False,polltimeout=None,use_environment=False, size_limit=None,
                      sockets=None):
        self.pyroConfig(host=host,port=port, socket=socket, hmac_key=hmac_key,debug=debug,
                        compression=compression,timeout=timeout,
                        multiplex=multiplex,polltimeout=polltimeout, size_limit=size_limit,
                        sockets=sockets)
        if self.socket:
            print 'start daemon new socket',self.socket
            self.daemon = Pyro4.Daemon(unixsocket=self.socket)
        else:
            self.daemon = Pyro4.Daemon(host=self.host,port=int(self.port))
        if not OLD_HMAC_MODE:
            self.daemon._pyroHmacKey = self.hmac_key
        self.main_uri = self.daemon.register(self,'GnrDaemon')
        print "uri=",self.main_uri
        self.running = True
        atexit.register(self.stop)
        self.daemon.requestLoop(lambda : self.running)
        
    def pyroConfig(self,host=None,port=None, socket=None, hmac_key=None,
                      debug=False,compression=False,timeout=None,
                      multiplex=False,polltimeout=None, size_limit=None,sockets=None):
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        self.port=port or PYRO_PORT
        self.host = host or PYRO_HOST
        self.socket = socket 
        self.sockets = sockets
        self.hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        if OLD_HMAC_MODE:
            Pyro4.config.HMAC_KEY = self.hmac_key
        if compression:
            Pyro4.config.COMPRESSION = True
        if multiplex:
            Pyro4.config.SERVERTYPE = "multiplex"
        if timeout:
            Pyro4.config.TIMEOUT = timeout
        if polltimeout:
            Pyro4.config.POLLTIMEOUT = timeout
        if size_limit:
            Pyro4.config.SIZE_LIMIT = size_limit
    
    def onRegisterStart(self,sitename,server_uri=None,register_uri=None):
        self.siteregisters[sitename]['server_uri'] = server_uri
        self.siteregisters[sitename]['register_uri'] = register_uri

        print 'registered ',sitename,server_uri

    def onRegisterStop(self,sitename=None):
        print 'onRegisterStop',sitename
        self.siteregisters.pop(sitename,None)
        process_dict = self.siteregisters_process.pop(sitename,None)
        if process_dict and process_dict['heartbeat']:
            process_dict['heartbeat'].terminate()
        
    def ping(self,**kwargs):
        return 'ping'
    
    def getSite(self,sitename=None,create=False,storage_path=None,autorestore=None,heartbeat_options=None,**kwargs):
        if sitename in self.siteregisters and self.siteregisters[sitename]['server_uri']:
            return self.siteregisters[sitename]
        elif create:
            self.addSiteRegister(sitename,storage_path=storage_path,autorestore=autorestore,
                                    heartbeat_options=heartbeat_options)
            return dict()
        
    def stop(self,saveStatus=False,**kwargs):
        self.daemon.close()
        self.siteregister_stop('*',saveStatus=saveStatus)
        for t in self.sshtunnel_index.values():
            t.stop()
        self.running = False

    def restart(self,**kwargs):
        self.stop(saveStatus=True)

    
    def addSiteRegister(self,sitename,storage_path=None,autorestore=False,heartbeat_options=None):
        if not sitename in self.siteregisters:
            socket = os.path.join(self.sockets,'%s_daemon.sock' %sitename) if self.sockets else None
            process_kwargs = dict(sitename=sitename,daemon_uri=self.main_uri,host=self.host,socket=socket
                                   ,hmac_key=self.hmac_key, storage_path=storage_path,autorestore=autorestore)
            childprocess = Process(name='sr_%s' %sitename, target=createSiteRegister,kwargs=process_kwargs)
            self.siteregisters[sitename] = dict(sitename=sitename,server_uri=False,register_uri=False,start_ts=datetime.now())
            childprocess.daemon = True
            childprocess.start()
            hbprocess = None
            if heartbeat_options:
                hbprocess = Process(name='hb_%s' %sitename, target=createHeartBeat,kwargs=heartbeat_options)
                hbprocess.start()
            self.siteregisters_process[sitename] = dict(register = childprocess,heartbeat=hbprocess)

        else:
            print 'ALREADY EXISTING ',sitename

    def pyroProxy(self,url):
        proxy = Pyro4.Proxy(url)
        if not OLD_HMAC_MODE:
            proxy._pyroHmacKey = self.hmac_key
        return proxy


    def siteRegisters(self,**kwargs):
        return self.siteregisters.items()

    def siteRegisterProxy(self,sitename):
        return self.pyroProxy(self.siteregisters[sitename]['register_uri'])

    def siteregister_dump(self,sitename=None,**kwargs):
        uri = self.siteregisters[sitename]['register_uri']
        with self.pyroProxy(uri) as proxy:
            return proxy.dump()


    def setSiteInMaintenance(self,sitename,status=None,allowed_users=None):
        uri = self.siteregisters[sitename]['register_uri']
        with self.pyroProxy(uri) as proxy:
            return proxy.setMaintenance(status,allowed_users=allowed_users)

    def siteregister_stop(self,sitename=None,saveStatus=False,**kwargs):
        result = None
        if sitename=='*':
            for k in self.siteregisters:
                self.siteregister_stop(k,saveStatus=saveStatus)
            return
        uri = self.siteregisters[sitename]['server_uri']
        with self.pyroProxy(uri) as proxy:
            result = proxy.stop(saveStatus=saveStatus)
        self.onRegisterStop(sitename)
        return result

    def siteregister_restart(self,sitename=None,**kwargs):
        self.siteregister_stop(sitename,True)

    def sshtunnel_port(self,ssh_host=None,ssh_port=None, ssh_user=None, ssh_password=None, forwarded_port=None,forwarded_host=None,**kwargs):
        return self.sshtunnel_get(ssh_host=ssh_host,ssh_port=ssh_port,ssh_password=ssh_password,forwarded_port=forwarded_port,forwarded_host=forwarded_host).local_port

    def sshtunnel_get(self,ssh_host=None,ssh_port=None, ssh_user=None, ssh_password=None, 
                     forwarded_port=None,forwarded_host=None,**kwargs):
        from gnr.core.gnrssh import normalized_sshtunnel_parameters
        ssh_parameters = normalized_sshtunnel_parameters(ssh_host=ssh_host,ssh_port=ssh_port,ssh_user=ssh_user,ssh_password=ssh_password,
                                        forwarded_port=forwarded_port,forwarded_host=forwarded_host)
        tunnelKey = '%(ssh_host)s:%(ssh_port)s - %(forwarded_host)s:%(forwarded_port)s' %ssh_parameters
        if not tunnelKey in self.sshtunnel_index:
            self.sshtunnel_index[tunnelKey] = self.sshtunnel_create(**ssh_parameters)
        return self.sshtunnel_index[tunnelKey]

    def sshtunnel_create(self,ssh_host=None,ssh_port=None, ssh_user=None, ssh_password=None, 
                     forwarded_port=None,forwarded_host=None,**kwargs):
        from gnr.core.gnrssh import SshTunnel
        tunnel = SshTunnel(forwarded_port=int(forwarded_port), forwarded_host=forwarded_host,
                ssh_host=ssh_host, ssh_port=int(ssh_port), 
                username=ssh_user, password=ssh_password)
        tunnel.prepare_tunnel()
        tunnel.serve_tunnel()
        return tunnel   

    def sshtunnel_stop(self,**tunnel_kwargs):
        self.sshtunnel_get(**tunnel_kwargs).stop()
        