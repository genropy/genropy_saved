# -*- coding: UTF-8 -*-
# Genro  
# Copyright (c) 2004 Softwell sas - Milano see LICENSE for details
# Author Giovanni Porcari, Francesco Cavazzana, Saverio Porcari, Francesco Porcari
import unittest
import datetime
import os
from gnr.core.gnrbag import Bag

class TestBasicBag(unittest.TestCase):
    def setUp(self):
        self.bag = Bag()
        self.fullbag = Bag({'office': Bag({'John': Bag(), 'Frank': Bag(), 'Alexandra': Bag()}),
                            'friends': Bag({'Henry': Bag(), 'Fred': Bag()}),
                            'relatives': Bag({'Karla': Bag(), 'Albert': Bag()})})

    def testinit(self):
        """
        this test case check different kinds of bag's instantiation:
        - from a list of tuples
        - from a dictionary
        - empty bag
        """
        firstbag = Bag({'a': 1}) #bag from a dict
        secondbag = Bag([('a', 1)]) #bag from list of tuple
        thirdbag = Bag()
        thirdbag.setItem('a', 1)#empty bag filled
        bagstring = '0 - (int) a: 1  ' #bag as string
        self.failUnless(firstbag.asString() == secondbag.asString() == thirdbag.asString() == bagstring)

    def testsetgetItem(self):
        """
        this test case checks the methods setItem and getItem
        """
        self.bag.setItem('a.b.c', 5)
        self.failUnless(self.bag.getItem('a.b.c') == self.bag['a.b.c'] == 5)
        self.bag['a.b.c'] = 6
        self.failUnless(self.bag.getItem('a.b.c') == self.bag['a.b.c'] == 6)

    def testindexposition(self):
        """
        this test case checks the method index and the argument "_position"
        """
        self.bag['a.b.c'] = 6
        self.bag.addItem('a.b.d', 15)
        self.failUnless(self.bag.getItem('a.b.#1') == self.bag['a.b.d'] == 15)
        self.assertEqual(self.bag['a.b'].index('d'), 1)
        self.bag.setItem('a.b.middle', 10, _position='<d')
        self.assertEqual(self.bag['a.b'].index('middle'), 1)
        self.assertEqual(self.bag['a.b'].index('d'), 2)

    def testgetIndexList(self):
        il = self.fullbag.getIndexList()
        self.assertEqual(len(il), 10)

    def testkeysitemsvalues(self):
        """
        this test case checks the methods
        -keys
        -items
        -values
        """
        self.failUnless(self.fullbag['office'].keys() ==
                        self.fullbag['office?'] ==
                        ['Frank', 'John', 'Alexandra'])
        self.failUnless(len(self.fullbag['office'].keys()) ==
                        len(self.fullbag['office'].values()) ==
                        len(self.fullbag['office'].items()) == 3)
        self.assertTrue(self.fullbag['office'].has_key('John'))

    def testpopin(self):
        """
        this test case checks the method pop and the clause "in"
        """
        self.assertTrue('John' in self.fullbag['office'])
        self.fullbag['office.Desmond'] = Bag()
        d = self.fullbag['office.Desmond']
        removed = self.fullbag['office'].pop('#3')
        self.assertEqual(d, removed)
        self.assertEqual(self.fullbag['office'].keys(), ['Frank', 'John', 'Alexandra'])

    def testasDict(self):
        """
        this test case checks the method asDict
        """
        d = self.fullbag['office'].asDict()
        self.assertTrue(isinstance(d, dict))
        self.assertEqual(d.keys(), self.fullbag['office?'])

class TestAttributeBag(unittest.TestCase):
    def setUp(self):
        self.fullbag = Bag({'office': Bag({'John': Bag(), 'Frank': Bag(), 'Alexandra': Bag()}),
                            'friends': Bag({'Henry': Bag(), 'Fred': Bag()}),
                            'relatives': Bag({'Karla': Bag(), 'Albert': Bag()})})
        self.fullbag['office'].setItem('Xavier', Bag(), fromdate='9-15-2005', role='researcher')
        self.fullbag['office'].setAttr('Frank', fromdate='3-5-1998', role='developer')
        self.fullbag['office'].setAttr('John', fromdate='2-1-1990', role='boss', age=55)

    def testattributes(self):
        self.assertEqual(self.fullbag['office'].getAttr('Xavier', 'role'), 'researcher')
        self.assertEqual(self.fullbag['office.Frank?a:role'], 'developer')
        l = [('Frank', 'developer'), ('John', 'boss'), ('Alexandra', None), ('Xavier', 'researcher')]
        self.failUnless(self.fullbag['office'].digest('#k,#a.role') ==
                        self.fullbag['office.?d:#k,#a.role'] == l)
        self.failUnless(self.fullbag['office.Xavier'] ==
                        self.fullbag['office.#3'] ==
                        self.fullbag['office.#role=researcher'])

    def testBagNodes(self):
        self.fullbag.delAttr('office.John', 'age')
        n = self.fullbag.getNode('office.John')
        self.assertTrue(n.hasAttr('role'))
        self.assertFalse(n.hasAttr('age'))
        self.assertEqual(n, self.fullbag.getNodeByAttr('role', 'boss'))

    def testgetNodeByAttr(self):
        researcher = self.fullbag.getNodeByAttr('role', 'researcher')
        self.assertEqual(researcher, self.fullbag.getNode('office.Xavier'))

    def testfromToXml(self):
        self.fullbag['relatives.Karla.birthday'] = datetime.date(1952, 12, 10)
        self.fullbag['relatives.Karla.pierciengs'] = 0
        self.fullbag['relatives.Karla.dogname'] = ''
        self.fullbag.setAttr('relatives.Karla', age=54)
        self.fullbag.toXml('mybag.xml')
        x = self.fullbag['relatives'].toXml()
        b = Bag(x)
        self.assertEqual(b.asString(), self.fullbag['relatives'].asString())

    def testsfromSource(self):
        current = os.getcwd()
        fromlocal_std = Bag('%s/test_files/standardxml.xml' % current)
        self.assertTrue(isinstance(fromlocal_std, Bag))
        #non riesce a printarla per carattere non encodabile
        fromlocal_bag = Bag('%s/test_files/mybag.xml' % current)
        self.assertTrue(isinstance(fromlocal_bag, Bag))
        #uncomment the following test if you are online
        #fromurl=Bag('http://www.plone.org')
        #self.assertTrue(isinstance(fromurl, Bag))
        stringxml = '<?xml version="1.02" encoding="UTF-8"?><a><b name="fuffy"><d>dog</d></b><c/></a>'
        fromstringxml = Bag(stringxml)
        self.assertTrue(isinstance(fromstringxml, Bag))
        fromdirectory = Bag('%s/test_files' % current)
        self.assertTrue(isinstance(fromdirectory, Bag))

    def testmerge(self):
        newbag = Bag()
        newbag.setItem('Henry', self.fullbag['friends.Henry'], role='documentation and tests')
        newbag.setItem('Xavier', 'Mr Xavier', role='documentation manager', age=26)
        allflagstrue = self.fullbag['office'].merge(newbag)#all flags true
        allflagsfalse = self.fullbag['office'].merge(newbag, upd_values=False, add_values=False, upd_attr=False,
                                                     add_attr=False)
        self.assertEqual(allflagsfalse.asString(), self.fullbag['office'].asString())
        notupdatevalues = self.fullbag['office'].merge(newbag, upd_values=False)
        self.assertTrue(isinstance(self.fullbag['office.Xavier'], Bag))
        notaddvalues = self.fullbag['office'].merge(newbag, add_values=False)
        self.assertEqual(len(self.fullbag['office'].items()), len(notaddvalues.items()))
        notupdateattrs = self.fullbag['office'].merge(newbag, upd_attr=False)
        self.assertEqual(self.fullbag['office.Xavier?a:role'], notupdateattrs['Xavier?a:role'])
        notaddattrs = self.fullbag['office'].merge(newbag, add_attr=False)
        self.assertFalse(notaddattrs.getAttr('Xavier', 'age', default=False))

    def testsum(self):
        numbers = Bag()
        numbers.setItem('first', 20, height=22)
        numbers.setItem('second', 30, height=342)
        self.assertEqual(numbers.sum('#v,#a.height'), [50, 364])

class TestAdvancedBag(unittest.TestCase):
    def setUp(self):
        self.bag = Bag()
        self.bag.setBackRef()
        self.bag['a.b.c.d'] = 4
        self.bag['a.b.e'] = 5

    def testparent(self):
        self.assertEqual(self.bag['a.b.c'].parent, self.bag['a.b'])
        c = self.bag['a.b.c']
        self.assertEqual(c['../e'], 5)
        self.bag['a.b'].delParentRef()
        self.assertFalse(self.bag['a.b'].backref)

    def testformula(self):
        self.bag['product'] = self.bag.formula('$x*$y', x='a.b.c.d', y='a.b.e')
        self.assertEqual(self.bag['product'], self.bag['a.b.c.d'] * self.bag['a.b.e'])

        self.bag.defineFormula(calculate_perimeter='2*($base + $height)')
        self.bag.defineSymbol(base='a.b.c.d', height='a.b.e')
        self.bag['perimeter'] = self.bag.formula('calculate_perimeter')
        self.assertEqual(self.bag['perimeter'], 18)

    def testcallbackitem(self):
        def hello():
            return 'Hello!'

        self.bag.setCallBackItem('say_hello', hello)
        self.assertEqual(self.bag['say_hello'], hello())

    def testnodetrigger(self):
        self.lastupdates = []

        def mycallback(node, info=None, evt=None):
            self.lastupdates.append((node.getLabel(), info, node.getValue()))

        self.bag.getNode('a.b.c.d').subscribe('lastupdates', mycallback)
        self.bag['a.b.c.d'] = 20
        self.assertEqual(self.lastupdates[-1], ('d', 4, 20))

    def testbagtriggers(self):
        self.log = []

        def log_upd(node, pathlist, oldvalue, evt):
            self.log.append(('.'.join(pathlist), node.getValue(), oldvalue, evt))

        def log_ins(node, pathlist, ind, evt):
            self.log.append(('.'.join(pathlist), node.getValue(), ind, evt))

        def log_del(node, pathlist, ind, evt):
            self.log.append(('.'.join(pathlist), node.getValue(), ind, evt))

        self.bag.subscribe('log', update=log_upd, insert=log_ins, delete=log_del)
        self.bag['a.b.t'] = 45
        self.assertEqual(self.log[-1], ('a.b', 45, 2, 'ins'))
        self.bag['a.b.t'] = 56
        self.assertEqual(self.log[-1], ('a.b.t', 56, 45, 'upd_value'))
        self.bag.delItem('a.b.t')
        self.assertEqual(self.log[-1], ('a.b', 56, 2, 'del'))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicBag)
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAttributeBag))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAdvancedBag))
    unittest.TextTestRunner(verbosity=2).run(suite)