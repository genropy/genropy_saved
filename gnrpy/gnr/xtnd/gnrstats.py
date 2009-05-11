from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import toText

class TotalizeSelection(object):
    def fillFilter(self, params, dpath, fltquery, keyfield='_pkey'):
        """Utility per ricevere una lista di pkey da una grid e aggiungere condizioni
           di filtro solo se ci sono pkey nella bag"""
        parlist=None
        if params[dpath]:
            parlist = params[dpath].digest('#a.%s' % keyfield)
        if parlist:
            fltquery = 'AND %s' % fltquery
        else:
            fltquery = ''
        return parlist, fltquery
        
    def setParameters(self, db, mainTable, relationDict, columns, where, queryArgs, 
                      fields, anagfields, sortfields, grcol, colgroups, subtotals, 
                      total_col=True, nfetch = 1000):
        self.db = db
        
        self.mainTable = mainTable
        self.relationDict = relationDict
        self.columns = columns
        self.where = where
        self.queryArgs = queryArgs
        
        self.grcol = grcol
        
        self.colgroups = {}
        for i,v in enumerate(colgroups):
            if not isinstance(v, tuple) and not isinstance(v, list):
                v = (v, )
            self.colgroups['C%i' % i] = v
        if total_col:
            self.colgroups['TT'] = '*tot*'
        
        self.fields = fields
        self.subtotals = tuple(['result'] + list(subtotals or []))
        self.anagfields = tuple(anagfields or [])
        self.sortfields = sortfields
        self.nfetch = nfetch or 1000
        
        self.data = None
        self.dataprev = None
        self.rtot = 0
        
    def calculate(self, prevperiod=False):
        serverfetch = self.getRowCursor()
        self.rowsTotalize(serverfetch, prevperiod=prevperiod)
        
        result = []
        for pathlist, node in self.data.getIndex(): # ritorna data corrente anche se calcolo prevperiod, 
            d = dict(node.getAttr())                # perche' modificato con le righe solo anno scorso
            d['pathlist'] = pathlist
            result.append(d)
        result.sort(key=lambda v: v.get('_sort_'))
        return result
        
    def getRowCursor(self):
        tblobj = self.db.table(self.mainTable)
        sel = tblobj.query(columns = self.columns, 
                                 where = self.where,
                                 relationDict = self.relationDict,
                                 **self.queryArgs)
        return sel.serverfetch(self.nfetch)[1]
    
    def rowsTotalize(self, serverfetch, prevperiod=False):
        if prevperiod:
            self.dataprev = Bag()
        else:
            self.data = Bag()
        self.rtot = 0
        for rows in serverfetch:
            self.rtot = self.rtot + len(rows)
            for r in rows:
                self.rowPreprocess(r)
                self.readRow(r, prevperiod=prevperiod)
                
    def rowPreprocess(self, r):
        pass
    
    def getOneBlock(self, row, grouplist, prevperiod=False):
        if prevperiod:
            data = self.dataprev
        else:
            data = self.data
        path = '.'.join([grouplist[0]]+[toText(row[x]).replace('.','_') for x in grouplist[1:]])
        result = data.getNode(path)
        if result is None:
            data.setItem(path, None)
            if prevperiod:
                self.data.setItem(path, None) # if a path is only in prev period put in in current also
            result = data.getNode(path)
        return result
    
    def sortKey(self, row, grouplist):
        return '_'.join([toText(row[x]).replace('.','_') for x in grouplist[1:]])

    def readRow(self, row, prevperiod=False):
        for colnum, grprods in self.colgroups.items():
            if (grprods=='*tot*') or (row[self.grcol] in grprods):
                blocknode = self.getOneBlock(row, self.subtotals, prevperiod=prevperiod)
                blockAttr = blocknode.getAttr()
                if not blockAttr and self.anagfields:
                    self.getAnagFields(row, blockAttr)
                    blockAttr['_sort_'] = self.sortKey(row, self.subtotals[:-1])+'_'.join([toText(blockAttr[k]) for k in self.sortfields])
                    
                    if prevperiod: # aggiungo una riga al precedente e, se manca, anche al corrente
                        newblockAttr = self.getOneBlock(row, self.subtotals, prevperiod=False).getAttr()
                        if not newblockAttr:
                            newblockAttr.update(blockAttr)
                    
                    grouplist = []
                    for i,gr in enumerate(self.subtotals[:-1]):
                        grouplist.append(gr)
                        grAttr = self.getOneBlock(row, grouplist, prevperiod=prevperiod).getAttr()
                        grAttr['_sort_'] = self.sortKey(row, grouplist) + '_zzzzzzzzzzzzzzzzzzzz'
                        grAttr['_subtot_'] = 'subtot_%i' % i
                        
                        grAttr.update(dict([(x, row[x]) for x in grouplist[1:]]))
                        if prevperiod:
                            newgrAttr = self.getOneBlock(row, grouplist, prevperiod=False).getAttr()
                            if not newgrAttr:
                                newgrAttr.update(grAttr)
                            
                values = self.getRowValues(row, colnum, blockAttr)
                
                grouplist = []
                for i,gr in enumerate(self.subtotals):
                    grouplist.append(gr)
                    blocknode = self.getOneBlock(row, grouplist, prevperiod=prevperiod)
                    blockAttr = blocknode.getAttr()
                    #if (i < (len(self.subtotals)-1)):
                    #    blockAttr['_subtot_'] = 'subtot_%i' % i
                    self.addToGroup(values, colnum, blockAttr)
            
    
    def getAnagFields(self, row, totals):
        for f in self.anagfields:
            getattr(self, 'anag_'+f, self.anag_base)(row, totals, f)
            
    def anag_base(self, row, totals, fld):
        totals[fld] = row[fld]
        
    def getRowValues(self, row, colnum, totals):
        rowValues = dict(row)
        for f in self.fields:
            h = getattr(self, 'fld_'+f, None)
            if h:
                rowValues[f] = h(row, totals, colnum, rowValues) or 0
            else:
                rowValues[f] = row[f] or 0
        return rowValues
    
    def addToGroup(self, values, colnum, totals):
        for f in self.fields:
            path = '%s_%s' % (colnum, f)
            h = getattr(self, 'tot_'+f, None)
            if h:
                h(values, totals, colnum, path)
            else:
                totals[path] = totals.get(path, 0) + (values[f] or 0)
                
