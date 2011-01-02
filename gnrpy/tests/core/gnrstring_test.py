# -*- coding: UTF-8 -*-
from gnr.core import gnrstring
import datetime

import pytest

def test_getUntil():
    """docstring for test_getUntil"""
    assert gnrstring.getUntil('teststring', 'st') == 'te'
    assert gnrstring.getUntil('teststring', 'te') == ''
    assert gnrstring.getUntil('teststring', 'te') == ''

def test_getUntilLast():
    """docstring for test_getUntilLast"""
    assert gnrstring.getUntilLast('teststring', 'st') == 'test'
    assert gnrstring.getUntilLast('teststring', 'te') == ''
    assert gnrstring.getUntilLast('teststring', 'co') == ''

def test_getFrom():
    """docstring for test_getFrom"""
    assert gnrstring.getFrom('teststring', 'st') == 'string'
    assert gnrstring.getFrom('teststring', 'te') == 'ststring'
    assert gnrstring.getFrom('teststring', 'co') == ''

def test_getFromLast():
    """docstring for test_getFromLast"""
    assert gnrstring.getFromLast('teststring', 'st') == 'ring'
    assert gnrstring.getFromLast('teststring', 'ng') == ''
    assert gnrstring.getFromLast('teststring', 'co') == ''

def test_wordSplit():
    """docstring for test_wordSplit"""
    assert gnrstring.wordSplit('hello, my dear friend') == ['hello', 'my', 'dear', 'friend']

def splitLast():
    """docstring for splitLast"""
    assert gnrstring.splitLast('hello my dear friend', 'e') == ('hello my dear fri', 'nd')

def getBetween():
    """docstring for getBetween"""
    assert gnrstring.getBetween('teststring', 'st', 'in') == 'str'
    assert gnrstring.getBetween('teststring', 'st', 'te') == ''
    assert gnrstring.getBetween('teststring', 'te', 'te') == ''

def test_like():
    """docstring for test_like"""
    assert gnrstring.like('*dog*', 'adogert', '*')
    assert not gnrstring.like('dog*', 'adogert', '*')
    assert not gnrstring.like('*dog', '*adogert', '*')

def test_filter():
    """docstring for Test_filter"""
    txt = "hello my beautiful princess"
    assert gnrstring.filter(txt, '*my*', '', '*')
    assert not gnrstring.filter(txt, 'my*', '', '*')
    assert gnrstring.filter(txt, '$beauti$', '$cwp$', '$')
    assert gnrstring.filter(txt, include='*my*', wildcard='*')
    print not gnrstring.filter(txt, exclude='%princess')

def test_regexDelete():
    """docstring for test_regexDelete"""
    assert gnrstring.regexDelete("hello my beautiful princess", 'utiful') == "hello my bea princess"

def test_templateReplace():
    """docstring for test_templateReplace"""
    assert gnrstring.templateReplace('$foo loves $bar but she loves $aux and not $foo',
                                     {'foo': 'John', 'bar': 'Sandra',
                                      'aux': 'Steve'}) == 'John loves Sandra but she loves Steve and not John'

def test_asDict():
    """docstring for asDict"""
    d = gnrstring.asDict('height=22, weight=73')
    assert d['height'] == '22' and d['weight'] == '73' and isinstance(d, dict)
    d = gnrstring.asDict('height=$myheight, weight=73', symbols={'myheight': 55})
    assert d['height'] == '55' and d['weight'] == '73' and isinstance(d, dict)

def test_stringDict():
    """docstring for test_stringDict"""
    assert gnrstring.stringDict({'height': 22, 'width': 33}) == 'width=33,height=22'

def test_updateString():
    """docstring for test_updateString"""
    assert gnrstring.updateString('I drink cola', 'beer') == 'I drink cola,beer'
    assert gnrstring.updateString('I drink cola', 'beer', ' and ') == 'I drink cola and beer'

def test_makeSet():
    """docstring for test_makeSet"""
    assert  gnrstring.makeSet('a', 'b') == set(['a', 'b'])

def test_splitAndStrip():
    """docstring for test_splitAndStrip"""
    assert gnrstring.splitAndStrip('cola, beer, milk') == ['cola', 'beer', 'milk']
    assert gnrstring.splitAndStrip('cola, beer, milk', n=1) == ['cola', 'beer, milk']
    assert gnrstring.splitAndStrip('cola, beer, milk', fixed=1) == ['cola']
    assert gnrstring.splitAndStrip('cola, beer, milk', fixed=5) == ['cola', 'beer', 'milk', '', '']
    assert gnrstring.splitAndStrip('cola, beer, milk', fixed=-5) == ['', '', 'cola', 'beer', 'milk']
    assert gnrstring.splitAndStrip('cola, beer, milk', fixed=5, n=1) == ['cola', 'beer, milk', '', '', '']

def test_countOf():
    """docstring for test_countOf"""
    assert gnrstring.countOf('hello bello', 'lo') == 2

def test_split():
    """docstring for test_split"""
    assert gnrstring.split('here.you.are') == ['here', 'you', 'are']
    assert gnrstring.split('here/you/are', '/') == ['here', 'you', 'are']
    assert gnrstring.split('here/(you/are)/again', '/') == ['here', '(you/are)', 'again']
    with pytest.raises(ValueError):
        gnrstring.split('(Something is wrong/here', '/')

def test_smartjoin():
    """docstring for test_smartjoin"""
    assert gnrstring.smartjoin(['Hello, dog', 'you', 'are', 'yellow'], ',') == 'Hello\\, dog,you,are,yellow'

def test_smartsplit():
    """docstring for smartsplit"""
    assert gnrstring.smartsplit('Hello\\, dog,you,are,yellow', ',') == ['Hello, dog', 'you', 'are', 'yellow']

def test_fromIsoDate():
    """docstring for test_fromIsoDate"""
    assert isinstance(gnrstring.fromIsoDate('1983/01/29'), datetime.date)

def test_toJson():
    res = gnrstring.toJson([{'a': 2}, {'b': 3, 'c': 6}, {'z': 9}])
    assert res == '[{"a": 2}, {"c": 6, "b": 3}, {"z": 9}]'