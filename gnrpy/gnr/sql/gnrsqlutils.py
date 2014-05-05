#!/usr/bin/env python
# encoding: utf-8
#
# gnrsqlutils.py
#
# Created by Saverio Porcari on 2007-09-20.
# Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core import gnrlist
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import GnrNonExistingDbException

class ModelExtractor(object):
    """TODO"""
    def __init__(self, dbroot):
        self.dbroot = dbroot
        
    def extractModelSrc(self, root):
        """Call the :meth:`buildSchemata()` and :meth:`buildRelations()` methods.
        Return the root
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` documentation section."""
        self.buildSchemata(root)
        self.buildRelations(root)
        return root
        
    def buildSchemata(self, root):
        """TODO
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` documentation section."""
        elements = self.dbroot.adapter.listElements('schemata')
        for pkg_name in elements:
            pkg = root.package(pkg_name, sqlschema=pkg_name, sqlprefix='')
            self.buildTables(pkg, pkg_name)
            
    def buildTables(self, pkg, pkg_name):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param pkg_name: the:ref:`package <packages>` name"""
        elements = self.dbroot.adapter.listElements('tables', schema=pkg_name)
        for tbl_name in elements:
            tbl = pkg.table(tbl_name)
            self.buildColumns(tbl, pkg_name, tbl_name)
            self.buildIndexes(tbl, pkg_name, tbl_name)
            
    def buildColumns(self, tbl, pkg_name, tbl_name):
        """TODO
        
        :param tbl: the :ref:`table` object
        :param pkg_name: the name of the package. For more information, check the
                         :ref:`packages` documentation page
        :param tbl_name: the name of the database :ref:`table`"""
        columns = list(self.dbroot.adapter.getColInfo(schema=pkg_name, table=tbl_name))
        gnrlist.sortByItem(columns, 'position')
        
        for col_dict in columns:
            col_dict.pop('position')
            colname = col_dict.pop('name')
            length = col_dict.pop('length', 0)
            decimals = col_dict.pop('decimals', 0)
            dtype = col_dict['dtype']
            if dtype == 'A':
                col_dict['size'] = '0:%s' % length
            elif dtype == 'C':
                col_dict['dtype'] = 'A'
                col_dict['size'] = length
            col = tbl.column(colname, **dict([(k, v) for k, v in col_dict.items() if not k.startswith('_')]))
        pkey = self.dbroot.adapter.getPkey(schema=pkg_name, table=tbl_name)
        if len(pkey) == 1:
            tbl.parentNode.setAttr(pkey=pkey[0])
        elif len(pkey) > 1:
            pass #multiple pkey
        else:
            pass #there's no pkey
        pass
        
    def buildIndexes(self, tbl, pkg_name, tbl_name):
        """TODO
        
        :param tbl: the :ref:`table` object
        :param pkg_name: the name of the package. For more information, check the
                         :ref:`packages` documentation page
        :param tbl_name: the name of the database :ref:`table`"""
        for ind in self.dbroot.adapter.getIndexesForTable(schema=pkg_name, table=tbl_name):
            if not ind['primary']:
                tbl.index(ind['columns'], name=ind['name'], unique=ind['unique'])
                
    def buildRelations(self, root):
        """TODO
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` documentation section."""
        relations = self.dbroot.adapter.relations()
        for (
        many_rel_name, many_schema, many_table, many_cols, one_rel_name, one_schema, one_table, one_cols, upd_rule) in relations:
            #one_rel_name = self.relName(ref, tbl)
            many_field = many_cols[0]
            one_field = one_cols[0]
            
            fld = root['packages.%s.tables.%s.columns.%s' % (many_schema, many_table, many_field)]
            fld.relation('%s.%s.%s' % (one_schema, one_table, one_field))
            
    def buildViews(self):
        """TODO"""
        elements = self.dbroot.adapter.listElements('views', schema=self.schema)
        children = Bag(self.children)
        for element in elements:
            if not element in children:
                children.setItem(element, None, tag='view')
        return SqlTableList(parent=self.structparent, name=self.name, attrs=self.attrs, children=children)
            
class SqlModelChecker(object):
    """Keep a database aligned with its logical structure in the GnrSqlDb.
    If there is any change in the modelobj, database is automatically updated."""
    
    def __init__(self, db):
        self.db = db
        
    def checkDb(self):
        """Return a list of instructions for the database building"""
        create_db = False
        self.changes = []
        self.bagChanges = Bag()
        try:
            self.actual_schemata = self.db.adapter.listElements('schemata')
        except GnrNonExistingDbException, exc:
            self.actual_schemata = []
            self.actual_tables = {}
            self.actual_views = {}
            self.actual_relations = {}
            self.unique_constraints = Bag()
            self.changes.append(self.db.adapter.createDbSql(exc.dbname, 'UNICODE'))
            create_db = True
        if not create_db:
            self.actual_tables = dict(
                    [(k, self.db.adapter.listElements('tables', schema=k)) for k in self.actual_schemata])
            self.actual_views = dict(
                    [(k, self.db.adapter.listElements('views', schema=k)) for k in self.actual_schemata])
            actual_relations = self.db.adapter.relations()
            self.actual_relations = {}
            for r in actual_relations:
                self.actual_relations.setdefault('%s.%s' % (r[1], r[2]), []).append(r)
            self.unique_constraints = self.db.adapter.getTableContraints()
        for pkg in self.db.packages.values():
            #print '----------checking %s----------'%pkg.name
            self._checkPackage(pkg)
        self._checkAllRelations()
        return [x for x in self.changes if x]

    def addExtesions(self):
        try:
            extensions = self.db.application.config['db?extensions']
            if extensions:
                self.db.adapter.createExtension(extensions)
        except Exception,e:
            print 'Error in adding extensions',e
        
    def _checkPackage(self, pkg):
        """Check if the current package is contained by a not defined schema and then call the
        :meth:`_checkTable()` method for each table. Return a list containing sql statements
        
        :param pkg: the :ref:`package <packages>` object"""
        self._checkSqlSchema(pkg)
        if pkg.tables:
            for tbl in pkg.tables.values():
                #print '----------checking table %s----------'%tbl.name
                self._checkSqlSchema(tbl)
                if tbl.sqlname in self.actual_tables.get(tbl.sqlschema, []):
                    tablechanges = self._checkTable(tbl)
                else:
                    tablechanges = self._buildTable(tbl)#Create sql commands to BUILD the missing table
                if tablechanges:
                    self.bagChanges.setItem('%s.%s' % (tbl.pkg.name, tbl.name), None,
                                            changes='\n'.join([ch for ch in tablechanges if ch]))
                                            
                    #views = node.value['views']
                    #if views:
                    #for viewnode in views:
                    #tbl_schema = self._checkSqlSchema(sql, node, pkg_schema)
                    #if self.sqlName(viewnode) in self.actual_views.get(tbl_schema, []):
                    #sql.extend(self._checkView(viewnode, tbl_schema))
                    #else:
                    #sql.extend(self._buildView(viewnode, tbl_schema))
                    
    def _checkSqlSchema(self, obj):
        """If the package/table/view is defined in a new schema that's not in the actual_schemata
        the new schema is created and its name is appended to self.actual_schemata. Return the
        schema name"""
        sqlschema = obj.sqlschema
        if sqlschema and not (sqlschema in self.actual_schemata) and not (sqlschema == self.db.main_schema):
            change = self.db.adapter.createSchemaSql(sqlschema)
            self.changes.append(change)
            self.bagChanges.setItem(obj.name, None, changes=change)
            self.actual_schemata.append(sqlschema)
            
    def _checkTable(self, tbl):
        """Check if any column has been changed and then build the sql statements for
        adding/deleting/editing table's columns calling the :meth:`_buildColumn()` method.
        
        :param tbl: the :ref:`table` object"""
        tablechanges = []
        tableindexes = self.db.adapter.getIndexesForTable(schema=tbl.sqlschema, table=tbl.sqlname)
        dbindexes = dict([(c['name'], c) for c in tableindexes])
        columnsindexes = dict([(c['columns'], c) for c in tableindexes])
        tblattr = tbl.attributes
        if tbl.columns:
            dbcolumns = dict(
                    [(c['name'], c) for c in self.db.adapter.getColInfo(schema=tbl.sqlschema, table=tbl.sqlname)])
            for col in tbl.columns.values():
                if col.sqlname in dbcolumns:
                    #it there's the column it should check if has been edited.
                    new_dtype = col.attributes['dtype']
                    new_size = col.attributes.get('size')
                    new_unique = col.attributes.get('unique')
                    old_dtype = dbcolumns[col.sqlname]['dtype']
                    old_size = dbcolumns[col.sqlname].get('size')
                    old_unique = self.unique_constraints['%s.%s.%s'%(tbl.sqlschema,tbl.sqlname,col.sqlname)]
                    if not self.unique_constraints and col.sqlname in columnsindexes:
                        if tblattr['pkey']==col.sqlname:
                            old_unique = new_unique
                        else:
                            old_unique = columnsindexes[col.sqlname].get('unique')
                    if new_dtype == 'A' and not new_size:
                        new_dtype = 'T'
                    if new_dtype == 'A' and not ':' in new_size:
                        new_dtype = 'C'
                    if new_size and ':' in new_size:
                        t1, t2 = new_size.split(':')
                        new_size = '%s:%s' % (t1 or '0', t2)
                    if new_size and new_dtype == 'N' and not ',' in new_size:
                        new_size = '%s,0' % new_size
                    elif new_dtype in ('X', 'Z', 'P') and old_dtype == 'T':
                        pass
                    elif new_dtype != old_dtype or new_size != old_size or bool(old_unique)!=bool(new_unique):
                        if (new_dtype != old_dtype or new_size != old_size):
                            change = self._alterColumnType(col, new_dtype, new_size)
                            self.changes.append(change)
                        if bool(old_unique)!=bool(new_unique):
                            self.changes.append(self._alterUnique(col,new_unique,old_unique))
                        #sql.extend(self.checkColumn(colnode, dbcolumns[self.sqlName(colnode)]))
                else:
                    change = self._buildColumn(col)
                    self.changes.append(change)
                    tablechanges.append(change)
                    self.bagChanges.setItem('%s.%s.columns.%s' % (tbl.pkg.name, tbl.name, col.name), None,
                                            changes=change)
                                            
        if tbl.indexes:
            for idx in tbl.indexes.values():
                if (idx.sqlname.endswith('_idx') and idx.sqlname[0:-4] in dbindexes):

                    change = self.db.adapter.dropIndex(idx.sqlname[0:-4][:63], sqlschema=tbl.sqlschema)
                    if change:
                        self.changes.append(change)
                        tablechanges.append(change)
                        self.bagChanges.setItem('%s.%s.indexes.%s' % (tbl.pkg.name, tbl.name, idx.sqlname), None,
                                                changes=change)
                                                
                if idx.sqlname[:63] in dbindexes:
                    pass
                else:
                    icols = idx.getAttr('columns')
                    icols = ','.join([tbl.column(col.strip()).sqlname for col in icols.split(',')])
                    unique = idx.getAttr('unique')
                    change = self._buildIndex(tbl.sqlname, idx.sqlname, icols, sqlschema=tbl.sqlschema, unique=unique,
                                              pkey=tbl.pkey)
                    if change:
                        self.changes.append(change)
                        tablechanges.append(change)
                        self.bagChanges.setItem('%s.%s.indexes.%s' % (tbl.pkg.name, tbl.name, idx.sqlname), None,
                                                changes=change)
        return tablechanges
        
    def _checkAllRelations(self):
        for pkg in self.db.packages.values():
            for tbl in pkg.tables.values():
                self._checkTblRelations(tbl)
                
    def _checkTblRelations(self, tbl):
        if not tbl.relations:
            return
        tbl_actual_rels = self.actual_relations.get(tbl.sqlfullname, [])[
                          :] #get all db foreignkey of the current table
        relations = [rel for rel in tbl.relations.digest('#a.joiner') if rel]
        for rel in relations:
            if rel.get('foreignkey'): # link has foreignkey constraint
                o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql = self._relationToSqlNames(rel)
                on_up = self._onStatementToSql(rel.get('onUpdate_sql')) or 'NO ACTION'
                on_del = self._onStatementToSql(rel.get('onDelete_sql')) or 'NO ACTION'
                init_deferred = self._deferredToSql(rel.get('deferred'))
                existing = False
                tobuild = True
                
                for actual_rel in tbl_actual_rels:
                    if actual_rel[3][0] == m_fld_sql: #if db foreignkey is on current col
                        linkto_sql = '%s.%s' % (actual_rel[5], actual_rel[6])
                        if linkto_sql == '%s.%s' % (
                        o_pkg_sql, o_tbl_sql): #if db foreignkey link on current many table
                            if actual_rel[7][0] == o_fld_sql:#if db foreignkey link on current many field
                                existing = True
                                tobuild = False
                                tbl_actual_rels.pop(tbl_actual_rels.index(actual_rel))
                                if actual_rel[8] != on_up:
                                    tobuild = True
                                    break
                                if actual_rel[9] != on_del:
                                    tobuild = True
                                    break
                                if (actual_rel[10] == 'YES' and not rel.get('deferred')) or (
                                actual_rel[10] == 'NO' and  rel.get('deferred')):
                                    tobuild = True
                                    break
                                    
                if tobuild:
                    if existing:
                        change = self._dropForeignKey(m_pkg_sql, m_tbl_sql, m_fld_sql, actual_name=actual_rel[0])
                        self.changes.append(change)
                        self.bagChanges.setItem(
                                '%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql))
                                , None, changes=change)
                        prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
                        self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None,
                                                changes='%s\n%s' % (prevchanges, change))
                    change = self._buildForeignKey(o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql,
                                                   on_up, on_del, init_deferred)
                    self.changes.append(change)
                    self.bagChanges.setItem(
                            '%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql)),
                            None, changes=change)
                    prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
                    self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None,
                                            changes='%s\n%s' % (prevchanges, change))
        for remaining_relation in tbl_actual_rels:
            m_pkg_sql = remaining_relation[1]
            m_tbl_sql = remaining_relation[2]
            m_fld_sql = remaining_relation[3][0]
            change = self._dropForeignKey(m_pkg_sql, m_tbl_sql, m_fld_sql,actual_name=remaining_relation[0])
            self.changes.append(change)
            self.bagChanges.setItem('%s.%s.relations.%s' % (tbl.pkg.name, tbl.name, 'fk_%s_%s' % (m_tbl_sql, m_fld_sql)), None, changes=change)
            prevchanges = self.bagChanges.getAttr('%s.%s' % (tbl.pkg.name, tbl.name), 'changes')
            self.bagChanges.setAttr('%s.%s' % (tbl.pkg.name, tbl.name), None, changes='%s\n%s' % (prevchanges, change))
                    
    def _onStatementToSql(self, command):
        if not command: return None
        command = command.upper()
        if command in ('R', 'RESTRICT'):
            return 'RESTRICT'
        elif command in ('C', 'CASCADE'):
            return 'CASCADE'
        elif command in ('N', 'NO ACTION'):
            return 'NO ACTION'
        elif command in ('SN', 'SETNULL', 'SET NULL'):
            return 'SET NULL'
        elif command in ('SD', 'SETDEFAULT', 'SET DEFAULT'):
            return 'SET DEFAULT'
            
    def _deferredToSql(self, command):
        if command == None:
            return None
        if command == True:
            return 'DEFERRABLE INITIALLY DEFERRED'
        if command == False:
            return 'DEFERRABLE INITIALLY IMMEDIATE'
            
    def _relationToSqlNames(self, rel):
        o_pkg, o_tbl, o_fld = rel['one_relation'].split('.')
        m_pkg, m_tbl, m_fld = rel['many_relation'].split('.')
        
        m_tbl = self.db.table('%s.%s' % (m_pkg, m_tbl)).model
        
        m_pkg_sql = m_tbl.sqlschema
        m_tbl_sql = m_tbl.sqlname
        m_fld_sql = m_tbl.column(m_fld).sqlname
        
        o_tbl = self.db.table('%s.%s' % (o_pkg, o_tbl)).model
        
        o_pkg_sql = o_tbl.sqlschema
        o_tbl_sql = o_tbl.sqlname
        o_fld_sql = o_tbl.column(o_fld).sqlname
        
        return o_pkg_sql, o_tbl_sql, o_fld_sql, m_pkg_sql, m_tbl_sql, m_fld_sql
        
    def _buildTable(self, tbl):
        """Prepare the sql statement list for adding the new table and its indexes.
        Return the statement.
        """
        tablechanges = []
        change = self._sqlTable(tbl)
        self.changes.append(change)
        tablechanges.append(change)
        self.bagChanges.setItem('%s.%s' % (tbl.pkg.name, tbl.name), None, changes=change)
        
        changes, bagindexes = self._sqlTableIndexes(tbl)
        self.changes.extend(changes)
        tablechanges.extend(changes)
        
        self.bagChanges['%s.%s.indexes' % (tbl.pkg.name, tbl.name)] = bagindexes
        
        return tablechanges
        
    def _buildView(self, node, sqlschema=None):
        """Prepare the sql statement for adding the new view and return it"""
        sql = []
        sql.append(self.sqlView(node, sqlschema=sqlschema))
        return sql
        
    def _buildColumn(self, col):
        """Prepare the sql statement for adding the new column to the given table and return it"""
        return 'ALTER TABLE %s ADD COLUMN %s' % (col.table.sqlfullname, self._sqlColumn(col))
        
    def _alterColumnType(self, col, new_dtype, new_size=None):
        """Prepare the sql statement for altering the type of a given column and return it"""
        sqlType = self.db.adapter.columnSqlType(new_dtype, new_size)
        usedColumn = col.table.dbtable.query(where='%s IS NOT NULL' %col.sqlname).count()>0
        if usedColumn or col.dtype == 'T' and col.dtype ==new_dtype:
            return 'ALTER TABLE %s ALTER COLUMN %s TYPE %s' % (col.table.sqlfullname, col.sqlname, sqlType)
        else:
            return '; '.join(['ALTER TABLE %s DROP COLUMN %s' % (col.table.sqlfullname, col.sqlname) ,self._buildColumn(col)])
        
    def _alterUnique(self, col, new_unique=None, old_unique=None):
        alter_unique=''
        if old_unique:
            alter_unique+=' DROP CONSTRAINT %s'%old_unique
        if new_unique:
            alter_unique+=' ADD CONSTRAINT un_%s_%s UNIQUE(%s)'%(col.table.sqlfullname.replace('.','_'), col.sqlname,col.sqlname)
        return 'ALTER TABLE %s %s' % (col.table.sqlfullname, alter_unique)
        
    def _buildForeignKey(self, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del, init_deferred):
        """Prepare the sql statement for adding the new constraint to the given table and return it"""
        c_name = 'fk_%s_%s' % (m_tbl, m_fld)
        statement = self.db.adapter.addForeignKeySql(c_name, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del,
                                                     init_deferred)
        return statement
        
    def _dropForeignKey(self, referencing_package, referencing_table, referencing_field, actual_name=None):
        """Prepare the sql statement for dropping the givent constraint from the given table and return it"""
        constraint_name = actual_name or 'fk_%s_%s' % (referencing_table, referencing_field)
        statement = 'ALTER TABLE %s.%s DROP CONSTRAINT %s' % (referencing_package, referencing_table, constraint_name)
        return statement
        
    def _sqlTable(self, tbl):
        """Return the sql statement string that creates the new table"""
        tablename = '%s.%s' % (tbl.sqlschema, tbl.sqlname)
        
        sqlfields = []
        for col in tbl.columns.values():
            sqlfields.append(self._sqlColumn(col))
        return 'CREATE TABLE %s (%s);' % (tablename, ', '.join(sqlfields))
        
    def _sqlDatabase(self, tbl):
        """Return the sql statement string that creates the new database"""
        return 'CREATE DATABASE "Dooo"  WITH ENCODING "UNICODE";'
        
    def _sqlTableIndexes(self, tbl):
        """Return the list of statements for building table's indexes"""
        tablename = tbl.sqlname
        sqlschema = tbl.sqlschema
        pkey = tbl.pkey
        sqlindexes = []
        bagindexes = Bag()
        if tbl.indexes:
            for idx in tbl.indexes.values():
                icols = idx.getAttr('columns')
                icols = ','.join([tbl.column(col.strip()).sqlname for col in icols.split(',')])
                unique = idx.getAttr('unique')
                change = self._buildIndex(tablename, idx.sqlname, icols, sqlschema=sqlschema, unique=unique, pkey=pkey)
                sqlindexes.append(change)
                bagindexes.setItem(idx.sqlname, None, changes=change)
        return (sqlindexes, bagindexes)
        
    def _buildIndex(self, tablename, iname, icols, unique=None, sqlschema=None, pkey=None):
        """Return the statement string for creating a table's index"""
        if icols != pkey:
            return self.db.adapter.createIndex(iname, columns=icols, table_sql=tablename, sqlschema=sqlschema,
                                               unique=unique)
                                               
    def _sqlColumn(self, col):
        """Return the statement string for creating a table's column"""
        return self.db.adapter.columnSqlDefinition(sqlname=col.sqlname,
                                                   dtype=col.dtype, size=col.getAttr('size'),
                                                   notnull=col.getAttr('notnull', False),
                                                   pkey=(col.name == col.table.pkey),unique=col.getAttr('unique'))

    def changeRelations(self,table,column,old_colname):
        tblobj = self.db.table(table)
        pkeyname = '%s.%s' %(table,tblobj.pkey)
        db = self.db
        for n in tblobj.relations:
            joiner = n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M' and joiner.get('one_relation') == pkeyname:
                fldlist = joiner['many_relation'].split('.')
                tblname = '.'.join(fldlist[0:2])
                if fldlist[2] == column:
                    try:
                        db.adapter.renameColumn(db.table(tblname).model.sqlfullname,old_colname,column)
                        print joiner['many_relation'],' fixed'
                        db.commit()
                    except Exception,e:
                        #print joiner['many_relation'],' error'
                        db.rollback()

                                                   
if __name__ == '__main__':
    db = GnrSqlDb(implementation='postgres', dbname='pforce',
                  host='localhost', user='postgres', password='postgres',
                  main_schema=None)
    db.importModelFromDb()
    db.saveModel('/Users/fporcari/Desktop/testmodel', 'py') 
