#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Organizer package',sqlschema='orgn',sqlprefix=True,
                    name_short='Organizer', name_long='Organizer', name_full='Organizer package')
                    
    def config_db(self, pkg):
        pass
        
    def sidebarPlugins(self):
        if self.getPreference('organizer_enabled'):
            return 'organizer','frameplugin_organizer'

    def onBuildingDbobj(self):
        annotaton_mixins = self.db.model.mixins['tbl.orgn.annotation']
        annotaton_src = self.db.model.src['packages.orgn.tables.annotation']
        config_entities = self.db.application.packages['orgn'].content['entities']
        for m in [k for k in dir(annotaton_mixins) if k.startswith('orgn_')]:
            pars = getattr(annotaton_mixins,m)()
            pars['code'] = m[5:]
            self.configureEntity(annotaton_src,**pars)
        if not config_entities:
            return
        for k,pars in config_entities.digest('#k,#a'):
            pars['code'] = k
            self.configureEntity(annotaton_src,**pars)


    def configureEntity(self,src,code=None,caption=None,tbl=None,pivot_date=None,**kwargs):
        pkg,tblname = tbl.split('.')
        tblsrc = self.db.model.src['packages.%s.tables.%s' %(pkg,tblname)]
        tblattrs = tblsrc.attributes
        pkey = tblattrs.get('pkey')
        pkeycolAttrs = tblsrc.column(pkey).getAttr()
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = 'le_%s_%s' %(tblname,pkey)
        curr_columns = src['columns']
        caption = caption or tblattrs['name_long']
        if caption.startswith('!!'):
            caption = '[%s]' %caption
        entity = '%s:%s' %(code,caption)
        linked_attrs = dict([('linked_%s' %k,v) for k,v in list(kwargs.items())])
        if fkey in curr_columns:
            colsrc = src['columns'][fkey]
            related_column = colsrc.getAttr('relation')['related_column']
            rpkg,rtbl,rpkey = related_column.split('.')
            if '%s.%s' %(rpkg,rtbl)==tbl:
                colattr = colsrc.attributes
                entity = colattr['linked_entity'].split(',')
                entity.append(entity)
                colattr['linked_entity'] = ','.join(entity)
                colattr.update(**kwargs)#da fare
                return
            else:
                fkey = 'le_%s' %tbl.replace('.','_')

        src.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,group='_',
                    name_long=tblattrs.get('name_long'),
                    size=pkeycolAttrs.get('size'),linked_entity=entity,
                    pivot_date=pivot_date,**linked_attrs).relation(rel,relation_name='annotations',mode='foreignKey',onDelete='cascade')


class Table(GnrDboTable):
    pass
