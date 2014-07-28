#!/usr/bin/env python
# # -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'

    def rpc_checkPackages(self,pkgbag=None,**kwargs):
        pkgpkeys = ['%s/%s' %(prj,pkg) for prj,pkg in pkgbag.digest('#v.project,#v.pkg')]
        packages = self.db.table('uke.pkgtable').query(where='$package_identifier IN :identifiers',identifiers=pkgpkeys).fetchGrouped('package_identifier')
        for p in pkgbag.values():
            package_identifier = '%s/%s' %(p['project'],p['pkg'])
            tables = p.pop('tables')
            if package_identifier in packages:
                sent_tables = set(tables.split(','))
                curr_tables = set([t['name'] for t in packages[package_identifier]])
                tbl_to_add =  ','.join(list(sent_tables.difference(curr_tables)))
                tbl_to_del =  ','.join(list(curr_tables.difference(sent_tables)))
                if tbl_to_add or tbl_to_del:
                    command = 'Update'
                    tip = 'Table to add: %s. Table to remove: %s' %(tbl_to_add,tbl_to_del)
                else:
                    p['status'] = 'OK'
                    continue
            else:
                tip = 'Missing package'
                command = 'Register'
                tbl_to_add = tables
                tbl_to_del = ''
            p['status'] = """<a href="javascript:genro.publish('update_uke_pkg',{package_identifier:'%s',tables_to_add:'%s',tables_to_del:'%s'})" title="%s">%s</a>""" %(package_identifier,tbl_to_add,tbl_to_del,tip,command)
        return pkgbag

    def rpc_updatePackage(self,package_identifier=None,tables_to_add=None,tables_to_del=None):
        pkg_table = self.db.table('uke.package')
        if not pkg_table.existsRecord(package_identifier):
            prj_tbl = self.db.table('uke.project')
            project_code,pkg_code = package_identifier.split('/')
            if not prj_tbl.existsRecord(project_code):
                print 'project_code',project_code
                prj_tbl.insert(dict(code=project_code))
            pkg_table.insert(dict(code=pkg_code,project_code=project_code))
        pkgtable_table = self.db.table('uke.pkgtable')
        for t in tables_to_add.split(','):
            pkgtable_table.insert(dict(package_identifier=package_identifier,name=t))
        self.db.commit()

