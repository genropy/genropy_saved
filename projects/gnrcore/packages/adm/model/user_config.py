#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime
from gnr.core.gnrdecorator import metadata,public_method
from gnr.core.gnrbag import Bag


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_config', pkey='ruleid', name_long='!!User config', name_plural='!!User config')
        self.sysFields(tbl,id=False)
        tbl.column('ruleid',size=':80')
        tbl.column('user_group',size=':15',name_long='!!Group').relation('group.code',relation_name='custom_info',mode='foreignkey')
        tbl.column('username',size=':32' ,group='_',name_long='!!User').relation('user.username',relation_name='custom_info',
                                                                              onDelete='cascade')
        tbl.column('pkgid' ,size=':30',name_long='!!Pkg').relation('pkginfo.pkgid',relation_name='rules',mode='foreignkey')
        tbl.column('tblid' ,size=':30',name_long='!!Tbl').relation('tblinfo.tblid',relation_name='rules',mode='foreignkey')
        
        tbl.column('data',dtype='X',name_long='!!Data',_sendback=True) #configuration data (tbl_permission,qtree,ftree,forbidden_cols,readonly_cols)
        
        tbl.formulaColumn('calc_pkgid',"""CASE WHEN $pkgid IS NOT NULL THEN $pkgid
                                               WHEN $tblid IS NOT NULL THEN split_part($tblid,'.',1)
                                               ELSE NULL END""")
        tbl.formulaColumn('rank',"""CAST(($tblid IS NOT NULL) AS int)*8+
                                    CAST(($pkgid IS NOT NULL) AS int)*2+
                                    CAST(($username IS NOT NULL) AS int)*4+
                                    CAST(($user_group IS NOT NULL) AS int)*1""",dtype='L')


    def pkeyValue(self,record=None):
        pkeylist = []
        for f in ('user_group','username'):
            v = record[f] or '*'
            pkeylist.append(v.replace('.','_'))
        if record['tblid']:
            tbllist = record['tblid'].split('.')
            record['pkgid'] = tbllist[0]
            pkeylist.extend(tbllist)
        elif record['pkgid']:
            pkeylist.append(record['pkgid'])
            pkeylist.append('*')
        return '/'.join(pkeylist)

    @public_method
    def newConfigRule(self,user_group=None,username=None,pkgid=None,tblid=None):
        if username and not user_group:
            user_group = self.db.table('adm.user').readColumns(columns='$group_code',where='$username=:u',u=username)
        if tblid:
            pkgid = tblid.split('.')[0]
        r = dict(user_group=user_group,username=username,pkgid=pkgid,tblid=tblid)
        pkeyValue = self.pkeyValue(r)
        if self.checkDuplicate(ruleid=pkeyValue):
            return pkeyValue
        else:
            self.insert(r)
            self.db.commit()
            return r['ruleid']


    @metadata(order=1,title="!!Quick Fields Tree",default=1)
    def type_QTREE(self):
        return '_NO_:No,0:Easy,1:Avarage,2:Expert,_RAW_:Raw'

    @metadata(order=2,title="!!Full Fields Tree",default=1)
    def type_FTREE(self):
        return '_NO_:No,0:Easy,1:Avarage,2:Expert,_RAW_:Raw'


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
            custom_codes = self.db.table('adm.tblinfo_item').query(where='$tblid=:t AND $item_type=:it AND $code NOT IN :c',
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

    def emptyTableUserConfigCache(self,record=None):
        site = getattr(self.db.application,'site',None)
        if site:
            with site.register.globalStore() as gs:
                expirebag = gs.getItem('tables_user_conf_expire_ts')
                if not expirebag:
                    expirebag = Bag()
                if record['tblid']:
                    key = record['tblid']
                elif record['pkgid']:
                    key = '%s.*' %record['pkgid']
                    expirebag[key] = Bag()
                else:
                    key = '*'
                    expirebag = Bag()
                expirebag[key] = datetime.now()
                gs.setItem('tables_user_conf_expire_ts',expirebag)

    def trigger_onInserting(self,record):
        self.trigger_common(record)

    def trigger_onInserted(self,record):
        self.emptyTableUserConfigCache(record)

    def trigger_onUpdating(self,record,old_record=None):
        self.trigger_common(record)

    def trigger_onUpdated(self,record,old_record=None):
        self.emptyTableUserConfigCache(record)

    def trigger_onDeleted(self,record):
        self.emptyTableUserConfigCache(record)

    def trigger_common(self,record):
        if record['tblid']:
            record['pkgid'] = None
        if record['username']:
            record['user_group'] = None

    def _updateColsPermission(self,cols_permission,updater,allcols,editMode):
        result = Bag()
        for colname in allcols:
            currattr = cols_permission.getAttr(colname) or dict()
            updattr = updater.getAttr(colname) or {}
            if currattr or updattr:
                if editMode:
                    currattr['colname'] = colname
                result.setItem(colname,None,_attributes=currattr)
                currattr = result.getAttr(colname)
                for permission in ('forbidden','readonly','blurred'):
                    last = currattr.get(permission)
                    upd = updattr.get(permission)
                    if editMode:
                        currattr[permission] = upd
                        if last is not None:
                            currattr['%s_inherited' %permission] = last
                    else:
                        currattr[permission] = upd if upd is not None else last
        return result

    def getInfoBag(self,pkg=None,tbl=None,user=None,user_group=None,_editMode=False):
        result = Bag()
        if tbl:
            pkg = tbl.split('.')[0]
            tblobj =  self.db.table(tbl)
            cols_permission_base = Bag()
            allcols = tblobj.columns.keys() + tblobj.model.virtual_columns.keys()
            result['cols_permission'] = cols_permission_base
        if user and not user_group:
            user_group = self.db.table('adm.user').readColumns(where='$username=:u',u=user,columns='$group_code')
        f = self.query(where="""($pkgid IS NULL OR $pkgid=:pkg) AND
                                ($tblid IS NULL OR $tblid=:tbl) AND
                                ($user_group IS NULL OR $user_group=:user_group) AND 
                                ($username IS NULL OR $username=:user)
                              """,pkg=pkg,tbl=tbl,user_group=user_group,user=user,
                              order_by='$rank ASC',columns="""$data""").fetch()
        for r in f:
            data = Bag(r['data'])
            last_permissions = data.pop('cols_permission')
            if tbl:
                result['cols_permission'] = self._updateColsPermission(result['cols_permission'],
                                                                        last_permissions or Bag(),
                                                                        allcols,_editMode)
            for k,v in data.items():
                if v is not None:
                    result[k] = v
        return result

    def onLoading_common(self, record, newrecord, loadingParameters, recInfo):
        if record['tblid']:
            current_full_data = self.getInfoBag(pkg=record['pkgid'],tbl=record['tblid'],
                                                user=record['username'],
                                                    user_group=record['user_group'],
                                                    _editMode=True)
            record['data.cols_permission'] = current_full_data['cols_permission']
            record['$current_cols'] = self._colsPickerStore(record['tblid'])
            record['$allPermissions'] = self.db.table(record['tblid']).availablePermissions
        else:
            record['$allPermissions'] = self.availablePermissions

    def _colsPickerStore(self,table=None):
        tblobj = self.db.table(table)
        result = Bag()
        for field,colobj in tblobj.model.columns.items():
            colattr = colobj.attributes
            result.setItem(field,None,colname=field,name_long=colattr.get('name_long'),
                                    datatype=colattr.get('dtype','T'),_pkey=field)

        for field,colobj in tblobj.model.virtual_columns.items():
            colattr = colobj.attributes
            result.setItem(field,None,colname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T'),_customClasses='virtualCol',_pkey=field)
        return result

