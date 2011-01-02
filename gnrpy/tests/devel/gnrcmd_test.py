# -*- encoding: utf-8 -*-

import os, os.path
from gnr.devel.utils import AutoDiscovery, expandpath

def test_expandpath():
    home = os.environ['HOME']
    home_src = os.path.join(home, 'src')
    assert expandpath('~/src') == home_src
    assert expandpath('$HOME/src') == home_src
    assert expandpath('~/src/../bin') == os.path.join(home, 'src', '..', 'bin')
    assert expandpath('~/src/../bin', True) == os.path.join(home, 'bin')

class TestAutodiscovery(object):
    def setup_class(self):
        self.ad = AutoDiscovery()

    def test_all_packages(self):
        assert 'showcase' in self.ad.all_packages

    def test_all_sites(self):
        assert 'testgarden' in self.ad.all_sites

    def test_all_instances(self):
        assert 'testgarden' in self.ad.all_instances

    def test_all_projects(self):
        assert 'testgarden' in self.ad.all_projects