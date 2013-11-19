#import itertools
from gnr.core.gnrbag import Bag

class AnalyzingBag(Bag):
    def analyze(self, data, group_by=None, sum=None, collect=None,
                keep=None, distinct=None, key=None, captionCb=None, collectIdx=True):
        """comment analyze"""
        totalize = sum

        def groupLabel(row, group):
            if isinstance(group, basestring):
                if group.startswith('*'):
                    label = group[1:]
                else:
                    label = row[group]
            else:
                label = group(row)
            if label is None:
                return ''
            if not isinstance(label, basestring):
                label = str(label)
            return label

        def updateTotals(bagnode, k, row):
            attr = bagnode.getAttr()
            if collectIdx:
                idx = attr.setdefault('idx', set())
                idx.add(k)
                attr['count'] = len(idx)
            else:
                if not 'count' in attr:
                    attr['count'] = 0
                attr['count'] += 1
            if totalize is not None:
                for fld in totalize:
                    lbl = 'sum_%s' % fld
                    tt = attr[lbl] = attr.get(lbl, 0) + (row.get(fld, 0) or 0)
                    lbl = 'avg_%s' % fld
                    attr[lbl] = float(tt / attr['count'])
            if collect is not None:
                for fld in collect:
                    lbl = 'collect_%s' % fld
                    l = attr.get(lbl, [])
                    l.append(row[fld])
                    attr[lbl] = l
            if distinct is not None:
                for fld in distinct:
                    fldset = attr.setdefault('dist_%s' % fld, set())
                    fldset.add(row[fld])
                    attr['count_%s' % fld] = len(fldset)

            if keep is not None:
                for fld in keep:
                    lbl = 'k_%s' % fld
                    value = attr.get(lbl, None)
                    if not value:
                        attr[lbl] = row[fld]

        #counter = itertools.count()
        for rowind, row in enumerate(data):
            #rowind = counter.next()
            #rowind += 1
            currbag = self
            for gr in group_by:
                label = groupLabel(row, gr)
                label = label.replace('.', '_') or '_'
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
                    bagnode.setAttr(caption=captionCb(gr, row, bagnode))
                else:
                    bagnode.setAttr(caption=label)

    def _get_nodeCounter(self):
        if not hasattr(self, '_nodeCounter'):
            self._nodeCounter = 0
        self._nodeCounter += 1
        return self._nodeCounter

    nodeCounter = property(_get_nodeCounter)