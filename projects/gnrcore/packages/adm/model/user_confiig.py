#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import metadata,public_method
from gnr.core.gnrbag import Bag


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_config', pkey='id', name_long='!!User tblinfo', name_plural='!!User tblinfo')
        self.sysFields(tbl)
        tbl.column('user_group',name_long='!!Group').relation('group.code',relation_name='custom_info',mode='foreignkey')
        tbl.column('user_id',size='22' ,group='_',name_long='!!User').relation('user.id',relation_name='custom_info',
                                                                                mode='foreignkey',onDelete='cascade')
        tbl.column('pkg' ,size=':30',name_long='!!Pkg').relation('pkginfo.pkg',relation_name='rules',mode='foreignkey')
        tbl.column('tbl' ,size=':30',name_long='!!Tbl').relation('tblinfo.tbl_key',relation_name='rules',mode='foreignkey')
        
        tbl.column('tbl_permission' ,size=':20',name_long='!!Table permission',name_short='!!Permission')#values='read,ins,upd,del'

        tbl.column('qtree',size=':30',name_long='!!QTree')
        tbl.column('ftree',size=':30',name_long='!!FTree')

        tbl.column('forbidden_columns',name_long='!!Forbidden columns')
        tbl.column('forbidden_override',name_long='!!Override forbidden',name_short='Override')

        tbl.column('readonly_columns',name_long='!!ReadOnly columns')
        tbl.column('readonly_override',name_long='!!Override readony',name_short='Override')

        tbl.formulaColumn('rank',"""CAST(($tbl IS NOT NULL) AS int)*8+
                                    CAST(($pkg IS NOT NULL) AS int)*2+
                                    CAST(($user_id IS NOT NULL) AS int)*4+
                                    CAST(($user_group IS NOT NULL) AS int)*1""",dtype='L')


    def info_type_condition(self,info_type=None):
        info_type_condition = 'True'
        if info_type=='QTREE':
            info_type_condition = '$qtree IS NOT NULL'
        elif info_type=='FTREE':
            info_type_condition = '$ftree IS NOT NULL'
        elif info_type=='VIEW':
            info_type_condition = '$view_permission IS NOT NULL'
        elif info_type=='FORM':
            info_type_condition = '$form_permission IS NOT NULL'
        elif info_type=='COLS':
            info_type_condition = '$columns_permission IS NOT NULL'
        return info_type_condition

    def loadUserTblInfoRecord(self,info_type=None,pkg=None,
                            tbl=None,branch=None,user_id=None,
                            user_group=None):
        if tbl and not pkg:
            pkg = tbl.split('.')[0]
        user_group=user_group or self.db.currentEnv.get('user_group_code')
        user_id=user_id or self.db.currentEnv.get('user_id')
        
        f = self.query(where=""" %s AND
                            ($tbl IS NULL OR $tbl=:tbl) AND 
                            ($pkg IS NULL OR $pkg=:pkg) AND
                            ($user_id IS NULL OR $user_id=:user_id) AND 
                            ($user_group IS NULL OR $user_group=:user_group)
                            """ %self.info_type_condition(info_type),
                    
                    pkg=pkg,
                    tbl=tbl,
                    user_id=user_id,
                    user_group=user_group,
                    order_by='$rank desc',limit=1).fetch()
        return f[0] if f else None


    @metadata(order=1,title="!!Quick Fields Tree",default=1)
    def type_QTREE(self):
        return 'NO:No,0:Easy,1:Avarage,2:Expert,_RAW_:Raw'

    @metadata(order=2,title="!!Full Fields Tree",default=1)
    def type_FTREE(self):
        return 'NO:No,0:Easy,1:Avarage,2:Expert,_RAW_:Raw'


    def getTypeList(self,type):
        r = getattr(self,'type_%s' %type)()
        r = [elem.split(':') for elem in r.split(',')]
        return r

    @public_method
    def getCustomCodes(self,_querystring=None,_id=None,tbl=None,item_type=None,**kwargs):
        result = Bag()
        standard_codes = self.getTypeList(item_type)
        d = dict(standard_codes)
        if tbl:
            custom_codes = self.db.table('adm.tblinfo_item').query(where='$tbl=:t AND $item_type=:it AND $code NOT IN :c',
                                        t=tbl,it=item_type,c=d.keys(),columns='$code,$description').fetch()
            if custom_codes:
                for r in custom_codes:
                    standard_codes.append((r['code'],r['description']))
        d = dict(standard_codes)
        if _id:
            f = [(_id,d[_id])]
        else:
            chunk = _querystring.replace('*','').lower()
            f = filter(lambda c: (chunk in c[1].lower() or chunk in c[0].lower()),standard_codes)
        for i,r in enumerate(f):
            result.setItem('%s_%s' %(r[0],i),None,
               code=r[0],description=r[1],_pkey=r[0],caption=r[1])
        return result,dict(columns='code,description',headers='Code,Description')


    def trigger_onInserting(self,record):
        self.trigger_tblpkg(record)

    def trigger_onUpdating(self,record,old_record=None):
        self.trigger_tblpkg(record)

    def trigger_tblpkg(self,record):
        if record['tbl'] and not record['pkg']:
            record['pkg'] = record['tbl'].split('.')[0]

    def _col_auth(self,mode=None,row=None,result=None):
        fieldcols = '%s_columns' %mode
        fieldoverride = '%s_override' %mode
        columns = row.pop(fieldcols)
        override = row.pop(fieldoverride)
        columns = columns.split(',') if columns else []
        if columns or override:
            if override:
                result[fieldcols] = columns
            elif columns:
                current = result[fieldcols]
                current = set(current) if current else set()
                current.add(set(columns))
                result[fieldcols] = list(columns)

    def getInfoBag(self,pkg=None,tbl=None,user_id=None,user_group=None):
        if not pkg and tbl:
            pkg = tbl.split('.')[0]
        result = Bag()
        f = self.query(where="""($pkg IS NULL OR $pkg=:pkg) AND
                                ($tbl IS NULL OR $tbl=:tbl) AND
                                ($user_group IS NULL OR $user_group=:user_group) AND 
                                ($user_id IS NULL OR $user_id=:user_id)
                              """,pkg=pkg,tbl=tbl,user_group=user_group,user_id=user_id,
                              order_by='$rank ASC',columns="""$qtree,$ftree,$tbl_permission,
                                                               $forbidden_columns,
                                                               $forbidden_override,
                                                               $readonly_columns,
                                                               $readonly_override""",addPkeyColumn=False).fetch()
        for r in f:
            r = dict(r)
            self._col_auth('forbidden',r,result)
            self._col_auth('readonly',r,result)
            for k,v in r.items():
                if v is not None:
                    result[k] = v
        return result
