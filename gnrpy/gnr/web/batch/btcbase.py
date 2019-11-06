#!/usr/bin/env python
# encoding: utf-8
#
#btcbase.py
#
#Created by Francesco Porcari on 2010-10-16
#Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from datetime import datetime
from gnr.core.gnrlang import tracebackBag


class BaseResourceBatch(object):
    """Base resource class to create a :ref:`batch`"""
    batch_prefix = 'BB'
    batch_thermo_lines = 'batch_steps,batch_main,ts_loop'
    batch_title = 'My Batch Title'
    batch_cancellable = True
    batch_delay = 0.5
    batch_note = None
    batch_steps = None #'foo,bar'
    batch_dblog = False
    dialog_height = '200px'
    dialog_width = '300px'
    virtual_columns = None
    batch_local_cache = True

    batch_selection_where = None
    batch_selection_kwargs = dict()
    batch_selection_savedQuery= None

    def __init__(self, page=None, resource_table=None):
        self.page = page
        self.db = self.page.db
        self.tblobj = resource_table
        if self.tblobj:
            self.maintable = self.tblobj.fullname
        self.btc = self.page.btc
        self.results = Bag()
        self.batch_debug = Bag()
        self.batch_logtbl = self.db.table('sys.batch_log')
        self.batch_log_id = self.page.getUuid()
        self.records = dict()
        self.result_info = dict()
        self._pkeys = None
        self.selectedPkeys = None
        self.batch_parameters = dict()
        #self.mail_preference = self.page.site.getService('mail').getDefaultMailAccount()


    def __call__(self, batch_note=None, task_execution_record=None,**kwargs):
        parameters = kwargs.get('parameters',dict())
        self.batch_parameters = parameters.asDict(True) if isinstance(parameters, Bag) else parameters or {}
        self.batch_note = batch_note or self.batch_parameters.get('batch_note')
        self.task_execution_record = task_execution_record
        if self.batch_dblog:
            self.batch_logrecord = self.batch_logtbl.newrecord(id=self.batch_log_id,
                                batch_title=self.batch_title,tbl=self.tblobj.fullname,
                                start_ts=datetime.now(),notes=self.batch_note)
        try:
            with self.db.tempEnv(cacheInPage=self.batch_local_cache):
                self.run()
                result, result_attr = self.result_handler()
                self.btc.batch_complete(result=result, result_attr=result_attr)
            #self.page.setInClientData('')
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
            self.batch_log_write('Batch Aborted')
        except Exception, e:
            if task_execution_record:
                task_execution_record['is_error'] = True
                task_execution_record['errorbag'] = tracebackBag()
            elif self.page.isDeveloper():
                raise
            else:
                try:
                    self.btc.batch_error(error=str(e))
                    self.batch_log_write('Error in batch %s' %str(e))
                except Exception, e:
                    print e
                    raise
        finally:
            if self.batch_dblog:
                with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
                    self.batch_logrecord['logbag'] =  self.batch_debug
                    self.batch_logrecord['end_ts'] = datetime.now()
                    self.batch_logtbl.insert(self.batch_logrecord)
                    self.db.commit()
            if self.task_execution_record:
                self.task_execution_record['logbag'] = self.batch_debug

    def batch_debug_write(self,caption,value=None,**kwargs):
        self.batch_debug.setItem('r_%04i' %len(self.batch_debug),value,caption=caption,ts=datetime.now(),**kwargs)

    def batch_log_write(self,logtxt):
        self.btc.log_write(logtxt)

    def _pre_process(self):
        self.pre_process()

    def pre_process(self):
        """Hook method on initing of the batch execution"""
        pass
        
    def _post_process(self):
        self.post_process()
        try:
            self.db.autoCommit()
        except self.db.exceptions['missedCommit'] as e:
            self.page.log(str(e))


    def post_process(self):
        """Hook method after the batch execution"""
        pass

    def run(self):
        """Run the :ref:`batch`"""
        self.btc.batch_create(batch_id='%s_%s' % (self.batch_prefix, self.batch_log_id),
                              title=self.batch_title,
                              cancellable=self.batch_cancellable,
                              delay=self.batch_delay,
                              note=self.batch_note)
        self._pre_process()
        if self.batch_steps:
            self.call_steps()
        else:
            self.do()
        self._post_process()
    
    def call_steps(self,offset=1):
        steps = self.batch_steps.split(',')
        if len(steps)>1:
            steps = self.btc.thermo_wrapper(steps, 'btc_steps', message=self.get_step_caption,keep=True)
        for step in steps:
            step_handler = getattr(self, 'step_%s' % step)
            step_handler()
            for line_code in self.btc.line_codes[offset:]:
                self.btc.thermo_line_del(line_code)

    def storeResult(self, key, result, record=None, **info):
        """TODO
        
        :param key: TODO
        :param result: TODO
        :param record: TODO
        :param \*\* info: TODO"""
        self.results[key] = result
        self.records[key] = record
        self.result_info[key] = info

    def batchUpdate(self, updater=None, table=None, line_code=None, message=None,**kwargs):
        """Redefine the :meth:`batchUpdate() <gnr.sql.gnrsqltable.SqlTable.batchUpdate>` of the
        :ref:`gnrsqltable <library_gnrsqltable>` module. Allow to make an update of the database.
        For more information, check the :ref:`batchupdate` section
        
        :param updater: MANDATORY. It can be a dict() (if the batch is a :ref:`simple substitution
                        <batchupdate>`) or a method
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param where: the :ref:`sql_where` parameter
        :param line_code: TODO
        :param message: TODO"""
        table = table or self.maintable
        tblobj = self.db.table(table) 
        tblobj.batchUpdate(updater=updater,_pkeys=self.get_selection_pkeys() if ('where' not in kwargs) else None,
                           _wrapper=self.btc.thermo_wrapper,
                           _wrapperKwargs=dict(line_code=line_code or 'date',
                                               message=message or self.get_record_caption,
                                               tblobj=tblobj),**kwargs)

    def result_handler(self):
        """TODO"""
        return 'Execution completed', dict()
    
    def result_email(self,**mailpars):
        mailmanager = self.page.getService('mail')
        mailpars = mailpars or dict()
        mailpars.update(self.mail_preference.asDict(True))
        filepath =  getattr(self,'filepath',None) #qui ho il mio filepath
        # se avesse come opzione zip lo zipperesti qui
        #
        mailpars['attachments'] = [filepath] if filepath else None
        mailmanager.sendmail(**mailpars)
        return 'Mail sent', dict()
        

    def get_step_caption(self, item, progress, maximum, **kwargs):
        """TODO
        
        :param item: TODO
        :param progress: TODO
        :param maximum: TODO"""
        step_handler = getattr(self, 'step_%s' % item)
        return step_handler.__doc__

    def get_record_caption(self, item, progress, maximum, tblobj=None, **kwargs):
        """TODO
        
        :param item: TODO
        :param progress: TODO
        :param maximum: TODO
        :param tblobj: TODO"""
        tblobj = tblobj or self.tblobj
        if tblobj:
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item), progress, maximum)
        else:
            caption = '%i/%i' % (progress, maximum)
        return caption

    def do(self, **kwargs):
        """Hook method. It starts during the :meth:`run() <run>` method execution if you
        have defined the :ref:`batch_steps` webpage variable"""
        pass

    def defineSelection(self, selectionName=None, selectedRowidx=None, selectionFilterCb=None, sortBy=None):
        """TODO
        
        :param selectionName: TODO
        :param selectedRowidx: TODO
        :param selectionFilterCb: TODO
        :param sortBy: TODO"""
        self.selectionName = selectionName
        self.selectedRowidx = selectedRowidx
        self.selectionFilterCb = selectionFilterCb
        self.sortBy=sortBy

    def get_selection(self, columns=None):
        """TODO
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section"""
        selection = None
        selection_kwargs = dict()
        if self.batch_selection_kwargs:
            selection_kwargs.update(self.batch_selection_kwargs) 
        if columns:
            selection_kwargs['columns'] = columns

        if self.batch_selection_savedQuery:
            selection = self._selection_from_savedQuery(selection_kwargs)

        elif self.batch_selection_where:                
            selection = self.tblobj.query(where=self.batch_selection_where,**selection_kwargs).selection()

        elif hasattr(self,'selectionName'):
            selection = self.page.getUserSelection(selectionName=self.selectionName,
                                                    selectedRowidx=self.selectedRowidx, filterCb=self.selectionFilterCb,
                                                    table=self.tblobj,sortBy=self.sortBy,
                                                    **selection_kwargs)
        elif self.selectedPkeys:
            selection = self.tblobj.query(where='$%s IN :selectedPkeys' %self.tblobj.pkey,selectedPkeys=self.selectedPkeys,
                                            excludeDraft=False,excludeLogicalDeleted=False,
                                            ignorePartition=True,
                                            **selection_kwargs).selection()
        return selection

    def _selection_from_savedQuery(self,selection_kwargs):
        
        userobject_tbl = self.db.table('adm.userobject')
        where = userobject_tbl.loadUserObject(userObjectIdOrCode=self.batch_selection_savedQuery, 
                        objtype='query', tbl=self.tblobj.fullname)[0]
        if where['where']:
            limit = where['queryLimit']
            customOrderBy = where['customOrderBy']
            where = where['where']
            self._selection_from_savedQuery_fill_parameters(where)
            where,selection_kwargs = self.tblobj.sqlWhereFromBag(where, selection_kwargs)
            if customOrderBy:
                order_by = []
                for fieldpath,sorting in customOrderBy.digest('#v.fieldpath,#v.sorting'):
                    fieldpath = '$%s' %fieldpath if not fieldpath.startswith('@') else fieldpath
                    sorting = 'asc' if sorting else 'desc'
                    order_by.append('%s %s' %(fieldpath,sorting))
                selection_kwargs['order_by'] = ' , '.join(order_by)
            if limit:
                selection_kwargs['limit'] = limit
            return self.tblobj.query(where=where,**selection_kwargs).selection()


    def _selection_from_savedQuery_fill_parameters(self,wherebag):
        def fillpar(n):
            if n.value is None and n.attr.get('value_caption','').startswith('?'):
                bp_name = n.attr['value_caption'][1:].lower().replace(' ','_')
                if bp_name in self.batch_parameters:
                    n.value = self.batch_parameters[bp_name]
        wherebag.walk(fillpar)


    def get_records(self,for_update=None,virtual_columns=None):
        """TODO"""
        pkeys = self.get_selection_pkeys()
        for pkey in pkeys:
            yield self.get_record(pkey,for_update=for_update,virtual_columns=virtual_columns)

    def get_record(self, pkey, virtual_columns=None,for_update=None):
        """TODO
        
        :param pkey: the record :ref:`primary key <pkey>`
        :param virtual_columns: the :ref:`virtual_columns` webpage variable"""
        return self.tblobj.record(pkey=pkey, virtual_columns=virtual_columns or self.virtual_columns,for_update=for_update).output('bag')

    def get_selection_pkeys(self):
        """TODO"""
        if self._pkeys is None:
            selection = self.get_selection()
            self._pkeys = selection.output('pkeylist') if selection else []
        return self._pkeys

    #def rpc_selectionFilterCb(self,row):
    #    """override me"""
    #    return True

    def parameters_pane(self, pane, **kwargs):
        """Hook method. This method receives a :ref:`contentpane` through which you can build a
        :ref:`form` to get parameters from client
        
        :param pane: the contentPane"""
        pass

    def table_script_parameters_footer(self,pane,**kwargs):
        bar = pane.slotBar('*,cancelbtn,3,confirmbtn,3',_class='slotbar_dialog_footer')
        bar.cancelbtn.slotButton('!!Cancel',action='FIRE .cancel;')
        bar.confirmbtn.slotButton('!!Confirm', action='FIRE .confirm;')
        return bar
        
    def table_script_option_footer(self,pane,**kwargs):
        bar = pane.slotBar('*,cancelbtn,3,confirmbtn,3',_class='slotbar_dialog_footer')
        bar.cancelbtn.slotButton('!!Cancel',action='FIRE .cancel;')
        bar.confirmbtn.slotButton('!!Confirm', action='FIRE .confirm;')
        return bar
        

    def configuration_handleQueryPars(self,fb,table):
        wherepars = set()
        for code,pars in self.queryPars.digest('#k,#a'):
            autoTopic = False
            aliasTopic = None
            if code.endswith('*'):
                code = code[0:-1]
                autoTopic = code
            field = pars['field']
            tblobj = self.db.table(table)
            rc = tblobj.column(field).relatedColumn()
            wherepath = pars['relpath']
            colobj = tblobj.column(field)
            tblcol = colobj.table
            if colobj.name==tblcol.pkey:
                wdg = fb.dbSelect(value='^.wherepars_%s' %code,lbl=pars['lbl'],
                                    #attr_wdg='dbselect',attr_dbtable=rc.table.fullname,
                                    dbtable=table)
                aliasTopic = '%s_pkey' %tblcol.fullname.replace('.','_')
            elif pars['op'] == 'equal' and rc is not None:
                wdg = fb.dbSelect(value='^.wherepars_%s' %code,lbl=pars['lbl'],
                                    #attr_wdg='dbselect',attr_dbtable=rc.table.fullname,
                                    dbtable=rc.table.fullname)
                aliasTopic = '%s_pkey' %rc.table.fullname.replace('.','_')
            else:
                wdg = fb.textbox(value='^.wherepars_%s' %code,lbl=pars['lbl'])
            wherepars.add('wherepars_%s' %code)
            fb.data('.wherepars_%s' %code,pars.get('dflt'),wdg_tag=wdg.attributes['tag'],
                    wdg_dbtable=wdg.attributes.get('dbtable'),autoTopic=autoTopic,aliasTopic=aliasTopic)