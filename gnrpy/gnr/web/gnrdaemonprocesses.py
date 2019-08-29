#!/usr/bin/env python2.7
# encoding: utf-8
#

from builtins import range
#from builtins import object
from datetime import datetime
from multiprocessing import Process, get_logger, cpu_count
import threading
import os
import time

class GnrCronHandler(object):
    def __init__(self, parent, sitename=None, interval=None, 
        batch_queue=None, batch_pars=None, monitor_interval=None):
        self.parent = parent
        self.sitename = sitename
        self.batch_pars = batch_pars
        self.batch_queue = batch_queue
        self.interval = batch_pars.get('interval', 60)
        self.monitor_interval = monitor_interval or 10
        self.monitor_thread = None
        self.monitor_running = False

    def start(self):
        self.startCronProcess()
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self.monitorCronProcess)
        self.monitor_thread.setDaemon(True)
        self.monitor_thread.start()

    def terminate(self):
        if self.cron_process:
            self.cron_process.terminate()
        self.monitor_running = False

    def is_alive(self):
        if self.cron_process:
            self.cron_process.is_alive()

    def startCronProcess(self):
        self.cron_process = Process(name='cron_%s' %self.sitename,
                        target=self.runCronProcess, args=(self.sitename,
                            self.interval,self.batch_queue))
        self.cron_process.daemon = True
        self.cron_process.start()

    @staticmethod
    def runCronProcess(sitename=None,interval=None, batch_queue=None,
        **kwargs):
        interval = interval or 60
        cron = GnrCron(sitename=sitename,interval=interval,batch_queue=batch_queue,**kwargs)
        time.sleep(1)
        cron.start()

    def monitorCronProcess(self):
        counter = 0
        while self.monitor_running:
            time.sleep(1)
            counter +=1
            if counter%self.monitor_interval:
                continue
            counter = 0
            if self.cron_process and not self.cron_process.is_alive():
                self.startCronProcess()


class GnrWorkerPool(object):
    def __init__(self, parent, sitename=None, workers=None, interval=None,loglevel=None, 
            batch_queue=None, lock=None, execution_dict=None,
            monitor_interval=None, batch_pars=None, **kwargs):
        self.parent = parent
        self.sitename = sitename
        self.batch_queue = batch_queue
        self.multiprocessing_manager = self.parent.multiprocessing_manager
        self.lock = self.multiprocessing_manager.Lock()
        self.execution_dict = self.multiprocessing_manager.dict()
        self.logger = get_logger()
        self.batch_pars = batch_pars
        processes = self.batch_pars.get('processes', 'auto')
        if processes=='auto':
            processes = cpu_count()
        else:
            processes = int(processes)
        self.gnrworkers = [None for n in range(processes)]
        self.monitor_interval = monitor_interval or 10
        self.monitor_thread = None
        self.monitor_running = False

    def terminate(self):
        self.monitor_running=False
        for p in self.gnrworkers:
            if p and p.is_alive():
                p.terminate()

    def is_alive(self):
        for p in self.gnrworkers:
            if p and p.is_alive():
                return True
        return False


    def start(self):
        for process_number, process in enumerate(self.gnrworkers):
            if not process or not process.is_alive():
                self.gnrworkers[process_number] = self.startWorker(process_number)
        self.monitor_running = True
        monitor_thread = threading.Thread(target=self.monitorGnrWorkers)
        monitor_thread.setDaemon(True)
        monitor_thread.start()


    def startWorker(self, process_number):
        process = Process(name='btc_%s_%i' %(self.sitename, process_number+1),
                    target=self.runWorker, args=(self.sitename, self.batch_queue,
                    self.lock, self.execution_dict))
        process.daemon = True
        process.start()
        return process


    @staticmethod
    def runWorker(sitename=None, batch_queue=None,
        lock=None, execution_dict=None,**kwargs):
        worker = GnrWorker(sitename=sitename,batch_queue=batch_queue,
            lock=lock, execution_dict=execution_dict,**kwargs)
        time.sleep(1)
        worker.start()

    def monitorGnrWorkers(self):
        counter = 0
        while self.monitor_running:
            time.sleep(1)
            counter +=1
            if counter%self.monitor_interval:
                continue
            counter = 0
            running_pids = []
            for process_number, process in enumerate(self.gnrworkers):
                if not process or not process.is_alive():
                    process = self.startWorker(process_number)
                    self.gnrworkers[process_number] = process
                running_pids.append(process.pid)
            for task_id, pid in list(self.execution_dict.items()):
                if not pid in running_pids:
                    self.execution_dict.pop(task_id, None)

class GnrRemoteProcess(object):

    def __init__(self, sitename=None, **kwargs):
        self.sitename = sitename
        self.logger = get_logger()

    def _makeSite(self):
        from gnr.web.gnrwsgisite import GnrWsgiSite
        self._site =  GnrWsgiSite(self.sitename,noclean=True)
        self._site_ts = datetime.now()
        self.logger.debug('Created site for PID {}'.format(os.getpid()))
    
    @property
    def site(self):
        if not hasattr(self, '_site'):
            self._makeSite()
        else:
            last_start_ts = self._site.register.globalStore().getItem('RESTART_TS')
            if last_start_ts and last_start_ts > self._site_ts:
                self.logger.debug('Site restarted')
                return None
                #self._makeSite()
        return self._site

class GnrDaemonServiceManager(object):
    def __init__(self, parent=None, sitename = None, monitor_interval=None):
        self.parent = parent
        self.sitename = sitename
        self.multiprocessing_manager = self.parent.multiprocessing_manager
        self.services = dict()
        self.services_info = dict()
        self.services_monitor = dict()
        self.monitor_interval = monitor_interval or 10


    @property
    def site(self):
        if not hasattr(self, '_site'):
            from gnr.web.gnrwsgisite import GnrWsgiSite
            self._site = GnrWsgiSite(self.sitename, noclean=True)
        return self._site

    def terminate(self):
        self.monitor_running=False
        for p in list(self.services.values()):
            if p and p.is_alive():
                p.terminate()

    def is_alive(self):
        for p in list(self.services.values()):
            if p and p.is_alive():
                return True
        return False

    def reloadServices(self, service_identifier=None):
        def needReload(service):
            service_info = self.services_info.get(service['service_identifier']) or dict()
            if service['__mod_ts']!=service_info.get('__mod_ts'):
                return True
            return False
        where = '$daemon IS TRUE'
        if service_identifier:
            service_identifier = service_identifier.split(',')
            where = '%s AND $service_identifier =:service_identifier'%where
        service_tbl = self.site.db.table('sys.service')
        services = service_tbl.query('$service_identifier,$service_type,$service_name,$__mod_ts,$disabled',
            where=where).fetch()
        old_services = list(self.services_info.keys()) or service_identifier or []
        old_services = dict([(o,True) for o in old_services])
        for service in services:
            service_identifier = service['service_identifier']
            old_services.pop(service_identifier, None)
            if needReload(service):
                self.services_info[service_identifier] = dict(service)
                self.updateService(service_identifier)
        for service_identifier in old_services:
            self.services_info.pop(service_identifier, None)
            self.updateService(service_identifier)

    def updateService(self, service_identifier):
        process = self.services.get(service_identifier)
        if process and process.is_alive():
            self.stopService(service_identifier)



    def start(self):
        #time.sleep(1)

        #self.reloadServices()
        self.monitor_running = True
        monitor_thread = threading.Thread(target=self.monitorServices)
        monitor_thread.setDaemon(True)
        monitor_thread.start()

    def stopService(self, service_identifier):
        stop_thread = threading.Thread(target=self._stopService, args=(service_identifier,))
        stop_thread.setDaemon(True)
        stop_thread.start()

    def _stopService(self, service_identifier):
        process = self.services.get(service_identifier)
        if process and process.is_alive():
            running = self.services_monitor.get(service_identifier)
            if running:
                running.value = False
            process.join(30)
            if process.is_alive():
                process.terminate()

    def startService(self, service_identifier):
        service = self.services_info.get(service_identifier)
        if not service:
            return
        service_type = service['service_type']
        service_name = service['service_name']
        _running = self.services_monitor.setdefault(service_identifier, self.multiprocessing_manager.Value('b',True))
        _running.value = True
        process = Process(name='svc_%s_%s' %(self.sitename, service_identifier),
                    target=self.runService, args=(service_type, service_name, _running))
        process.daemon = True
        process.start()
        return process

    def runService(self, service_type, service_name, _running,**kwargs):
        service = GnrDaemonService(site=self.site,service_type=service_type,service_name=service_name,
            _running=_running,**kwargs)
        # potrei anche fare direttamente qui il server senza wrapper, vedere
        time.sleep(1)
        service.start()

    def monitorServices(self):
        counter = 0
        while self.monitor_running:
            time.sleep(1)
            counter +=1
            if counter%self.monitor_interval:
                continue
            self.reloadServices()
            counter = 0
            for service_identifier, service in list(self.services_info.items()):
                process = self.services.get(service_identifier)
                if service['disabled']:
                    continue
                if not process or not process.is_alive():
                    process = self.startService(service_identifier)
                    self.services[service_identifier] = process

class GnrDaemonService(object):
    def __init__(self, site=None, service_type=None, service_name=None, _running=None,**kwargs):
        self.site = site
        self.service = self.site.getService(service_type,service_name)
        self._running = _running

    def start(self):
        if hasattr(self.service,'run'):
            self.service.run(running=self._running)
        

class GnrWorker(GnrRemoteProcess):
    def __init__(self,sitename=None,interval=None,loglevel=None, 
            batch_queue=None, lock=None, execution_dict=None,**kwargs):
        super(GnrWorker, self).__init__(sitename=sitename)
        self.batch_queue = batch_queue
        self.lock = lock
        self.execution_dict = execution_dict
        self.logger = get_logger()
        
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
                    self.logger.warn('Task {} already being executed by PID {} and not marked as concurrent'.format(task_id,self.execution_dict[task_id]))
                    return
                else:
                    self.execution_dict[task_id] = os.getpid()
        self.site.db.table('sys.task').runTask(task, page=page)
        self.execution_dict.pop(task_id, None)
        self.site.currentPage = None

    def start(self):
        queue = self.batch_queue
        self.logger.debug('Starting worker process PID %s'%os.getpid())
        while True:
            try:
                item = queue.get()
                if not self.site:
                    # I have to restart, so i'll put the item on the queue
                    queue.put(item)
                    self.logger.debug('Worker PID {} will restart'.format(os.getpid()))
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
        self.logger.debug('Starting cron process PID %s'%os.getpid())
        while True:
            now = datetime.now()
            if not self.site:
                self.logger.debug('Cron PID {} will restart'.format(os.getpid()))
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
