#!/usr/bin/python
# -*- coding: UTF-8 -*-

import py.test

from gnr.web.gnrwebstruct import GnrDomSrc, struct_method, StructMethodError

def  test_register_without_name_without_underscore():
    @struct_method
    def foo():
        pass

    assert GnrDomSrc._external_methods['foo'] == 'foo'

def  test_register_without_name_with_underscore():
    @struct_method
    def a_quuz():
        pass

    assert GnrDomSrc._external_methods['quuz'] == 'a_quuz'


def test_register_with_name():
    @struct_method('bar')
    def anotherFoo():
        pass

    assert GnrDomSrc._external_methods['bar'] == 'anotherFoo'


def test_valid_override_methods():
    @struct_method
    def foo1():
        pass

    @struct_method
    def foo1():
        pass

def test_invalid_override_methods():
    with py.test.raises(StructMethodError):
        @struct_method
        def foo1():
            pass

        @struct_method('foo1')
        def bar1():
            pass