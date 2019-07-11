# encoding: utf-8
from __future__ import print_function
from builtins import object
import os
import hashlib
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrdecorator import public_method
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('userobject', pkey='id', name_long='!!User Object',name_plural='!!User Objects',rowcaption='$code,$objtype',broadcast='objtype')
        self.sysFields(tbl, id=True, ins=True, upd=True)
        tbl.column('identifier',size=':120',indexed=True,sql_value="COALESCE(:tbl,:pkg,'')||:objtype||:code|| CASE WHEN :private THEN :userid ELSE '' END",unique=True)
        tbl.column('code', size=':40',name_long='!!Code', indexed='y') # a code unique for the same type / pkg / tbl
        tbl.column('objtype',size=':20', name_long='!!Object Type', indexed='y')
        tbl.column('pkg', size=':50',name_long='!!Package').relation('pkginfo.pkgid',relation_name='objects') # package code
        tbl.column('tbl', size=':50',name_long='!!Table').relation('tblinfo.tblid',relation_name='objects') # full table name: package.table
        tbl.column('userid',size=':50', name_long='!!User ID', indexed='y')
        tbl.column('description',size=':50', name_long='!!Description', indexed='y')
        tbl.column('notes', 'T', name_long='!!Notes')
        tbl.column('data', 'X', name_long='!!Data')
        tbl.column('authtags', 'T', name_long='!!Auth tags')
        tbl.column('private', 'B', name_long='!!Private')
        tbl.column('quicklist', 'B', name_long='!!Quicklist')
        tbl.column('flags', 'T', name_long='!!Flags')
        tbl.column('required_pkg', name_long='!!Required pkg')
        tbl.column('preview',name_long='!![it]Preview')
        tbl.formulaColumn('system_userobject',"$code LIKE :scode",var_scode='\_\_%%',dtype='B')
        tbl.pyColumn('resource_status',name_long='!!Resources',required_columns='$data')

    
    def pyColumn_resource_status(self,record=None,**kwargs):
        l = self.resourceStatus(record)
        if not l:
            return ''
        return '<br/>'.join(l)

    def resourceStatus(self,record):
        resources = []
        pkg = record['pkg']
        packages = self.db.application.packages
        current_data = record['data']
        record['data'] = None
        if not (record['tbl'] and packages[pkg]):
            return resources
        tbl = record['tbl'].split('.')[1]
        objtype = record['objtype']
        filename = '%s.xml' %(record['code'].lower().replace('.','_'))
        pkgkeys = list(packages.keys())
        page = self.db.currentPage
        respath = os.path.join(packages[pkg].packageFolder,'resources','tables',tbl,'userobjects',objtype,filename)
        if os.path.exists(respath):
            mainres = Bag(respath)
            color = 'darkgreen'
            if mainres['data'].toXml()!= current_data:
                color = 'red'
            resources.append('<span style="color:%s;">%s %s</span>' %(color,pkg,page.toText(mainres['__mod_ts'])))
        for pkgid in pkgkeys[pkgkeys.index(pkg)+1:]:
            if not packages[pkgid]:
                continue
            cust_resfilepath = os.path.join(packages[pkgid].packageFolder,'resources','tables','_packages',pkg,tbl,'userobjects',objtype,filename)
            if os.path.exists(cust_resfilepath):
                color = 'darkgreen'
                cust_res = Bag(cust_resfilepath)
                if cust_res['data'].toXml()!= current_data:
                    color = 'red'
                resources.append('<span style="color:%s;">%s %s</span>' %(color,pkgid, page.toText(cust_res['__mod_ts'])))
        return resources

    def trigger_onUpdating(self,record=None,old_record=None):
        self.updateRequiredPkg(record)

    def trigger_onInserting(self,record=None):
        self.updateRequiredPkg(record)
    
    def updateRequiredPkg(self,record):
        data = Bag(record['data'])
        required_pkg = set()
        def cb(n,**kwargs):
            if n.attr.get('_owner_package'):
                required_pkg.add(n.attr.get('_owner_package'))
        data.walk(cb)
        r = []
        record['required_pkg'] = ','.join([pkg for pkg in list(self.db.application.packages.keys()) if pkg in required_pkg]) if required_pkg else None
    

##################################

    def onDbUpgrade_checkResourceUserObject(self):
        self.checkResourceUserObject()

    def uo_identifier(self,record):
        return '%s%s%s' %(record['tbl'] or record['pkg'], record['objtype'],record['code'])
        
    def checkResourceUserObject(self):
        def cbattr(nodeattr):
            return not (nodeattr['file_ext'] !='directory' and not '%(sep)suserobjects%(sep)s' %{'sep':os.sep} in nodeattr['abs_path'])
        tableindex = self.db.tableTreeBag(packages='*')
        def cbwalk(node,**kwargs):
            if node.attr['file_ext'] !='directory':
                record = Bag(node.attr['abs_path'])
                record.pop('pkey')
                record.pop('id')
                identifier = self.uo_identifier(record)
                if  not self.checkDuplicate(code=record['code'],pkg=record['pkg'],tbl=record['tbl'],objtype=record['objtype']):
                    if record['tbl'] and not record['tbl'] in tableindex:
                        print('missing table',record['tbl'],'resource',node.attr['abs_path'])
                        return
                    print('inserting userobject %(code)s %(tbl)s %(pkg)s from resource' %record)
                    record['__ins_ts'] = None
                    record['__mod_ts'] = None
                    self.insert(record)
        for pkgid,pkgobj in list(self.db.application.packages.items()):
            table_resource_folder = os.path.join(pkgobj.packageFolder,'resources','tables') 
            d = DirectoryResolver(table_resource_folder,include='*.xml',callback=cbattr,processors=dict(xml=False))
            d().walk(cbwalk,_mode='deep')

    def listUserObject(self, objtype=None,pkg=None, tbl=None, userid=None, authtags=None, onlyQuicklist=None, flags=None):
        onlyQuicklist = onlyQuicklist or False
        def checkUserObj(r):
            if r['code'].startswith('__'):
                return False
            condition = (not r['private']) or (r['userid'] == userid)
            if onlyQuicklist:
                condition = condition and r['quicklist']
            if self.db.application.checkResourcePermission(r['authtags'], authtags):
                if condition:
                    return True
        where = []
        _flags = None
        if objtype:
            if ',' in objtype:
                objtype = objtype.split(',')
            if isinstance(objtype,list):
                where.append('$objtype IN :val_objtype')
            else:
                where.append('$objtype = :val_objtype')
        if tbl:
            where.append('$tbl = :val_tbl')
        if flags:
            where.append(' ($flags LIKE :_flags)  ')
            _flags = '%%'+flags+'%%'
        where = ' AND '.join(where)
        sel = self.query(columns='$id, $code, $objtype, $pkg, $tbl, $userid, $description, $authtags, $private, $quicklist, $flags',
                         where=where, order_by='$code',
                         val_objtype=objtype, val_tbl=tbl,_flags=_flags).selection()
        sel.filter(checkUserObj)
        return sel.output('dictlist')

    #PUBLIC METHODS 
    
    @public_method
    def loadUserObject(self, id=None, objtype=None,userObjectIdOrCode=None,**kwargs):
        if id:
            record = self.record(id, mode='record', ignoreMissing=True)

        elif userObjectIdOrCode:
            tbl = kwargs.get('tbl')
            pkg = kwargs.get('pkg')
            flags = kwargs.get('flags')
            record = self.record(where='$id=:userObjectIdOrCode OR ($code=:userObjectIdOrCode AND $tbl=:tbl AND $objtype=:objtype)',
                                userObjectIdOrCode=userObjectIdOrCode,
                                     objtype=objtype,ignoreMissing=True,
                                     mode='record',tbl=tbl)
            if not record['id'] and self.db.currentPage:
                #missing in table userobject
                page = self.db.currentPage
                record,path = page.getTableResourceContent(table=tbl,path='userobjects/%s/%s' %(objtype,userObjectIdOrCode),ext=['xml'])
                record = Bag(record)
        else:
            record = self.record(objtype=objtype, mode='record', 
                                 ignoreMissing=True,**kwargs)
        if not record:
            return None,None
        data = record.pop('data')
        metadata = record.asDict(ascii=True)
        metadata['pkey'] = metadata.get('id') or metadata['code']
        return data, metadata
    
    
    @public_method
    def deleteUserObject(self, pkey):
        self.delete(pkey)
        self.db.commit()

    @public_method
    def userObjectMenu(self,table=None, objtype=None,**kwargs): #th_listUserObject
        result = Bag()
        userobjects = self.listUserObject(objtype=objtype,userid=self.db.currentPage.user, tbl=table,
                                                authtags=self.db.currentPage.userTags,**kwargs)
        i = 0
        if len(userobjects)>0:
            for r in userobjects:
                r.pop('data',None)
                r['pkey'] = r.pop('id',None) or r.pop('code')
                r['caption'] = r['description'] or r['code'].title()
                r['draggable'] = True
                r['onDrag'] = """dragValues['dbrecords'] = {table:'adm.userobject',pkeys:['%(pkey)s'],objtype:'%(objtype)s',reftable:"%(tbl)s"}""" %r
                result.setItem(r['code'] or 'r_%i' % i, None, **dict(r))
                i+=1
        return result
            
    @public_method
    def saveUserObject(self, table=None,objtype=None,data=None,metadata=None,pkg=None,**kwargs):
        if table:
            pkg,tbl = table.split('.')
        pkey = metadata['pkey'] or metadata['id']
        if not metadata or not (metadata['code'] or pkey):
            return
        record = dict(data=data,objtype=objtype,
                    pkg=pkg,tbl=table,userid=self.db.currentPage.user,id=pkey,
                    code= metadata['code'],description=metadata['description'],private=metadata['private'] or False,
                    notes=metadata['notes'],flags=metadata['flags'],preview=metadata['preview'])
        self.insertOrUpdate(record)
        self.db.commit()
        return record['id'],record    

    @public_method
    def saveAsResource(self,pkeys=None):
        page = self.db.currentPage
        for pkey in pkeys:
            record = self.record(pkey=pkey).output('record')
            record.pop('id')
            required_pkg = record['required_pkg']
            filepath=os.path.join('userobjects',record['objtype'],record['code'].lower().replace('.','_'))
            respath = page.packageResourcePath(table=record['tbl'],filepath=filepath,
                                                forcedPackage=required_pkg.split(',')[-1] if required_pkg else None)
            record.toXml('%s.xml' %respath,autocreate=True)


                
        
