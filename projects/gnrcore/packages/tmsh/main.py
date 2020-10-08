#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin
from gnr.core.gnrdecorator import extract_kwargs
import datetime

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Timesheet utilities',sqlschema='tmsh',sqlprefix=True,
                    name_short='Tmsh', name_long='Tmsh', name_full='Tmsh')
                    

    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            package = pkgNode.value
            if not package:
                continue
            tables = package['tables']
            tmsh_tables = [tblname for tblname in tables.keys() if tblname.endswith('_tmsh')]
            for tmshtblname in tmsh_tables:
                maintable = tmshtblname[:-5]
                resTbl = tables.getNode(maintable)
                tmshTbl = tables.getNode(tmshtblname)
                self._plugResourceTable(resTbl)
                self._plugTmshTable(pkgNode,tmshTbl)
                tmruleTbl = tables.getNode('{}_tmru'.format(maintable))
                if tmruleTbl:
                    self._plugTmruTable(pkgNode,resTbl,tmruleTbl)

    def _plugResourceTable(self,tblNode):
        tblNode.attr['tmsh_resource'] = True
        pkeyColNode = tblNode.value.getNode("columns.{}".format(tblNode.attr['pkey']))
        pkeyColNode.attr['onInserted'] = 'onInsertedResource'

    def _plugTmshTable(self,pkgNode,tblNode):
        fkeys = self._addPluggedForeignKey(pkgNode,tblNode,'tmsh_')
        tblNode.value.formulaColumn('is_allocated',"(COALESCE({}) IS NOT NULL)".format(','.join(fkeys)),dtype='B')

    def _addPluggedForeignKey(self,pkgNode,tblNode,prefix):
        tbl_mixins = self.db.model.mixins['tbl.{pkg}.{tbl}'.format(pkg=pkgNode.label,tbl=tblNode.label)]
        fkeys = []
        tblsrc = tblNode.value
        for m in [k for k in dir(tbl_mixins) if k.startswith(prefix)]:
            pars = getattr(tbl_mixins,m)()
            pars['code'] = m[5:]
            fkey = self._configureLinkedEntity(tblsrc,**pars)
            fkeys.append('${fkey}'.format(fkey=fkey))
        return fkeys
    
    def _configureLinkedEntity(self,src,code=None,caption=None,tbl=None,relation_name=None,**kwargs):
        pkg,tblname = tbl.split('.')
        tblsrc = self.db.model.src['packages.{pkg}.tables.{tblname}'.format(pkg=pkg,tblname=tblname)]
        tblattrs = tblsrc.attributes
        pkey = tblattrs.get('pkey')
        pkeycolAttrs = tblsrc.column(pkey).getAttr()
        rel = '{pkg}.{tblname}.{pkey}'.format(pkg=pkg,tblname=tblname,pkey=pkey)
        fkey = 'le_{pkg}_{tblname}_{pkey}'.format(pkg=pkg,tblname=tblname,pkey=pkey)
        caption = caption or tblattrs['name_long']
        if caption.startswith('!!'):
            caption = '[{caption}]'.format(caption=caption)
        entity = '{code}:{caption}'.format(code=code,caption=caption)
        linked_attrs = {'linked_{k}'.format(k=k):v for k,v in kwargs.items()}
        relation_name = relation_name or "{}_items".format(src.attributes['fullname'].split('.')[1])
        src.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,group='_',
                    name_long=tblattrs.get('name_long'),
                    size=pkeycolAttrs.get('size'),linked_entity=entity,
                    **linked_attrs).relation(rel, relation_name=relation_name,
                                        mode='foreignKey',onDelete='cascade',deferred=True)
        return fkey

    def _plugTmruTable(self,pkgNode,tblNode,timeRuleTbl):
        tbl = tblNode.value
        structure_field = tblNode.attr.get('structure_field')
        if structure_field:
            col =tbl['columns'].getNode(structure_field)
            colattr = col.attr
            relattr = col.value['relation'].attributes
            timeRuleTbl.value.column('structure_resource_id',size=colattr.get('size'),
                        dtype=colattr.get('dtype'),
                        group='*',name_long='!![en]Structure',
                    ).relation(relattr['related_column'],mode='foreignkey', onDelete_sql='cascade',
                                onDelete='cascade', relation_name='tmsh_timerules',
                    one_group='_',many_group='_',deferred=True) 

    def onApplicationInited(self):
        self.mixinMultidbMethods()

    def mixinMultidbMethods(self):
        db = self.application.db
        for pkg,pkgobj in db.packages.items():
            for tbl,tblobj in pkgobj.tables.items():
                if tblobj.attributes.get('tmsh_resource'):
                    instanceMixin(tblobj.dbtable, TmshResourceTable)


class TmshResourceTable(object):
    def timesheetTable(self):
        return self.db.table('{}_tmsh'.format(self.fullname))

    def touch_timesheet(self,record,old_record=None):
        self.tmsh_initializeTimesheet(record)

    def trigger_onInsertedResource(self,record,**kwargs):
        self.tmsh_initializeTimesheet(record)
    
    def tmsh_initializeTimesheet(self,record):
        tstable = self.timesheetTable()
        tsrec = tstable.newrecord(resource_id=record[self.pkey])
        tstable.insert(tsrec)


    @extract_kwargs(duration=True)
    def tmsh_allocate(self,resource_id=None,ts_start=None,ts_end=None,date_start=None,
                        time_start=None,date_end=None,time_end=None,duration_kwargs=None,
                        timezone=None,ts_max=None,best_fit=False,**kwargs):
        tmsh_table = self.timesheetTable()
        kw = tmsh_table.normalize(ts_start=ts_start,ts_end=ts_end,date_start=date_start,
                        time_start=time_start,date_end=date_end,time_end=time_end,
                        duration_kwargs=duration_kwargs,timezone=timezone)
        tmsh_table.autoAllocate(resource_id=resource_id,ts_start=kw['ts_start'],
                                            ts_end=kw['ts_end'],ts_max=ts_max,for_update=True,
                                            **kwargs)

    def tmsh_allocation(self,**kwargs):
        return self.timesheetTable().prepareAllocation(**kwargs)
                

    def timechoords(self,date_start=None,date_end=None,
                        time_start=None,time_end=None,
                        dtstart = None,dtend=None,
                        delta_minutes=None,delta_hour=None,
                        delta_days=None,
                        delta_month=None,
                        delta_year=None):
        result = {}
        result['date_start'] = date_start or dtstart.date()
        result['date_end'] = date_end or dtend.date()
        result['time_start'] = time_start or dtstart.time()
        result['time_end'] = time_end or dtend.time()
        result['dtstart'] = datetime.datetime.combine(result['date_start'],result['time_start'])
        result['dtend'] = datetime.datetime.combine(result['date_end'],result['time_end'])



                

class Table(GnrDboTable):
    pass
