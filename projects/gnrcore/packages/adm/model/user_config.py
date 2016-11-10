#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import metadata,public_method
from gnr.core.gnrbag import Bag


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_config', pkey='ruleid', name_long='!!User config', name_plural='!!User config')
        self.sysFields(tbl,id=False)
        tbl.column('ruleid',size=':80')
        tbl.column('user_group',name_long='!!Group').relation('group.code',relation_name='custom_info',mode='foreignkey')
        tbl.column('username',size='22' ,group='_',name_long='!!User').relation('user.username',relation_name='custom_info',
                                                                              onDelete='cascade')
        tbl.column('pkgid' ,size=':30',name_long='!!Pkg').relation('pkginfo.pkgid',relation_name='rules',mode='foreignkey')
        tbl.column('tblid' ,size=':30',name_long='!!Tbl').relation('tblinfo.tblid',relation_name='rules',mode='foreignkey')
        
        tbl.column('data',dtype='X',name_long='!!Data',_sendback=True) #configuration data (tbl_permission,qtree,ftree,forbidden_cols,readonly_cols)

        #tbl.column('tbl_permission' ,size=':20',name_long='!!Table permission',name_short='!!Permission')#values='read,ins,upd,del'

       #tbl.column('qtree',size=':30',name_long='!!QTree')
       #tbl.column('ftree',size=':30',name_long='!!FTree')

       #tbl.column('forbidden_columns',name_long='!!Forbidden columns')
       #tbl.column('forbidden_override',dtype='B',name_long='!!Override forbidden',name_short='Override')

       #tbl.column('readonly_columns',name_long='!!ReadOnly columns')
       #tbl.column('readonly_override',dtype='B',name_long='!!Override readony',name_short='Override')
       #tbl.column('entity' ,size=':12',name_long='!!Entity')

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


    def trigger_onInserting(self,record):
        self.trigger_tblpkg(record)

    def trigger_onUpdating(self,record,old_record=None):
        self.trigger_tblpkg(record)

    def trigger_tblpkg(self,record):
        if record['tblid'] and not record['pkgid']:
            record['pkgid'] = record['tblid'].split('.')[0]


    def _updateColsPermission(self,cols_permission,updater):
        for cnode in cols_permission:
            updattr = updater.getAttr(cnode.label) or dict()
            last_readonly = cnode.attr.get('readonly')
            last_forbidden = cnode.attr.get('forbidden')
            if last_readonly is not None:
                cnode.attr['readonly_inherited'] = last_readonly
            if last_forbidden:
                cnode.attr['forbidden_inherited'] = last_forbidden
            cnode.attr['readonly'] = updattr.get('readonly')
            cnode.attr['forbidden'] = updattr.get('forbidden')

    def getInfoBag(self,pkg=None,tbl=None,user=None,user_group=None):
        if not pkg and tbl:
            pkg = tbl.split('.')[0]
        result = Bag()
        if tbl:
            tblobj =  self.db.table(tbl)
            cols_permission_base = Bag()
            for c in tblobj.columns.keys():
                cols_permission_base.setItem(c,None,colname=c)
            result['cols_permission'] = cols_permission_base

        f = self.query(where="""($pkgid IS NULL OR $pkgid=:pkg) AND
                                ($tblid IS NULL OR $tblid=:tbl) AND
                                ($user_group IS NULL OR $user_group=:user_group) AND 
                                ($username IS NULL OR $username=:user)
                              """,pkg=pkg,tbl=tbl,user_group=user_group,user=user,
                              order_by='$rank ASC',columns="""$data""",addPkeyColumn=False).fetch()
        for r in f:
            data = Bag(r['data'])
            for k,v in data.items():
                if k == 'cols_permission' and v:
                    self._updateColsPermission(result['cols_permission'],v)
                else:
                    if v is not None:
                        result[k] = v
        return result
