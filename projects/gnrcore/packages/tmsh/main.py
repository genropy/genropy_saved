#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Timesheet utilities',sqlschema='tmsh',sqlprefix=True,
                    name_short='Tmsh', name_long='Tmsh', name_full='Tmsh')
                    

    def onBuildingDbobj(self):
        tbl_timerule = self.db.model.src['packages.tmsh.tables.timerule']
        timerule_fkeys = []
        for pkgNode in self.db.model.src['packages']:
            if not pkgNode.value:
                continue
            tables = pkgNode.value['tables']
            pkgname = pkgNode.label
            for tblNode in tables:
                tblname = tblNode.label
                if '{tblname}_tmsh'.format(tblname=tblname) in tables:
                    self._plugResourceTable(tblNode)
                    timerule_fkeys.append(self.configureEntity(tbl_timerule,tblNode.label,
                                        tbl='{pkgname}.{tblname}'.format(pkgname=pkgname,tblname=tblname),
                                        relation_name='timerules'))
                elif tblNode.label.endswith('_tmsh'):
                    self._addAllocationFkeys(pkgNode,tblNode)
        tbl_timerule.column('_row_count', dtype='L', name_long='!![en]Ord.', onInserting='setRowCounter',counter=True,
                            _counter_fkey=','.join(timerule_fkeys),
                            group='*',_sysfield=True)
        tbl_timerule.attributes.setdefault('order_by','$_row_count')
   

    def _plugResourceTable(self,tblNode):
        tblNode.attr['tmsh_resource'] = True
        pkeyColNode = tblNode.value.getNode("columns.{}".format(tblNode.attr['pkey']))
        pkeyColNode.attr['onInserted'] = 'onInsertedResource'

    def _addAllocationFkeys(self,pkgNode,tblNode):
        tbl = tblNode.label
        pkg = pkgNode.label
        tbl_mixins = self.db.model.mixins['tbl.{pkg}.{tbl}'.format(pkg=pkg,tbl=tbl)]
        fkeys = []
        tblsrc = tblNode.value
        for m in [k for k in dir(tbl_mixins) if k.startswith('tmsh_')]:
            pars = getattr(tbl_mixins,m)()
            pars['code'] = m[5:]
            fkey = self.configureEntity(tblsrc,**pars)
            fkeys.append('${fkey}'.format(fkey=fkey))
        tblsrc.formulaColumn('is_allocated',"(COALESCE({}) IS NOT NULL)".format(','.join(fkeys)),dtype='B')
        
    
    def configureEntity(self,src,code=None,caption=None,tbl=None,relation_name=None,**kwargs):
        pkg,tblname = tbl.split('.')
        tblsrc = self.db.model.src['packages.{pkg}.tables.{tblname}'.format(pkg=pkg,tblname=tblname)]
        tblattrs = tblsrc.attributes
        pkey = tblattrs.get('pkey')
        pkeycolAttrs = tblsrc.column(pkey).getAttr()
        rel = '{pkg}.{tblname}.{pkey}'.format(pkg=pkg,tblname=tblname,pkey=pkey)
        fkey = 'le_{tblname}_{pkey}'.format(tblname=tblname,pkey=pkey)
        curr_columns = src['columns']
        caption = caption or tblattrs['name_long']
        if caption.startswith('!!'):
            caption = '[{caption}]'.format(caption=caption)
        entity = '{code}:{caption}.format(code=code,caption=caption)
        linked_attrs = {'linked_{k}'.format(k=k):v for k,v in kwargs.items()}
        if fkey in curr_columns:
            colsrc = src['columns'][fkey]
            related_column = colsrc.getAttr('relation')['related_column']
            rpkg,rtbl,rpkey = related_column.split('.')
            if '{rpkg}.{rtbl}'.format(rpkg=rpkg,rtbl=rtbl) == tbl:
                colattr = colsrc.attributes
                entity = colattr['linked_entity'].split(',')
                entity.append(entity)
                colattr['linked_entity'] = ','.join(entity)
                colattr.update(**kwargs)#da fare
                return
            else:
                fkey = "le_{}".format(tbl.replace('.','_'))
        relation_name = relation_name or "{}_items".format(src.attributes['fullname'].split('.')[1])
        src.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,group='_',
                    name_long=tblattrs.get('name_long'),
                    size=pkeycolAttrs.get('size'),linked_entity=entity,
                    **linked_attrs).relation(rel, relation_name=relation_name,
                                        mode='foreignKey',onDelete='cascade')
        return fkey

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

    def onInsertedResource(self,record):
        self.initializeTimesheet(record)
    
    def initializeTimesheet(self,record):
        tstable = self.timesheetTable()
        tsrec = tstable.newrecord(resource_id=record[self.pkey])
        tstable.insert(tsrec)

    def touch_timesheet(self,record,old_record=None):
        self.initializeTimesheet(record)
    
                

class Table(GnrDboTable):
    pass
