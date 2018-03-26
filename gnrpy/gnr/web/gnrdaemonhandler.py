#!/usr/bin/env python2.7
# encoding: utf-8
#
from datetime import datetime
import logging
from multiprocessing import Process, log_to_stderr, get_logger, Pool, Queue, cpu_count, Manager
from gnr.web.gnrwsgisite_proxy.gnrsiteregister import GnrSiteRegisterServer
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrbag import Bag
from gnr.core.gnrsys import expandpath
from gnr.app.gnrconfig import gnrConfigPath
from gnr.app.gnrdeploy import PathResolver
import threading
from gnr.core.gnrstring import boolean
import atexit
import os
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
        self.logger = get_logger()
        self.logger.setLevel(loglevel or logging.DEBUG)

    def start(self):
        os.environ['no_proxy'] = '*'
        import urllib
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

class GnrRemoteProcess(object):

    def __init__(self, sitename=None, **kwargs):
        self.sitename = sitename

    def _makeSite(self):
        from gnr.web.gnrwsgisite import GnrWsgiSite
        self._site =  GnrWsgiSite(self.sitename,noclean=True)
        self._site_ts = datetime.now()

    @property
    def site(self):
        if not hasattr(self, '_site'):
            self._makeSite()
        else:
            last_start_ts = self._site.register.globalStore().getItem('RESTART_TS')
            if last_start_ts and last_start_ts > self._site_ts:
                return None
                #self._makeSite()
        return self._site

class GnrWorker(GnrRemoteProcess):
    def __init__(self,sitename=None,interval=None,loglevel=None, 
            batch_queue=None, lock=None, execution_dict=None,**kwargs):
        super(GnrWorker, self).__init__(sitename=sitename)
        self.batch_queue = batch_queue
        self.lock = lock
        self.execution_dict = execution_dict
        self.logger = get_logger()
        self.logger.setLevel(loglevel or logging.DEBUG)

    def run_batch(self, item_value):
        page_id = item_value.get('page_id')
        batch_kwargs = item_value.get('batch_kwargs')
        page = self.site.resource_loader.get_page_by_id(page_id)
        self.site.currentPage = page
        page.table_script_run(**batch_kwargs)
        self.site.currentPage = None

    def run_task(self, item_value):
        task = item_value
        task_id = task['id']
        page = self.site.dummyPage
        self.site.currentPage = page
        if not task['concurrent']:
            with self.lock:
                if task_id in self.execution_dict:
                    self.logger.info('Task {} already being executed by PID {} and not marked as concurrent'.format(task_id,self.execution_dict[task_id]))
                    return
                else:
                    self.execution_dict[task_id] = os.getpid()
        self.site.db.table('sys.task').runTask(task, page=page)
        self.execution_dict.pop(task_id, None)
        self.site.currentPage = None

    def start(self):
        queue = self.batch_queue
        self.logger.info('Starting cron process PID %s'%os.getpid())
        while True:
            try:
                item = queue.get()
                if not self.site:
                    # I have to restart, so i'll put the item on the queue
                    queue.put(item)
                    self.logger.info('PID {} will restart'.format(os.getpid()))
                    break
                if not item:
                    continue
                site = self.site
                item_type = item.get('type')
                item_value = item.get('value')
                handler = getattr(self, 'run_%s'%item_type,None)
                if handler:
                    handler(item_value)
            except Exception as e:
                import sys
                import traceback
                el = sys.exc_info()
                tb_text = traceback.format_exc()
                self.logger.error(tb_text)

class GnrCron(GnrRemoteProcess):
    def __init__(self,sitename=None,interval=None,loglevel=None, batch_queue=None, timespan=None,**kwargs):
        super(GnrCron, self).__init__(sitename=sitename)
        self.interval = interval
        self.batch_queue = batch_queue
        self._task_queue = []
        self.logger = get_logger()
        self.logger.setLevel(loglevel or logging.DEBUG)
        self.timespan = timespan or 60

    def _populateTaskQueue(self):
        self._task_ts = datetime.now()
        self._task_queue = self.site.db.table('sys.task').getNextExecutions(timespan=self.timespan)

    @property
    def changesInTask(self):
        last_task_ts = self.site.register.globalStore().getItem('TASK_TS')
        return last_task_ts and last_task_ts > self._task_ts

    @property
    def task_queue(self):
        if not self._task_queue or self.changesInTask:
            self._populateTaskQueue()
        return self._task_queue

    def start(self):
        site = None
        self.logger.info('Starting worker process PID %s'%os.getpid())
        while True:
            now = datetime.now()
            if not self.site:
                self.logger.info('Worker PID {} will restart'.format(os.getpid()))
                break
            task_queue = self.task_queue
            while task_queue:
                first_task = task_queue[0]
                if first_task['execution_ts'] <= now:
                    first_task = task_queue.pop(0)
                    self.batch_queue.put(dict(type='task',value=first_task['task']))
                else:
                    break
            time.sleep(self.interval)

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
        self.multiprocessing_manager =  Manager()
        self.batch_queues = dict()
        self.batch_processes = dict()
        self.cron_processes = dict()
        self.task_locks = dict()
        self.task_execution_dicts = dict()
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
            self.logger.info('Start daemon new socket {}'.format(self.socket))
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

    def on_reloader_restart(self, sitename=None):
        if sitename:
            self.restartBatchWorkers(sitename)

    def restartBatchWorkers(self, sitename=None):
        batch_processes = self.batch_processes.get(sitename,[])
        for process_number, process in enumerate(batch_processes):
            if process.is_alive():
                process.terminate()
        cron_process = self.cron_processes.get(sitename)
        if cron_process and not cron_process[0].is_alive():
            cron_process[0].terminate()

    @staticmethod
    def runWorkerProcess(sitename=None, batch_queue=None,
        lock=None, execution_dict=None,**kwargs):
        worker = GnrWorker(sitename=sitename,batch_queue=batch_queue,
            lock=lock, execution_dict=execution_dict,**kwargs)
        time.sleep(1)
        worker.start()


    def monitorSiteProcesses(self, sitename):
        while True:
            time.sleep(10)
            batch_processes = self.batch_processes.get(sitename,[])
            execution_dict = self.task_execution_dicts.get(sitename)
            batch_queue = self.batch_queues.get(sitename)
            lock = self.task_locks.get(sitename)
            for process_number, process in enumerate(batch_processes):
                if not process.is_alive():
                    self.batch_processes[sitename][process_number] = None
                    process = Process(name='btc_%s_%i' %(sitename, process_number+1),
                    target=self.runWorkerProcess, args=(sitename,batch_queue,lock, execution_dict))
                    process.daemon = True
                    process.start()
                    self.batch_processes[sitename][process_number] = process
            running_pids = [p.pid for p in batch_processes]
            for task_id, pid in execution_dict.items():
                if not pid in running_pids:
                    execution_dict.pop(task_id, None)
            cron_process = self.cron_processes.get(sitename)
            if cron_process:
                cron_process, interval = cron_process
            if cron_process and not cron_process.is_alive():
                batch_queue = self.batch_queues.get(sitename)
                cron_process = Process(name='cron_%s' %sitename,
                        target=self.runCronProcess, args=(sitename,interval,batch_queue))
                cron_process.daemon = True
                cron_process.start()
                self.cron_processes[sitename] = (cron_process, interval)

    @staticmethod
    def runCronProcess(sitename=None,interval=None, batch_queue=None,
        **kwargs):
        interval = interval or 60
        cron = GnrCron(sitename=sitename,interval=interval,batch_queue=batch_queue,**kwargs)
        time.sleep(1)
        cron.start()

    def startWorkerProcesses(self, sitename=None, batch_pars=None):
        self.batch_queues[sitename] = batch_queue = self.multiprocessing_manager.Queue()
        self.batch_processes[sitename] = []
        processes = batch_pars.get('processes', 'auto')
        if processes=='auto':
            processes = cpu_count()
        else:
            processes = int(processes)
        lock = self.task_locks[sitename] = self.multiprocessing_manager.Lock()
        execution_dict = self.task_execution_dicts[sitename] = self.multiprocessing_manager.dict()
        for i in range(processes):
            p = Process(name='btc_%s_%i' %(sitename, i+1),
                        target=self.runWorkerProcess, args=(sitename,batch_queue, lock, execution_dict))
            p.daemon = True
            p.start()
            self.batch_processes[sitename].append(p)
        interval = batch_pars.get('interval', 60)
        cron_process = Process(name='cron_%s' %sitename,
                        target=self.runCronProcess, args=(sitename,interval,batch_queue))
        cron_process.daemon = True
        cron_process.start()
        self.cron_processes[sitename] = (cron_process, interval)
        t = threading.Thread(target=self.monitorSiteProcesses, args=(sitename,))
        t.setDaemon(True)
        t.start()


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

    def getBatchProcessPars(self, sitename=None):
        siteconfig = PathResolver().get_siteconfig(sitename)
        batch_pars = siteconfig.getAttr('batch_processes')
        if not batch_pars or boolean(batch_pars.get('disabled')):
            return None
        return batch_pars

    def addSiteRegister(self,sitename,storage_path=None,autorestore=False,heartbeat_options=None,port=None):
        if not sitename in self.siteregisters:
            socket = os.path.join(self.sockets,'%s_daemon.sock' %sitename) if self.sockets else None
            batch_pars = self.getBatchProcessPars(sitename=sitename)
            if batch_pars:
                self.startWorkerProcesses(sitename=sitename, batch_pars=batch_pars)
            process_kwargs = dict(sitename=sitename,daemon_uri=self.main_uri,host=self.host,socket=socket
                                   ,hmac_key=self.hmac_key, storage_path=storage_path,autorestore=autorestore,
                                   port=port, batch_queue=self.batch_queues.get(sitename))
            childprocess = Process(name='sr_%s' %sitename, target=createSiteRegister,kwargs=process_kwargs)
            self.siteregisters[sitename] = dict(sitename=sitename,server_uri=False,
                                        register_uri=False,start_ts=datetime.now(),
                                        storage_path=storage_path,heartbeat_options=heartbeat_options,
                                        autorestore=autorestore)
            childprocess.daemon = True
            childprocess.start()
            hbprocess = None
            if heartbeat_options and not batch_pars:
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
        if sitename == '*':
            sitelist = self.siteregisters.keys()
        elif isinstance(sitename,basestring):
            sitelist = sitename.split(',')
        result = {}
        for k in sitelist:
            sitepars = self.siteregisters[k]
            try:
                with self.pyroProxy(sitepars['server_uri']) as proxy:
                    proxy.stop(saveStatus=saveStatus)
            except Exception as e:
                print str(e)
            self.onRegisterStop(k)
            result[k] = sitepars
        return result

    def siteregister_start(self,stopStatus):
        for sitename,pars in stopStatus.items():
            self.addSiteRegister(sitename,storage_path=pars['storage_path'],
                        heartbeat_options=pars['heartbeat_options'],
                        autorestore=pars['autorestore'],
                        port=pars['register_port'])

    def siteregister_restartServiceDaemon(self,sitename=None,service_name=None):
        self.restartServiceDaemon(sitename=sitename, service_name=service_name)

    def siteregister_restart(self,sitename=None,**kwargs):
        self.siteregister_start(self.siteregister_stop(sitename,True))



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
