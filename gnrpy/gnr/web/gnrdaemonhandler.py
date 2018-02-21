#!/usr/bin/env python2.7
# encoding: utf-8
# 
from datetime import datetime
import logging
from multiprocessing import Process, log_to_stderr, Pool, Queue, cpu_count
from gnr.web.gnrwsgisite_proxy.gnrsiteregister import GnrSiteRegisterServer
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
from gnr.core.gnrsys import expandpath
from gnr.app.gnrconfig import gnrConfigPath
from gnr.app.gnrdeploy import PathResolver
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

def createSiteRegister(sitename=None,daemon_uri=None,host=None, socket=None,
                         hmac_key=None,storage_path=None,debug=None,autorestore=False,
                         port=None, batch_queue=None):
    print 'creating'
    server = GnrSiteRegisterServer(sitename=sitename,daemon_uri=daemon_uri,
        storage_path=storage_path,debug=debug,batch_queue=batch_queue)
    print 'starting'
    server.start(host=host,socket=socket,hmac_key=hmac_key,port=port or '*',autorestore=autorestore)

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
    def __init__(self,site_url=None,interval=None,loglevel=None,**kwargs):
        self.interval = interval
        self.site_url = site_url
        self.url = "%s/sys/heartbeat"%self.site_url
        self.logger = log_to_stderr()
        self.logger.setLevel(loglevel or logging.DEBUG)

    def start(self):
        while True:
            try:
                self.logger.info("Calling {}".format(self.url))
                response = urllib.urlopen(self.url)
                response_code = response.getcode() 
                if response_code!=200:
                    self.retry('WRONG CODE %i' %response_code)   
                else:                
                    time.sleep(self.interval)
            except IOError:
                self.retry('IOError')
            except Exception, e:
                self.logger.error(str(e))


    def retry(self,reason):
        self.logger.warn('%s -> will retry in %i seconds' %(reason,3*self.interval))
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
        Pyro4.config.ITER_STREAMING = False


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
        self.logger = log_to_stderr()
        

    def start(self,use_environment=False,**kwargs):
        if use_environment:
            options =  getFullOptions(options=kwargs)
        self.do_start(**options)


    def do_start(self, host=None, port=None, socket=None, hmac_key=None,
                      debug=False,compression=False,timeout=None,
                      multiplex=False,polltimeout=None,use_environment=False, size_limit=None,
                      sockets=None, loglevel=None):
        self.loglevel = loglevel or logging.ERROR
        self.logger.setLevel(self.loglevel)
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
        self.logger.info("uri={}".format(self.main_uri))
#        print "uri=",self.main_uri
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
        self.siteregisters[sitename]['register_port'] = int(register_uri.split(':')[-1])
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

    def restart(self, sitename=None, **kwargs):
        self.stop(saveStatus=True)

    def restartServiceDaemon(self,sitename=None,service_name=None):
        print 'restartServiceDaemon',sitename,service_name
        sitedict = self.siteregisters_process[sitename]
        print 'sitedict',sitedict
        if service_name in sitedict:
            print('restarting daemon %s' %service_name)
            proc = sitedict[service_name]
            proc.terminate()
            sitedict[service_name] = self.startServiceDaemon(sitename, service_name=service_name)
            print('restarted daemon %s' %service_name)

    @staticmethod
    def batchWorker(sitename, queue):
        from gnr.web.gnrwsgisite import GnrWsgiSite
        run = True
        site = None
        print 'starting process batch for: ', sitename
        while run:
            try:
                print 'wait for'
                item = queue.get()
                print 'got ', item
                if not item:
                    run = False
                    continue
                print item
                page_id,kwargs = item
                print page_id
                site = site or GnrWsgiSite(sitename)
                page = site.resource_loader.get_page_by_id(page_id)
                page.table_script_run(**kwargs)
            except:
                raise
                pass # dovrei fare qualcosa


    def startBatchPool(self, sitename):
        from gnr.core.gnrstring import boolean
        p = PathResolver()
        siteconfig = p.get_siteconfig(sitename)
        batch_pars = siteconfig.getAttr('batch_processes')
        if not batch_pars or boolean(batch_pars.get('disabled')):
            self.batch_queue = self.batch_pool = None
            return
        self.batch_queue = Queue()
        self.batch_pool = []
        processes = batch_pars.get('processes', 'auto')
        if processes=='auto':
            processes = cpu_count() * 2
        else:
            processes = int(processes)
        for i in range(processes):
            p = Process(name='btc_%s_%i' %(sitename, i+1), 
                        target=self.batchWorker, args=(sitename,self.batch_queue))
            p.daemon = True
            p.start()
            self.batch_pool.append(p)


    def startServiceProcesses(self, sitename, sitedict=None):
        p = PathResolver()
        siteconfig = p.get_siteconfig(sitename)
        services = siteconfig['services']
        if not services:
            return
        for serv in services:
            if serv.attr.get('daemon'):
                sitedict[serv.label] = self.startServiceDaemon(sitename,serv.label)
                print('sitedict',sitedict)

    def startServiceDaemon(self,sitename, service_name=None):
        p = PathResolver()
        siteconfig = p.get_siteconfig(sitename)
        services = siteconfig['services']
        service_attr = services.getAttr(service_name)
        pkg, pathlib = service_attr['daemon'].split(':')
        p = os.path.join(p.package_name_to_path(pkg), 'lib', '%s.py' % pathlib)
        m = gnrImport(p)
        service_attr.update({'sitename': sitename})
        proc = Process(name='service_daemon_%s_%s' %(sitename, service_name), 
                        target=getattr(m, 'run'), kwargs=service_attr)
        proc.daemon = True
        proc.start()
        return proc
        
    
    def addSiteRegister(self,sitename,storage_path=None,autorestore=False,heartbeat_options=None,port=None):
        if not sitename in self.siteregisters:
            socket = os.path.join(self.sockets,'%s_daemon.sock' %sitename) if self.sockets else None
            self.startBatchPool(sitename)
            process_kwargs = dict(sitename=sitename,daemon_uri=self.main_uri,host=self.host,socket=socket
                                   ,hmac_key=self.hmac_key, storage_path=storage_path,autorestore=autorestore,
                                   port=port, batch_queue=self.batch_queue)
            childprocess = Process(name='sr_%s' %sitename, target=createSiteRegister,kwargs=process_kwargs)
            self.siteregisters[sitename] = dict(sitename=sitename,server_uri=False,
                                        register_uri=False,start_ts=datetime.now(),
                                        storage_path=storage_path,heartbeat_options=heartbeat_options,
                                        autorestore=autorestore)
            childprocess.daemon = True
            childprocess.start()
            hbprocess = None
            if heartbeat_options:
                heartbeat_options['loglevel'] = self.loglevel
                hbprocess = Process(name='hb_%s' %sitename, target=createHeartBeat,kwargs=heartbeat_options)
                hbprocess.daemon = True
                hbprocess.start()
            sitedict = dict(register = childprocess,heartbeat=hbprocess)
            self.startServiceProcesses(sitename,sitedict=sitedict)
            self.siteregisters_process[sitename] = sitedict
            

        else:
            print 'ALREADY EXISTING ',sitename

    def pyroProxy(self,url):
        proxy = Pyro4.Proxy(url)
        if not OLD_HMAC_MODE:
            proxy._pyroHmacKey = self.hmac_key
        return proxy


    def siteRegisters(self,**kwargs):
        sr = dict(self.siteregisters)
        for k,v in sr.items():
            register_process = self.siteregisters_process[k]['register']
            v['pid'] = register_process.pid
            v['is_alive'] = register_process.is_alive()
        return sr.items()

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
            for k in self.siteregisters.keys():
                self.siteregister_stop(k,saveStatus=saveStatus)
            return
        uri = self.siteregisters[sitename]['server_uri']
        try:
            with self.pyroProxy(uri) as proxy:
                result = proxy.stop(saveStatus=saveStatus)
                print('after stop',result)
        except Exception as e:
            print str(e)
        self.onRegisterStop(sitename)
        return result

    def siteregister_restartServiceDaemon(self,sitename=None,service_name=None):
        self.restartServiceDaemon(sitename=sitename, service_name=service_name)

    def siteregister_restart(self,sitename=None,**kwargs):
        pars = self.siteregisters[sitename]
        port = pars['register_port']
        self.siteregister_stop(sitename,True)
        self.addSiteRegister(sitename,storage_path=pars['storage_path'],
                        heartbeat_options=pars['heartbeat_options'],
                        autorestore=pars['autorestore'],port=port)



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
        