import itertools

from gnr.core.gnrbag import Bag

class AnalyzingBag(Bag):
    def analyze(self, data, group_by=None, sum=None, collect=None,
                keep=None, distinct=None, key=None, captionCb=None):
        """comment analyze"""
        def groupLabel(row,group):
            if isinstance(group, basestring):
                if group.startswith('*'):
                    label = group[1:]
                else:
                    label = row[group]
            else:
                label = group(row)
            if not isinstance(label, basestring):
                label = str(label)
            return label
                
        def updateTotals(bagnode, k, row):
            attr = bagnode.getAttr()
            idx = attr.setdefault('idx', set())
            idx.add(k)
            if sum is not None:
                for fld in sum:
                    lbl = 'sum_%s' % fld 
                    attr[lbl] = attr.get(lbl, 0) + (row.get(fld,0) or 0)
            if collect is not None:
                for fld in collect:
                    lbl = 'collect_%s' % fld
                    l= attr.get(lbl,[])
                    l.append(row[fld])
                    attr[lbl]=l
            if distinct is not None:
                for fld in distinct:
                    fldset = attr.setdefault('dist_%s' % fld, set())
                    fldset.add(row[fld])
                    
            if keep is not None:
                for fld in keep:
                    lbl='k_%s' % fld
                    value=attr.get(lbl, None)
                    if not value:
                        attr[lbl]=row[fld]
                    

        counter=itertools.count()
        for row in data:
            rowind = counter.next()
            currbag = self
            for gr in group_by:
                label = groupLabel(row, gr) or '_'
                bagnode = currbag.getNode(label, autocreate=True)
                if bagnode.value is None:
                    bagnode.setAttr(_pkey=self.nodeCounter)
                    bagnode.value = Bag()
                currbag = bagnode.value
                if key is None:
                    k = rowind
                else:
                    k = row[key]
                updateTotals(bagnode, k, row)
                if captionCb:
                    bagnode.setAttr(caption = captionCb(gr, row, bagnode))
                
    def _get_nodeCounter(self):
        if not hasattr(self, '_nodeCounter'):
            self._nodeCounter = 0
        self._nodeCounter += 1
        return self._nodeCounter
    nodeCounter = property(_get_nodeCounter)
    
        